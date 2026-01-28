#!/usr/bin/env python3
"""
LinkedIn Content Automation - Streamlit Web Interface
Modern, interactive dashboard for managing LinkedIn content generation.
"""

import streamlit as st
import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

# Add parent directory to path to import main module
sys.path.insert(0, str(Path(__file__).parent))

from main import LinkedInAutomator, PROMPT_STYLES
from core.scrapers import (
    scrape_github_trending,
    scrape_github_javascript_trends,
    scrape_github_nodejs_trends,
    scrape_hacker_news,
    scrape_tech_news,
    scrape_github_all_languages_trending,
    scrape_hacker_news_news,
)
import json
from datetime import datetime

# Custom trends file path
CUSTOM_TRENDS_FILE = "custom_trends.json"

def load_custom_trends():
    """Load custom trends from file."""
    if os.path.exists(CUSTOM_TRENDS_FILE):
        try:
            with open(CUSTOM_TRENDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_custom_trends(trends):
    """Save custom trends to file."""
    with open(CUSTOM_TRENDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(trends, f, ensure_ascii=False, indent=2)

# Page configuration
st.set_page_config(
    page_title="LinkedIn İçerik Otomasyonu",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .css-1q7y456 {
        margin-top: 1rem;
    }
    .preview-box {
        border: 2px solid #00d4ff;
        border-radius: 8px;
        padding: 1.5rem;
        background-color: #f0f8ff;
        margin: 1rem 0;
    }
    .info-box {
        border: 2px solid #90EE90;
        border-radius: 8px;
        padding: 1rem;
        background-color: #f0fff0;
        margin: 0.5rem 0;
    }
    .warning-box {
        border: 2px solid #FFD700;
        border-radius: 8px;
        padding: 1rem;
        background-color: #fffacd;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "automator" not in st.session_state:
        try:
            st.session_state.automator = LinkedInAutomator()
        except ValueError as e:
            st.error(f"⚠️ Konfigürasyon hatası: {e}")
            st.stop()
        except Exception as e:
            st.error(f"⚠️ Beklenmedik hata: {e}")
            st.stop()
    
    if "trends" not in st.session_state:
        st.session_state.trends = []
    
    if "current_content" not in st.session_state:
        st.session_state.current_content = None
    
    if "current_style" not in st.session_state:
        st.session_state.current_style = None
    
    if "current_trend_index" not in st.session_state:
        st.session_state.current_trend_index = 0
    
    if "custom_trends" not in st.session_state:
        st.session_state.custom_trends = load_custom_trends()
    
    if "show_post_detail" not in st.session_state:
        st.session_state.show_post_detail = None


def display_header():
    """Display the main header."""
    st.markdown("""
    # 🚀 LinkedIn İçerik Otomasyonu
    ✨ DeepSeek AI ile Türkçe LinkedIn gönderileri oluşturun
    """)
    st.divider()


def display_history_stats():
    """Display statistics about posted and dismissed content."""
    automator = st.session_state.automator
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        posted_count = len(automator.history.get("posts", []))
        st.metric("📝 Yayınlanan", posted_count)
    
    with col2:
        dismissed_count = len(automator.history.get("dismissed", []))
        st.metric("🚫 Atlanan", dismissed_count)
    
    with col3:
        total = posted_count + dismissed_count
        st.metric("📊 Toplam", total)


def display_sidebar():
    """Display sidebar with options."""
    st.sidebar.title("⚙️ Kontrol Paneli")
    
    # Manual trend addition
    st.sidebar.subheader("➕ Manuel Trend Ekle")
    with st.sidebar.expander("🔗 Yeni Trend Girin", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            manual_title = st.text_input(
                "Başlık",
                placeholder="örn: DeepSeek v2",
                key="manual_title"
            )
        with col2:
            manual_url = st.text_input(
                "URL",
                placeholder="https://github.com/...",
                key="manual_url"
            )
        
        manual_desc = st.text_area(
            "Açıklama",
            placeholder="Trend hakkında kısa açıklama",
            height=100,
            key="manual_desc"
        )
        
        if st.button("✅ Trend Ekle", use_container_width=True):
            if manual_title and manual_url:
                new_trend = {
                    "title": manual_title,
                    "url": manual_url,
                    "description": manual_desc or "Manuel olarak eklenen trend",
                    "source": "🔗 Manual",
                    "added_date": datetime.now().isoformat()
                }
                st.session_state.custom_trends.append(new_trend)
                save_custom_trends(st.session_state.custom_trends)
                # Add to main trends list
                st.session_state.trends.append(new_trend)
                st.success(f"✅ '{manual_title}' eklendi!")
                st.rerun()
            else:
                st.error("❌ Başlık ve URL gereklidir!")
    
    # Long form toggle
    long_form_choice = st.sidebar.checkbox(
        "📝 Daha uzun içerik (4–5 cümle)",
        value=getattr(st.session_state.automator, "long_form", False),
        help="Tiklersen içerik 4–5 cümle olur; tik yoksa 2–3 cümle yazılır."
    )
    st.session_state.automator.long_form = long_form_choice

    # Trend fetching with async/parallel support
    st.sidebar.subheader("1️⃣ Otomatik Trend Bulma")
    if st.sidebar.button("🔍 Trend Ara", key="fetch_trends", use_container_width=True):
        # Define all scrapers with their metadata
        scrapers = [
            ("🐍 Python", scrape_github_trending, 5),
            ("🟨 JavaScript", scrape_github_javascript_trends, 5),
            ("💚 Node.js", scrape_github_nodejs_trends, 3),
            ("🌍 GitHub All", scrape_github_all_languages_trending, 3),
            ("📰 Dev.to", scrape_tech_news, 5),
            ("📢 HN News", scrape_hacker_news_news, 5),
        ]
        
        # Status placeholder for real-time updates
        status_placeholder = st.empty()
        results_placeholder = st.empty()
        
        with status_placeholder.container():
            st.info("🔄 Kaynaklar paralel olarak taranıyor...")
        
        # Execute scrapers in parallel
        all_trends = []
        completed_sources = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
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
                    
                    # Add source tag and limit results
                    if trends:
                        for trend in trends[:limit]:
                            trend["source"] = source_name
                        all_trends.extend(trends[:limit])
                    
                    completed_sources.append(f"✅ {source_name}: {count} bulundu")
                    
                    # Update status in real-time
                    with status_placeholder.container():
                        st.info(f"🔄 Taranıyor... ({len(completed_sources)}/6)\n\n" + 
                               "\n".join(completed_sources))
                    
                except Exception as e:
                    completed_sources.append(f"❌ {source_name}: Hata ({str(e)[:30]})")
        
        # Final results
        if all_trends:
            st.session_state.trends = st.session_state.custom_trends + all_trends
            st.session_state.current_trend_index = 0
            
            with status_placeholder.container():
                st.success(f"✅ Tüm kaynaklar tarandı! Toplam {len(all_trends)} trend bulundu.\n\n" + 
                          "\n".join(completed_sources))
        else:
            with status_placeholder.container():
                st.error(f"❌ Trend bulunamadı.\n\n" + 
                        "\n".join(completed_sources))
    
    # Trends list
    if st.session_state.trends:
        st.sidebar.subheader("2️⃣ Konuları Seç")
        
        # Find next unprocessed trend as default
        for idx, trend in enumerate(st.session_state.trends):
            if not st.session_state.automator._is_already_posted(trend["url"]):
                st.session_state.current_trend_index = idx
                break
        
        # Group trends by source
        trends_by_source = {}
        for t in st.session_state.trends:
            source = t.get("source", "Bilinmiyor")
            if source not in trends_by_source:
                trends_by_source[source] = []
            trends_by_source[source].append(t)
        
        # Display source tabs
        st.sidebar.markdown("**📊 Kaynaklar:**")
        source_cols = st.sidebar.columns(len(trends_by_source))
        for col, (source, trends) in zip(source_cols, trends_by_source.items()):
            with col:
                st.metric(source.split()[0], len(trends))
        
        # Create trend labels for selectbox
        trend_labels = []
        for t in st.session_state.trends:
            source = t.get("source", "")
            title = t["title"][:30]
            is_done = "✓" if st.session_state.automator._is_already_posted(t["url"]) else "○"
            label = f"{is_done} {source} {title}"
            trend_labels.append(label)
        
        # Selectbox for all trends
        selected_idx = st.sidebar.selectbox(
            "Konu seçin:",
            range(len(st.session_state.trends)),
            index=st.session_state.current_trend_index,
            format_func=lambda i: trend_labels[i],
            key="trend_selector"
        )
        
        # Update current trend index
        st.session_state.current_trend_index = selected_idx
        current_trend = st.session_state.trends[st.session_state.current_trend_index]
        
        # Display selected trend details with full info
        source = current_trend.get("source", "")
        description = current_trend.get("description", "Açıklama yok")
        st.sidebar.info(
            f"{source}\n**{current_trend['title']}**\n\n"
            f"📝 {description}\n\n"
            f"[🔗 Link]({current_trend['url']})"
        )
        
        if st.sidebar.button("🤖 İçerik Oluştur", use_container_width=True):
            with st.spinner("AI içerik oluşturuyor..."):
                try:
                    # Get the currently selected trend
                    selected_trend = st.session_state.trends[st.session_state.current_trend_index]
                    content, style = st.session_state.automator.generate_post_content(selected_trend)
                    st.session_state.current_content = content
                    st.session_state.current_style = style
                    st.success("✅ İçerik oluşturuldu!")
                except Exception as e:
                    st.error(f"Hata: {e}")
    
    # History section
    st.sidebar.divider()
    st.sidebar.subheader("📚 Geçmiş")
    
    with st.sidebar.expander("✅ Yayınlanan İçerik"):
        automator = st.session_state.automator
        posts = automator.history.get("posts", [])
        if posts:
            st.caption(f"_Toplam: {len(posts)} yazı_")
            for i, post in enumerate(reversed(posts[-10:]), 1):  # Show last 10
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"**{post['url'].split('/')[-1]}**")
                    st.caption(f"📅 {post['timestamp'][:10]}")
                with col2:
                    if st.button("👁️", key=f"view_post_{i}", help="Yazıyı görüntüle"):
                        st.session_state.show_post_detail = post
                        st.rerun()
        else:
            st.info("Henüz yayınlanan içerik yok")
    
    with st.sidebar.expander("🚫 Atlanan Konular"):
        dismissed = automator.history.get("dismissed", [])
        if dismissed:
            st.caption(f"_Toplam: {len(dismissed)} konu_")
            for url in dismissed[-10:]:  # Show last 10
                st.caption(f"🔗 {url.split('/')[-1]}")
        else:
            st.info("Henüz atlanan konu yok")
    
    # Custom trends management
    if st.session_state.custom_trends:
        st.sidebar.divider()
        st.sidebar.subheader("🔗 Manuel Trendler")
        
        for idx, trend in enumerate(st.session_state.custom_trends):
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.caption(f"📌 {trend['title'][:25]}...")
            with col2:
                if st.button("🗑️", key=f"remove_trend_{idx}", help="Sil"):
                    st.session_state.custom_trends.pop(idx)
                    save_custom_trends(st.session_state.custom_trends)
                    # Remove from trends list too
                    st.session_state.trends = [t for t in st.session_state.trends if t.get('url') != trend['url']]
                    st.success("✅ Trend silindi!")
                    st.rerun()


def display_content_preview():
    """Display content preview and options."""
    if not st.session_state.current_content:
        st.info("📝 Henüz içerik oluşturulmadı. Başlamak için sidebar'dan 'İçerik Oluştur' düğmesine tıklayın.")
        return
    
    st.subheader("📝 Oluşturulan İçerik")
    
    # Style info
    if st.session_state.current_style:
        style_info = PROMPT_STYLES.get(st.session_state.current_style, {})
        st.info(f"📌 **Stil:** {style_info.get('name', 'Bilinmiyor')}")
    
    # Content preview
    st.markdown("""
    <div class="preview-box">
    """, unsafe_allow_html=True)
    st.write(st.session_state.current_content)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Kaydet", use_container_width=True, key="save_btn"):
            automator = st.session_state.automator
            trend = st.session_state.trends[st.session_state.current_trend_index]
            automator.save_content(st.session_state.current_content, trend["url"])
            automator._save_history(trend["url"], st.session_state.current_content)
            st.success("✅ İçerik kaydedildi ve panoya kopyalandı!")
            st.session_state.current_content = None
            st.session_state.current_style = None
            st.rerun()
    
    with col2:
        if st.button("🚫 Atla", use_container_width=True, key="skip_btn"):
            st.session_state.current_content = None
            st.session_state.current_style = None
            st.info("⏭️ Sonraki trend'e geçiliyor...")
            st.rerun()
    
    with col3:
        if st.button("❌ Beğenmedim", use_container_width=True, key="dismiss_btn"):
            automator = st.session_state.automator
            trend = st.session_state.trends[st.session_state.current_trend_index]
            automator._dismiss_trend(trend["url"])
            st.session_state.current_content = None
            st.session_state.current_style = None
            st.warning("🚫 Bu trend tekrar gösterilmeyecek.")
            st.rerun()
    
    with col4:
        if st.button("✏️ Düzenle", use_container_width=True, key="edit_btn"):
            st.session_state.show_edit_modal = True
            st.rerun()


def display_style_selector():
    """Display style selector for regeneration."""
    st.subheader("🎨 Stil Değiştir")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        style_options = {v["name"]: k for k, v in PROMPT_STYLES.items()}
        selected_style_name = st.selectbox(
            "Yeni bir stil seçin:",
            list(style_options.keys()),
            key="style_selector"
        )
    
    with col2:
        if st.button("🔄 Yeniden Oluştur", use_container_width=True):
            selected_style = style_options[selected_style_name]
            trend = st.session_state.trends[st.session_state.current_trend_index]
            
            with st.spinner("Yeni stil ile oluşturuluyor..."):
                try:
                    content, style = st.session_state.automator.generate_post_content(
                        trend, 
                        style_key=selected_style
                    )
                    st.session_state.current_content = content
                    st.session_state.current_style = style
                    st.success("✅ Yeni stil ile oluşturuldu!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Hata: {e}")


def display_post_detail():
    """Display detailed view of a saved post."""
    if not st.session_state.show_post_detail:
        return
    
    post = st.session_state.show_post_detail
    
    st.subheader("📖 Yazı Detayı")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Tarih", post.get('timestamp', 'N/A')[:10])
    with col2:
        st.metric("🔗 Konu", post.get('url', 'N/A').split('/')[-1][:20])
    with col3:
        st.metric("📝 Karakter", len(post.get('content', '')))
    
    st.divider()
    
    # Content
    st.markdown("**📄 İçerik:**")
    st.markdown("""
    <div class="preview-box">
    """, unsafe_allow_html=True)
    st.write(post.get('content', 'İçerik bulunamadı'))
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Panoya Kopyala", use_container_width=True):
            import pyperclip
            pyperclip.copy(post.get('content', ''))
            st.success("✅ Panoya kopyalandı!")
    
    with col2:
        if st.button("💾 Dosyaya Kaydet", use_container_width=True):
            with open(f"post_{post.get('timestamp', 'unknown')[:10]}.txt", 'w', encoding='utf-8') as f:
                f.write(post.get('content', ''))
            st.success("✅ Dosyaya kaydedildi!")
    
    with col3:
        if st.button("❌ Kapat", use_container_width=True):
            st.session_state.show_post_detail = None
            st.rerun()


def display_manual_edit():
    """Display manual edit section."""
    st.subheader("✏️ Manuel Düzenleme")
    
    edited_content = st.text_area(
        "İçeriği düzenleyin:",
        value=st.session_state.current_content,
        height=200,
        key="manual_edit"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Düzenlemeyi Kaydet", use_container_width=True):
            st.session_state.current_content = edited_content
            st.success("✅ Düzenleme kaydedildi!")
            st.rerun()
    
    with col2:
        if st.button("❌ Düzenlemeyi İptal Et", use_container_width=True):
            st.rerun()


def main():
    """Main application."""
    initialize_session_state()
    
    # Check if showing post detail
    if st.session_state.show_post_detail:
        # Header
        display_header()
        display_post_detail()
        return
    
    # Header
    display_header()
    
    # Stats
    display_history_stats()
    st.divider()
    
    # Main layout with sidebar
    display_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_content_preview()
    
    with col2:
        if st.session_state.current_content:
            st.divider()
            display_style_selector()
            st.divider()
            
            with st.expander("✏️ Manuel Düzenleme"):
                display_manual_edit()


if __name__ == "__main__":
    main()
