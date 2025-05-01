from abc import ABC, abstractmethod
from typing import List, Dict, Set

class LinkScraper(ABC):
    @abstractmethod
    def scrape_links(self) -> Set[str]:
        pass

class SpecsScraper(ABC):
    @abstractmethod
    def scrape_specs(self, urls: List[str]) -> List[Dict]:
        pass

class Storage(ABC):
    @abstractmethod
    def save(self, data: List[Dict]) -> None:
        pass
