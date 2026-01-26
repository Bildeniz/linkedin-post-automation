#!/usr/bin/env python3
"""
LinkedIn Content Automation - Streamlit Web Interface
Modern, interactive dashboard for managing LinkedIn content generation.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path to import main module
sys.path.insert(0, str(Path(__file__).parent))

from main import LinkedInAutomator, PROMPT_STYLES
import json

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
    
    # Trend fetching
    st.sidebar.subheader("1️⃣ Trend Bulma")
    if st.sidebar.button("🔍 Trend Ara", key="fetch_trends", use_container_width=True):
        with st.spinner("Trend'ler aranıyor..."):
            trends = st.session_state.automator.scrape_github_trending()
            if trends:
                st.session_state.trends = trends
                st.session_state.current_trend_index = 0
                st.success(f"✅ {len(trends)} trend bulundu!")
            else:
                st.error("❌ Trend bulunamadı")
    
    # Content generation
    if st.session_state.trends:
        st.sidebar.subheader("2️⃣ İçerik Oluştur")
        
        # Find next unprocessed trend
        for idx, trend in enumerate(st.session_state.trends):
            if not st.session_state.automator._is_already_posted(trend["url"]):
                st.session_state.current_trend_index = idx
                break
        
        current_trend = st.session_state.trends[st.session_state.current_trend_index]
        st.sidebar.info(f"📌 **{current_trend['title']}**")
        
        if st.sidebar.button("🤖 İçerik Oluştur", use_container_width=True):
            with st.spinner("AI içerik oluşturuyor..."):
                try:
                    content, style = st.session_state.automator.generate_post_content(current_trend)
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
            for i, post in enumerate(reversed(posts[-5:]), 1):  # Show last 5
                st.caption(f"**{i}. {post['url'].split('/')[-1]}**")
                st.caption(f"📅 {post['timestamp'][:10]}")
        else:
            st.info("Henüz yayınlanan içerik yok")
    
    with st.sidebar.expander("🚫 Atlanan Konular"):
        dismissed = automator.history.get("dismissed", [])
        if dismissed:
            for url in dismissed[-5:]:  # Show last 5
                st.caption(f"🔗 {url.split('/')[-1]}")
        else:
            st.info("Henüz atlanan konu yok")


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
