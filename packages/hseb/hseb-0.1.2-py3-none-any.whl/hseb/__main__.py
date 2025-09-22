import argparse
import time
from hseb.core.submission import ExperimentMetrics, Submission
from hseb.engine.base import EngineBase
from hseb.core.config import Config
from hseb.core.dataset import BenchmarkDataset
from hseb.core.measurement import ExperimentResult, QueryResult
from tqdm import tqdm
from structlog import get_logger
import tempfile
import random

logger = get_logger()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        required=True,
        type=str,
        help="path to a config file",
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="output file name",
    )
    parser.add_argument(
        "--cleanup",
        type=bool,
        required=False,
        default=True,
        help="should we delete all stopped containers? this saves disk space, but you lose engine logs",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        required=False,
        default=1000,
        help="number of random queries to warmup the engine",
    )
    parser.add_argument(
        "--queries",
        type=int,
        required=False,
        help="number of queries to sample for benchmark",
    )
    parser.add_argument(
        "--index-wait-seconds",
        type=int,
        required=False,
        default=300,
        help="how long should we wait for an index to become green",
    )

    args = parser.parse_args()

    config = Config.from_file(args.config)
    data = BenchmarkDataset(config.dataset)
    engine = EngineBase.load_class(config.engine, config)
    with tempfile.TemporaryDirectory(prefix="hseb_", delete=args.cleanup) as workdir:
        logger.info(f"Initialized engine, workdir: {workdir}")
        run_index = 0
        index_fails = 0
        search_fails = 0
        search_request_fails = 0
        for exp_index, exp in enumerate(config.experiments):
            index_variations = exp.index.expand()
            search_variations = exp.search.expand()
            total_cases = len(index_variations) * len(search_variations)
            logger.info(
                f"Running experiment {exp_index + 1} of {len(config.experiments)}. Targets: index={len(index_variations)} search={len(search_variations)} total={total_cases}"
            )

            for indexing_args_index, index_args in enumerate(index_variations):
                logger.info(f"Indexing run {indexing_args_index + 1}/{len(index_variations)}: {index_args}")
                try:
                    engine.start(index_args)
                    batches = data.corpus_batched(index_args.batch_size)
                    total = int(len(data.corpus_dataset) / index_args.batch_size)
                    index_start = time.perf_counter()
                    index_batch_times: list[float] = []
                    for batch in tqdm(batches, total=total, desc="indexing"):
                        index_response = engine.index_batch(batch=batch)
                        index_batch_times.append(index_response.client_latency)

                    commit_start = time.perf_counter()
                    engine.commit()
                    poll_green_attempts = 0
                    is_green = False
                    while not is_green and poll_green_attempts < args.index_wait_seconds:
                        is_green = engine.index_is_green()
                        poll_green_attempts += 1
                        if not is_green:
                            time.sleep(1)
                    if not is_green:
                        raise Exception(f"Index stuck in non-green status for {args.index_wait_seconds} seconds")
                    try:
                        warmup_start = time.perf_counter()
                        logger.info(
                            f"Index built in {warmup_start - index_start} seconds (ingest={int(commit_start - index_start)} commit={int(warmup_start - commit_start)})"
                        )
                        warmup_latencies: list[float] = []
                        for warmup_query in tqdm(
                            random.choices(list(data.queries(limit=1000)), k=args.warmup), desc="warmup"
                        ):
                            k_eff = min(exp.k, search_variations[0].ef_search)
                            response = engine.search(search_variations[0], warmup_query, k_eff)
                            warmup_latencies.append(response.client_latency)

                        logger.info(f"Warmup done in {time.perf_counter() - warmup_start} seconds")
                        for search_args_index, search_args in enumerate(search_variations):
                            logger.info(
                                f"Search {search_args_index + 1}/{len(search_variations)} ({run_index + 1}/{total_cases}): {search_args}"
                            )

                            measurements: list[QueryResult] = []
                            k_eff = min(exp.k, search_args.ef_search)
                            incomplete_results: list[int] = []
                            failed_queries = 0
                            for query in tqdm(list(data.queries(limit=args.queries)), desc="search"):
                                try:
                                    response = engine.search(search_args, query, k_eff)
                                    if len(response.results) != k_eff:
                                        incomplete_results.append(len(response.results))
                                    measurements.append(
                                        QueryResult.from_response(
                                            query=query, search_args=search_args, response=response
                                        )
                                    )
                                except Exception as error:
                                    logger.exception(f"got search request error {error}")
                                    failed_queries += 1
                                    search_request_fails += 1

                            result = ExperimentResult(
                                tag=exp.tag,
                                index_args=index_args,
                                search_args=search_args,
                                queries=measurements,
                                indexing_time=index_batch_times,
                                warmup_latencies=warmup_latencies,
                            )
                            result.to_json(workdir=workdir)
                            metrics = ExperimentMetrics.from_experiment(result)
                            if len(incomplete_results) > 0:
                                logger.warning(
                                    f"Engine returned {len(incomplete_results)}/{len(measurements)} incomplete results (expected {k_eff}): {incomplete_results}"
                                )
                            if failed_queries > 0:
                                logger.warning(f"Engine got {failed_queries} queries with errors")
                            logger.info(f"Run finished: {metrics.metrics.as_string()}")
                            run_index += 1
                    except Exception as error:
                        logger.exception(f"skipping search run {search_args}: {error}")
                        search_fails += 1
                    logger.debug(
                        f"Indexing run {indexing_args_index + 1}/{len(index_variations)} done in {time.perf_counter() - index_start} seconds"
                    )
                except Exception as error:
                    logger.exception(f"skipping index run {index_args}: {error}")
                    index_fails += 1
                finally:
                    engine.stop(args.cleanup)
        submission = Submission.from_dir(config=config, path=workdir)
        logger.info(f"Writing submission file to {args.out}")
        submission.to_json(args.out)
        logger.info(
            f"Experiment finished. {index_fails} index fails, {search_fails} search fails ({search_request_fails} failed requests)."
        )
