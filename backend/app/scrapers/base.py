from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class RawJob:
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    posted_date: date | None = None
    salary_range: str | None = None
    is_remote: bool = False


class BaseScraper(ABC):
    @abstractmethod
    async def fetch_jobs(self, titles: list[str], locations: list[str]) -> list[RawJob]:
        ...
