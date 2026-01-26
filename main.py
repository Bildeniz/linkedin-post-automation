#!/usr/bin/env python3
"""
LinkedIn Content Automation CLI
A tool to automate daily LinkedIn content creation from trending topics.
Powered by DeepSeek AI.
"""

import os
import json
import random
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from dotenv import load_dotenv

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


# Prompt style definitions - multiple writing styles for variety
PROMPT_STYLES = {
    "hikaye": {
        "name": "📖 Hikaye Anlatma",
        "description": "Konuyu bir hikaye gibi, ilişkili bir senaryoyla anlat",
        "system": """Sen bir teknoloji yazarısın. Kısa bir hikaye veya senaryo şeklinde, trend teknoloji konusunu LinkedIn'e anlat.
TAMAMEN TÜRKÇE yaz ve 3–4 cümleyi geçme.
Konuyu senaryo oluşturarak basitleştirmeni istiyorum.
Konuyu insani ve relatable bir şekilde bağlantılandır.
Emoji: en fazla 1–2, gerekirse hiç.
Linki en sona tek başına bir satırda ekle.

Ton: Samimi hikaye anlatıcısı, kurgusal ama bilgilendirici.""",
    },
    "haberci": {
        "name": "📰 Haberci/Teknik Stili",
        "description": "Tarafsız, teknolojik ve bilgilendirici açıklama",
        "system": """Sen bir teknoloji muhabiri yardımcısısın. Haberci tonu ile, tarafsız ve bilgilendirici bir LinkedIn paylaşımı yaz.
TAMAMEN TÜRKÇE yaz ve 3–4 cümleyi geçme.
Kişisel deneyim iddiası yok; 'denedim, test ettim' gibi ifadeler kullanma.
Ne, neden, nasıl sorularını kısa cevapla.
Emoji: minimal (0–1), teknik ton için gerekli değilse hiç.
Linki en sona tek başına bir satırda ekle.

Ton: Objektif, profesyonel, bilgilendirici (gazetecilik tarzı).""",
    },
    "meraklandir": {
        "name": "✨ Meraklandırma/Etki",
        "description": "Neden önemli, ne değişecek, hangi problem çözüyor vb. vurgula",
        "system": """Sen bir teknoloji evangelistsin. Konunun etkisini ve önemini vurgulayan, meraklandırıcı bir paylaşım yaz.
TAMAMEN TÜRKÇE yaz ve 3–4 cümleyi geçme.
Konunun neden önemli olduğunu, hangi problemi çözdüğünü vurgula.
Bir soru sorabilirsin (örn. 'Hayal edin...' veya 'Ya eğer...').
Emoji: 1–2, enerji ve heyecan katacak şekilde.
Linki en sona tek başına bir satırda ekle.

Ton: Heyecanl­ı, düşündürücü, meraklı ve umutlu.""",
    },
    "kisa-oz": {
        "name": "⚡ Kısa ve Öz",
        "description": "Çok kısa, dakikada anlaşılır şekilde",
        "system": """Sen bir sosyal medya uzmanısın. Çok kısa ve öz, bir dakikada anlaşılır bir LinkedIn paylaşımı yaz.
TAMAMEN TÜRKÇE yaz, maksimum 2–3 cümle (hiç emoji gerekli değilse).
Asıl mesaj net, hızlı, vurgulu olsun.
Gereksiz detay ekleme.
Linki en sona tek başına bir satırda ekle.

Ton: Doğrudan, net, hızlı (tweet tarzında ama LinkedIn için).""",
    },
    "akademik": {
        "name": "🔬 Akademik/Derinlemesine",
        "description": "Biraz daha derinlemesine, teknik alt detaylar ile",
        "system": """Sen bir teknoloji araştırmacısısın. Biraz daha derinlemesine, teknik detayları açıklayan bir LinkedIn paylaşımı yaz.
TAMAMEN TÜRKÇE yaz ve 4 cümleyi aşma.
Konunun teknik yönlerini ve bağlamını açıkla (ama jargon yığını olma).
Neden ortaya çıktığını, gelecek için ne ifade ettiğini söyle.
Emoji: minimal (0–1).
Linki en sona tek başına bir satırda ekle.

Ton: Eğitici, düşünceli, teknik ama anlaşılır.""",
    },
}


