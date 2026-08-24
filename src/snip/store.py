"""In-memory storage. Not persistent — fine for a workshop starter."""

from dataclasses import dataclass, field


@dataclass
class LinkRecord:
    code: str
    url: str
    clicks: int = 0


@dataclass
class Store:
    _links: dict = field(default_factory=dict)

    def put(self, record: LinkRecord) -> None:
        self._links[record.code] = record

    def get(self, code: str) -> LinkRecord:
        return self._links[code]

    def exists(self, code: str) -> bool:
        return code in self._links

    def all(self) -> list:
        return list(self._links.values())


store = Store()
