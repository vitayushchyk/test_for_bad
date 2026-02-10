import logging


class Reader:
    def __init__(self, logger: logging.Logger) -> None:
        self._log = logger

    def _clean_fragment(self, line: str) -> str | None:
        fragment = line.strip()
        return fragment or None

    def read(self, filename: str) -> list[str]:
        with open(filename, "r", encoding="utf-8") as f:
            fragments = [
                fragment
                for line in f
                if (fragment := self._clean_fragment(line)) is not None
            ]
        return fragments