class LinkedInAutomator:
    """
    Main class for automating LinkedIn content creation from trending topics.
    """
    
    def __init__(self):
        """Initialize the automator with configuration and setup."""
        load_dotenv()
        
        self.console = Console()
        self.history_file = "history.json"
        self.style_guide_path = os.getenv("STYLE_GUIDE_PATH", "style_guide.txt")
        
        # Load API keys from environment
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.linkedin_email = os.getenv("LINKEDIN_EMAIL")
        self.linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        
        # Validate configuration
        self._validate_config()
        
        # Initialize DeepSeek client (OpenAI-compatible)
        self.openai_client = OpenAI(
            api_key=self.deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Load history
        self.history = self._load_history()
        
        # Track used style for current session
        self.current_style_key = None
        self.current_trend = None
    
    def _validate_config(self):
        """Validate that all required environment variables are set."""
        if not self.deepseek_api_key:
            self.console.print("[bold red]Error: DEEPSEEK_API_KEY not found in .env file[/bold red]")
            raise ValueError("Missing DEEPSEEK_API_KEY")
        
        if not self.linkedin_email or not self.linkedin_password:
            self.console.print("[yellow]Warning: LinkedIn credentials not found. Posting will be mocked.[/yellow]")
    
    def _load_history(self) -> Dict:
        """Load posting history from JSON file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    # Ensure dismissed array exists
                    if "dismissed" not in history:
                        history["dismissed"] = []
                    return history
            except json.JSONDecodeError:
                self.console.print("[yellow]Warning: Could not parse history.json. Starting fresh.[/yellow]")
                return {"posts": [], "dismissed": []}
        return {"posts": [], "dismissed": []}
    
    def _save_history(self, url: str, content: str):
        """Save a successful post to history."""
        self.history["posts"].append({
            "url": url,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def _is_already_posted(self, url: str) -> bool:
        """Check if a URL has already been posted or dismissed."""
        posted_urls = [post["url"] for post in self.history.get("posts", [])]
        dismissed_urls = self.history.get("dismissed", [])
        return url in posted_urls or url in dismissed_urls
    
    def _dismiss_trend(self, url: str):
        """Mark a trend as dismissed (don't show again)."""
        if "dismissed" not in self.history:
            self.history["dismissed"] = []
        if url not in self.history["dismissed"]:
            self.history["dismissed"].append(url)
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def _load_style_guide(self) -> str:
        """Load personal style guide from a text file if available, else use defaults."""
        default_style = (
            "- Ton: tarafsız ve kısa bir 'haberiniz olsun' paylaşımı.\n"
            "- Birinci tekil şahıs (ben) kullanma; kişisel deneyim iddiası yok.\n"
            "- 'Denedim, test ettim' gibi ifadelerden kaçın; bilgi aktar.\n"
            "- Bir cümlelik bağlam + 1–2 cümlelik değer; sade ve net.\n"
            "- Emoji: en fazla 1–2, gerekirse hiç kullanma.\n"
            "- Hashtag kullanma ya da çok nadir kullan (gerekli değilse atla).\n"
            "- Linki en sona tek başına bir satırda ver.\n"
            "- 3–4 cümleyi aşma; öz ve akıcı ol."
        )
        if os.path.exists(self.style_guide_path):
            try:
                with open(self.style_guide_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not read style guide '{self.style_guide_path}': {e}[/yellow]")
        return default_style
    
    def scrape_github_trending(self) -> List[Dict[str, str]]:
        """
        Scrape GitHub Trending page for Python/AI repositories.
        Returns top 3 trending items.
        """
        self.console.print("[cyan]🔍 GitHub'da trend konular aranıyor...[/cyan]")
        
        try:
            # GitHub Trending for Python
            url = "https://github.com/trending/python?since=daily"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article', class_='Box-row')
            
            trends = []
            for article in articles[:5]:  # Get top 5 to have backups
                try:
                    # Extract repository name
                    h2 = article.find('h2', class_='h3')
                    if not h2:
                        continue
                    
                    repo_link = h2.find('a')
                    if not repo_link:
                        continue
                    
                    repo_name = repo_link.get('href', '').strip('/')
                    repo_url = f"https://github.com/{repo_name}"
                    
                    # Extract description
                    desc_tag = article.find('p', class_='col-9')
                    description = desc_tag.get_text(strip=True) if desc_tag else "No description available"
                    
                    # Extract stars today
                    stars_tag = article.find('span', class_='d-inline-block float-sm-right')
                    stars = stars_tag.get_text(strip=True) if stars_tag else ""
                    
                    trends.append({
                        "title": repo_name,
                        "description": description,
                        "url": repo_url,
                        "stars": stars
                    })
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not parse a trend item: {e}[/yellow]")
                    continue
            
            if trends:
                self.console.print(f"[green]✓ {len(trends)} trend repository bulundu[/green]")
                return trends
            else:
                self.console.print("[yellow]GitHub'da trend bulunamadı. Hacker News'e bakılıyor...[/yellow]")
                return self.scrape_hacker_news()
                
        except Exception as e:
            self.console.print(f"[red]GitHub scraping hatası: {e}[/red]")
            self.console.print("[yellow]Hacker News'e geçiliyor...[/yellow]")
            return self.scrape_hacker_news()
    
    def scrape_hacker_news(self) -> List[Dict[str, str]]:
        """
        Scrape Hacker News front page for trending tech topics.
        Returns top 5 items.
        """
        try:
            # Use Hacker News API
            api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            story_ids = response.json()[:5]  # Get top 5 stories
            
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
                    self.console.print(f"[yellow]Warning: Could not fetch story {story_id}: {e}[/yellow]")
                    continue
            
            if trends:
                self.console.print(f"[green]✓ Hacker News'de {len(trends)} trend hikaye bulundu[/green]")
            return trends
            
        except Exception as e:
            self.console.print(f"[red]Hacker News scraping hatası: {e}[/red]")
            return []
    
    def scrape_github_javascript_trends(self) -> List[Dict[str, str]]:
        """
        Scrape GitHub trending JavaScript repositories.
        """
        try:
            self.console.print("[cyan]🔍 GitHub'da JavaScript trend konuları aranıyor...[/cyan]")
            url = "https://github.com/trending/javascript?since=daily"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article', class_='Box-row')
            trends = []
            
            for article in articles[:5]:  # Get top 5
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
                    self.console.print(f"[yellow]Warning: Could not parse a trend item: {e}[/yellow]")
                    continue
            
            if trends:
                self.console.print(f"[green]✓ {len(trends)} JavaScript trend repository bulundu[/green]")
                return trends
            else:
                return []
                
        except Exception as e:
            self.console.print(f"[red]GitHub JavaScript scraping hatası: {e}[/red]")
            return []
    
    def scrape_github_nodejs_trends(self) -> List[Dict[str, str]]:
        """
        Scrape GitHub trending Node.js related repositories.
        """
        try:
            self.console.print("[cyan]🔍 GitHub'da Node.js trend konuları aranıyor...[/cyan]")
            url = "https://github.com/trending?spoken_language_code=&since=daily"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article', class_='Box-row')
            trends = []
            
            for article in articles[:5]:  # Get top 5
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
                    self.console.print(f"[yellow]Warning: Could not parse a trend item: {e}[/yellow]")
                    continue
            
            if trends:
                self.console.print(f"[green]✓ {len(trends)} Node.js trend repository bulundu[/green]")
                return trends
            else:
                return []
                
        except Exception as e:
            self.console.print(f"[red]GitHub Node.js scraping hatası: {e}[/red]")
            return []
    
    def scrape_tech_news(self) -> List[Dict[str, str]]:
        """
        Scrape tech news from Dev.to API (no scraping needed, API available).
        """
        try:
            self.console.print("[cyan]🔍 Dev.to'dan teknoloji haberleri çekiliyor...[/cyan]")
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
                    self.console.print(f"[yellow]Warning: Could not parse article: {e}[/yellow]")
                    continue
            
            if trends:
                self.console.print(f"[green]✓ Dev.to'da {len(trends)} teknoloji haberi bulundu[/green]")
                return trends
            else:
                return []
                
        except Exception as e:
            self.console.print(f"[red]Dev.to scraping hatası: {e}[/red]")
            return []
    
    def generate_post_content(self, trend: Dict[str, str], style_key: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate LinkedIn post content using DeepSeek AI.
        Returns (content, style_key) tuple.
        """
        # Select or use provided style
        if style_key is None:
            style_key = random.choice(list(PROMPT_STYLES.keys()))
        
        style = PROMPT_STYLES.get(style_key, PROMPT_STYLES["haberci"])
        self.console.print(f"[cyan]🤖 {style['name']} kullanılıyor...[/cyan]")
        
        style_guide = self._load_style_guide()
        system_prompt = f"""{style['system']}

Aşağıdaki Stil Rehberi'ne sadık kal:
{style_guide}

Biçim:
- Akıcı ve doğal Türkçe.
- Gereksiz teknik jargon ve uzun cümlelerden kaçın.
- Okuyanı yormayan, insani ama net bir ton.
"""

        user_prompt = f"""Bu trend olan konu hakkında Türkçe bir LinkedIn paylaşımı oluştur:

Başlık: {trend['title']}
Açıklama: {trend['description']}
URL: {trend['url']}

Stil rehberini ve yukarıdaki talimatları uygula."""

        try:
            response = self.openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            self.current_style_key = style_key
            self.console.print("[green]✓ İçerik başarıyla oluşturuldu[/green]")
            return content, style_key
            
        except Exception as e:
            self.console.print(f"[red]İçerik oluşturma hatası: {e}[/red]")
            raise
    
    def display_preview(self, content: str):
        """Display the generated content in a beautiful panel."""
        panel = Panel(
            content,
            title="[bold cyan]📝 Oluşturulan LinkedIn İçeriği[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print("\n")
        self.console.print(panel)
        self.console.print("\n")
    
    def get_user_approval(self, content: str, trend: Dict[str, str]) -> Tuple[bool, str, bool]:
        """
        Ask user for approval to save content.
        If user edits, allow regeneration with different style.
        Returns (approved, final_content, is_dismissed)
        """
        self.display_preview(content)
        
        self.console.print("[dim]y = Kaydet  |  n = Atla  |  e = Düzenle  |  d = Beğenmedim (atlat)[/dim]")
        choice = Prompt.ask(
            "[bold yellow]Ne yapmak istersiniz?[/bold yellow]",
            choices=["y", "n", "e", "d"],
            default="y"
        )
        
        if choice == "y":
            return True, content, False
        elif choice == "d":
            # Mark as dismissed and skip
            self.console.print("[yellow]📋 Bu trend tekrar gösterilmeyecek.[/yellow]")
            return False, content, True
        elif choice == "e":
            # Show available styles
            self.console.print("\n[bold cyan]Mevcut Stil Seçenekleri:[/bold cyan]")
            styles_list = list(PROMPT_STYLES.items())
            for i, (key, style_info) in enumerate(styles_list, 1):
                marker = " ← Mevcut" if key == self.current_style_key else ""
                self.console.print(f"  {i}. {style_info['name']}: {style_info['description']}{marker}")
            
            choice_input = Prompt.ask(
                "[bold yellow]Hangi stil ile yeniden oluşturmak istersiniz? (1-5 veya manual edit)[/bold yellow]",
                default="1"
            )
            
            # Check if user picked a number
            try:
                style_num = int(choice_input)
                if 1 <= style_num <= len(styles_list):
                    selected_style_key = styles_list[style_num - 1][0]
                    self.console.print(f"\n[cyan]🔄 {PROMPT_STYLES[selected_style_key]['name']} ile yeniden oluşturuluyor...[/cyan]")
                    new_content, _ = self.generate_post_content(trend, style_key=selected_style_key)
                    # Recursive call to show approval menu again for new content
                    return self.get_user_approval(new_content, trend)
                else:
                    self.console.print("[red]Geçersiz seçim. Manual düzenlemeye geçiliyor.[/red]")
            except ValueError:
                pass
            
            # Manual edit fallback
            self.console.print("\n[cyan]Manuel düzenleme modu girin (bitirmek için Enter'a iki kez basın):[/cyan]")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            
            # Remove the last empty line
            if lines and lines[-1] == "":
                lines = lines[:-1]
            
            edited_content = "\n".join(lines)
            if edited_content.strip():
                self.display_preview(edited_content)
                # Recursive call to show approval menu again for edited content
                return self.get_user_approval(edited_content, trend)
            else:
                self.console.print("[red]İçerik girilmedi. Atlanıyor.[/red]")
                return False, content, False
        else:
            return False, content, False
    
    def save_content(self, content: str, trend_url: str):
        """
        Save content to file and optionally to clipboard.
        User will manually post to LinkedIn.
        """
        self.console.print("\n[cyan]📝 İçerik hazırlandı![/cyan]")
        
        # Save to a text file
        output_file = "linkedin_post.txt"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
                f.write("\n\n" + "="*50)
                f.write(f"\n✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} tarihinde oluşturuldu")
                f.write(f"\n📌 Stil: {PROMPT_STYLES[self.current_style_key]['name']}")
            
            self.console.print(f"[green]✓ İçerik '{output_file}' dosyasına kaydedildi[/green]")
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Dosya kaydetme hatası: {e}[/yellow]")
        
        # Copy to clipboard if available
        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(content)
                self.console.print("[green]✓ İçerik panoya kopyalandı! (Ctrl+V ile yapıştırabilirsiniz)[/green]")
            except Exception as e:
                self.console.print(f"[yellow]⚠️  Panoya kopyalama hatası: {e}[/yellow]")
        else:
            self.console.print("[yellow]💡 İpucu: 'pip install pyperclip' ile otomatik kopyalama özelliğini aktifleştirebilirsiniz[/yellow]")
    
    def run(self):
        """Main execution flow."""
        self.console.print("\n")
        self.console.print(Panel.fit(
            "[bold cyan]LinkedIn İçerik Otomasyonu[/bold cyan]\n"
            "Günlük teknoloji içeriklerinizi otomatikleştirin 🚀",
            border_style="cyan"
        ))
        self.console.print("\n")
        
        # Step 1: Get trending topics from multiple sources
        self.console.print("[bold cyan]📡 Birden fazla kaynaktan trend konuları alınıyor...[/bold cyan]\n")
        
        all_trends = []
        
        # Python trends (main source)
        python_trends = self.scrape_github_trending()
        if python_trends:
            for trend in python_trends:
                trend["source"] = "🐍 Python"
            all_trends.extend(python_trends)
        
        # JavaScript trends
        js_trends = self.scrape_github_javascript_trends()
        if js_trends:
            for trend in js_trends:
                trend["source"] = "🟨 JavaScript"
            all_trends.extend(js_trends)
        
        # General trending (Node.js, etc.)
        nodejs_trends = self.scrape_github_nodejs_trends()
        if nodejs_trends:
            for trend in nodejs_trends:
                trend["source"] = "💚 Node.js"
            all_trends.extend(nodejs_trends[:3])  # Limit to 3
        
        # Tech news from Dev.to
        tech_news = self.scrape_tech_news()
        if tech_news:
            for trend in tech_news:
                trend["source"] = "📰 Dev.to"
            all_trends.extend(tech_news)
        
        # Hacker News as fallback
        if not all_trends:
            hn_trends = self.scrape_hacker_news()
            if hn_trends:
                for trend in hn_trends:
                    trend["source"] = "📢 Hacker News"
                all_trends.extend(hn_trends)
        
        if not all_trends:
            self.console.print("[red]❌ Hiç trend konu bulunamadı. Lütfen daha sonra tekrar deneyin.[/red]")
            return
        
        self.console.print(f"[green]✓ Toplam {len(all_trends)} trend konu bulundu![/green]\n")
        
        # Step 2: Loop through trends until one is approved or all are skipped
        for trend_index, selected_trend in enumerate(all_trends):
            # Check if already posted or dismissed
            if self._is_already_posted(selected_trend["url"]):
                continue
            
            # Store current trend for edit flow
            self.current_trend = selected_trend
            
            # Display selected trend
            source = selected_trend.get("source", "📌 Unknown")
            self.console.print(f"\n[green]✓ Seçilen trend ({trend_index + 1}/{len(all_trends)}):[/green] {source} [bold]{selected_trend['title']}[/bold]")
            self.console.print(f"[dim]{selected_trend['url']}[/dim]\n")
            
            # Step 3: Generate content
            try:
                post_content, style_key = self.generate_post_content(selected_trend)
            except Exception as e:
                self.console.print(f"[red]İçerik oluşturulamadı: {e}[/red]")
                continue
            
            # Step 4: Get user approval (with regeneration option)
            approved, final_content, is_dismissed = self.get_user_approval(post_content, selected_trend)
            
            if is_dismissed:
                # Mark as dismissed and continue to next
                self._dismiss_trend(selected_trend["url"])
                self.console.print(f"[dim]Sonraki trend'e geçiliyor...\n[/dim]")
                continue
            
            if not approved:
                self.console.print("[yellow]İçerik kaydedilmedi. Sonraki trend'e geçiliyor.\n[/yellow]")
                continue
            
            # Step 5: Save content (no auto-posting)
            self.save_content(final_content, selected_trend["url"])
            
            # Step 6: Save to history
            self._save_history(selected_trend["url"], final_content)
            
            self.console.print("\n[bold green]✅ Tamamlandı! İçerik hazır.[/bold green]")
            self.console.print("[bold cyan]📋 Şimdi LinkedIn'e gidip manuel olarak paylaşabilirsiniz![/bold cyan]")
            self.console.print(f"[dim]Geçmiş kaydedildi: {self.history_file}[/dim]\n")
            
            # Successfully processed a trend, exit
            break
        else:
            # All trends were dismissed or skipped
            self.console.print("[yellow]✓ Tüm trend konular zaten kullanıldı veya atlandı![/yellow]")
            self.console.print("[cyan]Yeni içerik için yarın tekrar deneyin.[/cyan]")


def main():
    """Entry point for the CLI tool."""
    try:
        automator = LinkedInAutomator()
        automator.run()
    except KeyboardInterrupt:
        print("\n\nİşlem kullanıcı tarafından iptal edildi.")
    except Exception as e:
        console = Console()
        console.print(f"\n[bold red]Ölümcül hata: {e}[/bold red]\n")
        raise


if __name__ == "__main__":
    main()
