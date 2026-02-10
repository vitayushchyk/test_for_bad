import logging
from typing import Iterable

import networkx as nx


class GraphBuilder:
    def __init__(self, logger: logging.Logger, overlap: int = 2) -> None:
        self._log = logger
        self._overlap = overlap

    def build(self, fragments: Iterable[str]) -> nx.DiGraph:
        fragments_list = list(fragments)
        self._log.debug(
            "Building graph for %d fragments (overlap=%d)",
            len(fragments_list),
            self._overlap,
        )

        graph = nx.DiGraph()
        prefix_map: dict[str, list[str]] = {}

        for fragment in fragments_list:
            prefix = fragment[: self._overlap]
            prefix_map.setdefault(prefix, []).append(fragment)

        for fragment in fragments_list:
            suffix = fragment[-self._overlap :]
            for next_fragment in prefix_map.get(suffix, []):
                if fragment != next_fragment:
                    graph.add_edge(fragment, next_fragment)
        self._log.debug(
            "Graph built: %d nodes, %d edges",
            graph.number_of_nodes(),
            graph.number_of_edges(),
        )
        return graph
