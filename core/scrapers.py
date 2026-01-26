"""
Web scraper modules for fetching trending topics from various sources.
Supports GitHub (Python, JavaScript, Node.js), Hacker News, and Dev.to.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from rich.console import Console


console = Console()


def scrape_github_trending() -> List[Dict[str, str]]:
    """
    Scrape GitHub Trending page for Python repositories.
    Returns top 5 trending items.
    """
    console.print("[cyan]🔍 GitHub'da trend konular aranıyor...[/cyan]")
    
    try:
        url = "https://github.com/trending/python?since=daily"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article', class_='Box-row')
        
        trends = []
        for article in articles[:5]:
            try:
                h2 = article.find('h2', class_='h3')
                if not h2:
                    continue
                
                repo_link = h2.find('a')
                if not repo_link:
                    continue
                
                repo_name = repo_link.get('href', '').strip('/')
                repo_url = f"https://github.com/{repo_name}"
                
                desc_tag = article.find('p', class_='col-9')
                description = desc_tag.get_text(strip=True) if desc_tag else "No description available"
                
                stars_tag = article.find('span', class_='d-inline-block float-sm-right')
                stars = stars_tag.get_text(strip=True) if stars_tag else ""
                
                trends.append({
                    "title": repo_name,
                    "description": description,
                    "url": repo_url,
                    "stars": stars
                })
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse a trend item: {e}[/yellow]")
                continue
        
        if trends:
            console.print(f"[green]✓ {len(trends)} trend repository bulundu[/green]")
            return trends
        else:
            console.print("[yellow]GitHub'da trend bulunamadı. Hacker News'e bakılıyor...[/yellow]")
            return scrape_hacker_news()
            
    except Exception as e:
        console.print(f"[red]GitHub scraping hatası: {e}[/red]")
        console.print("[yellow]Hacker News'e geçiliyor...[/yellow]")
        return scrape_hacker_news()


def scrape_github_javascript_trends() -> List[Dict[str, str]]:
    """Scrape GitHub trending JavaScript repositories."""
    try:
        console.print("[cyan]🔍 GitHub'da JavaScript trend konuları aranıyor...[/cyan]")
        url = "https://github.com/trending/javascript?since=daily"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('article', class_='Box-row')
        trends = []
        
        for article in articles[:5]:
            try:
                h2 = article.find('h2', class_='h3')
                if h2:
                    link = h2.find('a')
                    if link:
                        repo_url = "https://github.com" + link.get('href', '')
                        title = link.get_text(strip=True).replace('\n', ' ').strip()
                        
                        desc_elem = article.find('p', class_='col-9')
                        description = desc_elem.get_text(strip=True) if desc_elem else "No description"
                        
                        trends.append({
                            "title": title,
                            "description": description,
                            "url": repo_url,
                            "type": "JavaScript"
                        })
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse a trend item: {e}[/yellow]")
                continue
        
        if trends:
            console.print(f"[green]✓ {len(trends)} JavaScript trend repository bulundu[/green]")
            return trends
        else:
            return []
            
    except Exception as e:
        console.print(f"[red]GitHub JavaScript scraping hatası: {e}[/red]")
        return []


def scrape_github_nodejs_trends() -> List[Dict[str, str]]:
    """Scrape GitHub trending Node.js related repositories."""
    try:
        console.print("[cyan]🔍 GitHub'da Node.js trend konuları aranıyor...[/cyan]")
        url = "https://github.com/trending?spoken_language_code=&since=daily"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('article', class_='Box-row')
        trends = []
        
        for article in articles[:5]:
            try:
                h2 = article.find('h2', class_='h3')
                if h2:
                    link = h2.find('a')
                    if link:
                        repo_url = "https://github.com" + link.get('href', '')
                        title = link.get_text(strip=True).replace('\n', ' ').strip()
                        
                        desc_elem = article.find('p', class_='col-9')
                        description = desc_elem.get_text(strip=True) if desc_elem else "No description"
                        
                        trends.append({
                            "title": title,
                            "description": description,
                            "url": repo_url,
                            "type": "General"
                        })
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse a trend item: {e}[/yellow]")
                continue
        
        if trends:
            console.print(f"[green]✓ {len(trends)} Node.js trend repository bulundu[/green]")
            return trends
        else:
            return []
            
    except Exception as e:
        console.print(f"[red]GitHub Node.js scraping hatası: {e}[/red]")
        return []


def scrape_hacker_news() -> List[Dict[str, str]]:
    """Scrape Hacker News for trending tech topics. Returns top 5 items."""
    try:
        api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        story_ids = response.json()[:5]
        
        trends = []
        for story_id in story_ids:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url, timeout=5)
                story_data = story_response.json()
                
                if story_data and story_data.get('type') == 'story':
                    trends.append({
                        "title": story_data.get('title', 'Untitled'),
                        "description": story_data.get('title', 'No description'),
                        "url": story_data.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                        "score": story_data.get('score', 0)
                    })
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch story {story_id}: {e}[/yellow]")
                continue
        
        if trends:
            console.print(f"[green]✓ Hacker News'de {len(trends)} trend hikaye bulundu[/green]")
        return trends
        
    except Exception as e:
        console.print(f"[red]Hacker News scraping hatası: {e}[/red]")
        return []


def scrape_tech_news() -> List[Dict[str, str]]:
    """Scrape tech news from Dev.to API."""
    try:
        console.print("[cyan]🔍 Dev.to'dan teknoloji haberleri çekiliyor...[/cyan]")
        url = "https://dev.to/api/articles?top=7&per_page=5"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        articles = response.json()
        trends = []
        
        for article in articles:
            try:
                trends.append({
                    "title": article.get('title', 'Untitled'),
                    "description": article.get('description', 'No description')[:200],
                    "url": article.get('url', ''),
                    "type": "Dev.to"
                })
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse article: {e}[/yellow]")
                continue
        
        if trends:
            console.print(f"[green]✓ Dev.to'da {len(trends)} teknoloji haberi bulundu[/green]")
            return trends
        else:
            return []
            
    except Exception as e:
        console.print(f"[red]Dev.to scraping hatası: {e}[/red]")
        return []
