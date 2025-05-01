"""
This module defines abstract base classes for web scraping components:
LinkScraper, SpecsScraper, and Storage. These ABCs outline the
interfaces for scraping links from a website, extracting specifications
from web pages, and storing the scraped data, respectively.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Set

class LinkScraper(ABC):
    """
    Abstract base class for link scrapers.

    Subclasses should implement the `scrape_links` method to extract
    URLs from a target website.
    """
    @abstractmethod
    def scrape_links(self) -> Set[str]:
        """
        Abstract method to scrape links.

        Returns:
            Set[str]: A set of unique URLs found on the target website.
        """
        pass

class SpecsScraper(ABC):
    """
    Abstract base class for specifications scrapers.

    Subclasses should implement the `scrape_specs` method to extract
    structured data (specifications) from a list of URLs.
    """
    @abstractmethod
    def scrape_specs(self, urls: List[str]) -> List[Dict]:
        """
        Abstract method to scrape specifications from a list of URLs.

        Args:
            urls (List[str]): A list of URLs to scrape.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary
                       contains the scraped specifications from a single URL.
        """
        pass

class Storage(ABC):
    """
    Abstract base class for data storage.

    Subclasses should implement the `save` method to persist the scraped data.
    """
    @abstractmethod
    def save(self, data: List[Dict]) -> None:
        """
        Abstract method to save scraped data.

        Args:
            data (List[Dict]): A list of dictionaries containing the scraped data.

        Returns:
            None
        """
        pass
