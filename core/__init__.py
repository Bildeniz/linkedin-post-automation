"""Core modules for LinkedIn Automator."""

from .styles import (
    PromptStyle,
    HikayeStyle,
    HaberciStyle,
    MeraklandiricaStyle,
    KisaOzStyle,
    AkademikStyle,
    MaddelerStyle,
    KarsilastimaStyle,
    get_all_styles,
)

from .scrapers import (
    scrape_github_trending,
    scrape_github_javascript_trends,
    scrape_github_nodejs_trends,
    scrape_hacker_news,
    scrape_tech_news,
    scrape_github_all_languages_trending,
    scrape_hacker_news_news,
)

__all__ = [
    "PromptStyle",
    "HikayeStyle",
    "HaberciStyle",
    "MeraklandiricaStyle",
    "KisaOzStyle",
    "AkademikStyle",
    "MaddelerStyle",
    "KarsilastimaStyle",
    "get_all_styles",
    "scrape_github_trending",
    "scrape_github_javascript_trends",
    "scrape_github_nodejs_trends",
    "scrape_hacker_news",
    "scrape_tech_news",
    "scrape_github_all_languages_trending",
    "scrape_hacker_news_news",
]
