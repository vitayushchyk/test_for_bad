import logging
import time
from contextlib import contextmanager

from chain_finder import CpSatChainFinder
from graph_builder import GraphBuilder
from logger import LoggerConfigurator
from reader import Reader

logger = LoggerConfigurator.setup_logger(
    __name__,
    logging.DEBUG,
)


@contextmanager
def timer(log: logging.Logger, label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        log.info("[TIME] %s: %.4f s", label, time.perf_counter() - start)


def solve(
    filename: str, *, overlap: int = 2, time_limit_sec: float = 30.0, workers: int = 8
) -> None:
    reader = Reader(logger.getChild("reader"))
    builder = GraphBuilder(logger.getChild("graph"), overlap=overlap)
    finder = CpSatChainFinder(
        logger.getChild("cp_sat"),
        time_limit_sec=time_limit_sec,
        workers=workers,
        overlap=overlap,
    )

    with timer(logger, "Read input"):
        fragments = reader.read(filename)

    with timer(logger, "Build graph"):
        graph = builder.build(fragments)

    with timer(logger, "Solve with CP-SAT"):
        solution = finder.find(graph)

    logger.info("Longest digit sequence:\n%s", solution.combined)
    logger.debug("Fragment chain:\n%s", " -> ".join(solution.path))


if __name__ == "__main__":
    solve("source.txt")
