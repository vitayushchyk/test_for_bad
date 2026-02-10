import logging

from chain_finder import CpSatChainFinder
from graph_builder import GraphBuilder
from logger import LoggerConfigurator
from reader import Reader

logger = LoggerConfigurator.setup_logger(
    __name__,
    logging.INFO,
)


def solve(filename: str, *, overlap: int = 2, workers: int = 8) -> None:
    reader = Reader(logger.getChild("reader"))
    builder = GraphBuilder(logger.getChild("graph"), overlap=overlap)
    finder = CpSatChainFinder(
        logger.getChild("cp_sat"),
        workers=workers,
        overlap=overlap,
    )

    fragments = reader.read(filename)
    graph = builder.build(fragments)
    solution = finder.find(graph)

    logger.debug("Longest digit sequence length: %d", len(solution.combined))
    logger.info("Longest digit sequence:\n%s", solution.combined)
    logger.debug("Fragment chain:\n%s", " -> ".join(solution.path))


if __name__ == "__main__":
    solve("source.txt")
