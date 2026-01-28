#!/usr/bin/env python3
"""
LinkedIn Content Automation CLI
A tool to automate daily LinkedIn content creation from trending topics.
Powered by DeepSeek AI.

Refactored to use modular architecture (core/ and utils/).
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from dotenv import load_dotenv

# Modular imports from core/
from core import get_all_styles
from core.scrapers import (
    scrape_github_trending,
    scrape_github_javascript_trends,
    scrape_github_nodejs_trends,
    scrape_hacker_news,
    scrape_tech_news,
    scrape_github_all_languages_trending,
    scrape_hacker_news_news,
)

# Check if pyperclip is available
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


# Initialize PROMPT_STYLES from modular styles
PROMPT_STYLES = get_all_styles()


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
        # Long form toggle (4–5 cümle için)
        self.long_form = False

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
            "- Bir cümlelik bağlam + 3-4 cümlelik değer; sade ve net.\n"
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
        length_instruction = (
            "4–5 cümle yaz; gerektiğinde 2 kısa paragraf kullan; gereksiz uzatma yok."
            if self.long_form
            else "2–3 cümlede tut; tek paragraf yeter; net ve öz ol."
        )

        system_prompt = f"""{style['system']}

    Aşağıdaki Stil Rehberi'ne sadık kal:
    {style_guide}

    Biçim:
    - Akıcı ve doğal Türkçe.
    - Gereksiz teknik jargon ve uzun cümlelerden kaçın.
    - Okuyanı yormayan, insani ama net bir ton.
    - {length_instruction}
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
                max_tokens=500
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
                "[bold yellow]Hangi stil ile yeniden oluşturmak istersiniz? (1-7 veya manual edit)[/bold yellow]",
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

        # Long form toggle
        self.long_form = Confirm.ask(
            "[yellow]Daha uzun (4–5 cümle) formatta yazılsın mı?[/yellow]",
            default=False
        )

        # Step 1: Get trending topics from multiple sources (parallel)
        self.console.print("[bold cyan]📡 Birden fazla kaynaktan trend konuları alınıyor (paralel)...[/bold cyan]\n")

        # Define all scrapers with their metadata
        scrapers = [
            ("🐍 Python", scrape_github_trending, 5),
            ("🟨 JavaScript", scrape_github_javascript_trends, 5),
            ("💚 Node.js", scrape_github_nodejs_trends, 3),
            ("🌍 GitHub All", scrape_github_all_languages_trending, 3),
            ("📰 Dev.to", scrape_tech_news, 5),
            ("📢 HN News", scrape_hacker_news_news, 5),
        ]

        all_trends = []
        completed_sources = []

        # Execute scrapers in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_source = {
                executor.submit(scraper): (name, scraper, limit)
                for name, scraper, limit in scrapers
            }

            # Process completed tasks as they finish
            for future in as_completed(future_to_source):
                source_name, scraper_func, limit = future_to_source[future]
                try:
                    trends = future.result()
                    count = len(trends[:limit]) if trends else 0

                    if trends:
                        for trend in trends[:limit]:
                            trend["source"] = source_name
                        all_trends.extend(trends[:limit])

                    status = f"✅ {source_name}: {count} bulundu"
                    completed_sources.append(status)
                    self.console.print(status)

                except Exception as e:
                    status = f"❌ {source_name}: Hata"
                    completed_sources.append(status)
                    self.console.print(f"[yellow]{status} ({str(e)[:30]})[/yellow]")

        # Summary
        self.console.print(f"\n[bold cyan]✅ Tüm kaynaklar tarandı! Toplam {len(all_trends)} trend bulundu.[/bold cyan]\n")

        # Hacker News as fallback
        if not all_trends:
            hn_trends = scrape_hacker_news()
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
