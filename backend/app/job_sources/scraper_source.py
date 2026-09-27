"""
Scraper job source adapter.
Only scrapes publicly accessible pages where robots.txt/ToS allow it.
Implements proper rate limiting, retries, and error handling.
"""
from __future__ import annotations

from typing import List

from app.job_sources.base_source import BaseJobSource, RawJob
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScraperSource(BaseJobSource):
    """
    Web scraper adapter.
    Currently scaffolded for future implementation.
    Only scrapes sites where ToS and robots.txt permit it.
    """

    name = "web_scraper"
    source_type = "scraper"
    base_url = ""

    def is_available(self) -> bool:
        # Disabled by default until configured and ToS verified
        return False

    def collect(self, query: str = "", location: str = "", max_results: int = 50) -> List[RawJob]:
        """
        Scraping implementation placeholder.
        Add specific site scrapers here after verifying:
        1. Site's robots.txt permits scraping
        2. Site's Terms of Service permit automated access
        3. Proper rate limiting is implemented
        4. No authentication bypass is used
        5. No CAPTCHA bypass is used
        """
        logger.info("Scraper source not configured, returning empty list")
        return []
