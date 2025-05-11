from abc import ABC, abstractmethod
from typing import Any

class AbstractScraper(ABC):
    """Abstract base class for all scrapers."""
    
    @abstractmethod
    def scrape(self) -> Any:
        """Perform the scraping operation."""
        pass