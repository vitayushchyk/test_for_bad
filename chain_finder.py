import logging
from dataclasses import dataclass

import networkx as nx
from ortools.sat.python import cp_model


@dataclass(frozen=True)
class ChainSolution:
    path: list[str]
    combined: str


class CpSatChainFinder:
    """
     Finds the longest possible chain in a directed graph, where each node
    can be used at most once. Uses CP-SAT solver."""

    def __init__(
        self,
        logger: logging.Logger,
        time_limit_sec: float = 30.0,
        workers: int = 8,
        overlap: int = 2,
    ) -> None:
        self._log = logger
        self._time_limit_sec = time_limit_sec
        self._workers = workers
        self._overlap = overlap

    @staticmethod
    def _add_arc(
        model: cp_model.CpModel,
        arcs: list[list[int | cp_model.IntVar]],
        u: int,
        v: int,
    ) -> cp_model.IntVar:
        lit = model.new_bool_var(f"a_{u}_{v}")
        arcs.append([u, v, lit])
        return lit

    def find(self, graph: nx.DiGraph) -> ChainSolution:
        nodes = list(graph.nodes())
        num_nodes = len(nodes)
        if num_nodes == 0:
            return ChainSolution(path=[], combined="")

        idx = {v: i for i, v in enumerate(nodes)}
        dummy = num_nodes

        model = cp_model.CpModel()

        arcs: list[list[int | cp_model.IntVar]] = []

        self._log.debug("Finding chain in graph with %d nodes", num_nodes)

        for i in range(num_nodes):
            self._add_arc(model, arcs, i, i)
        self._add_arc(model, arcs, dummy, dummy)

        for u, v in graph.edges():
            self._add_arc(model, arcs, idx[u], idx[v])

        for i in range(num_nodes):
            self._add_arc(model, arcs, dummy, i)
            self._add_arc(model, arcs, i, dummy)

        model.add_circuit(arcs)

        used = []
        for i in range(num_nodes):
            self_loop_lit = next(lit for (a, b, lit) in arcs if a == i and b == i)
            ui = model.new_bool_var(f"used_{i}")
            model.add(ui + self_loop_lit == 1)
            used.append(ui)

        model.maximize(sum(used))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self._time_limit_sec
        solver.parameters.num_search_workers = self._workers

        self._log.info(
            "CP-SAT solving (time_limit=%.1fs, workers=%d)...",
            self._time_limit_sec,
            self._workers,
        )
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError("CP-SAT failed to find a solution.")

        self._log.info(
            "CP-SAT status: %s | objective=%s",
            solver.status_name(status),
            solver.objective_value,
        )

        succ: dict[int, int] = {}
        for u, v, lit in arcs:
            if solver.value(lit) == 1:
                succ[int(u)] = int(v)

        path_idx: list[int] = []
        cur = succ[dummy]
        while cur != dummy:
            path_idx.append(cur)
            cur = succ[cur]

        path = [nodes[i] for i in path_idx]
        combined = self._combine(path)
        return ChainSolution(path=path, combined=combined)

    def _combine(self, path: list[str]) -> str:
        if not path:
            return ""
        result = path[0]
        for fragment in path[1:]:
            result += fragment[self._overlap :]
        return result
