# 🚀 LinkedIn İçerik Otomasyonu

Günlük LinkedIn içeriklerinizi otomatikleştiren bir Python CLI aracı. Trend teknoloji konularını bulur, DeepSeek AI ile **Türkçe** içerik oluşturur ve sizin manuel olarak LinkedIn'e eklemeniz için hazırlar.

## ✨ Özellikler

- 🔍 **Trend Avcılığı**: GitHub Trending (Python) ve Hacker News'den otomatik konu bulma
- 🤖 **Türkçe İçerik**: DeepSeek AI ile samimi, ilgi çekici Türkçe LinkedIn gönderileri
- 📝 **Manuel Paylaşım**: İçeriği gözden geçirip kendiniz LinkedIn'e ekleyin
- � **Otomatik Kopyalama**: İçerik panoya kopyalanır, direkt Ctrl+V ile yapıştırın
- 💾 **Dosyaya Kaydetme**: Her içerik `linkedin_post.txt` dosyasına kaydedilir
Günlük LinkedIn içeriklerinizi otomatikleştiren Python aracı (CLI + Streamlit). Trend teknoloji konularını çoklu kaynaktan toplar, DeepSeek AI ile **Türkçe** içerik üretir, onayınıza sunar ve manuel paylaşım için hazırlar.
- 🎨 **Güzel Terminal Arayüzü**: Rich kütüphanesi ile renkli ve şık çıktılar
- ⚡ **Kolay Kurulum**: `.env` dosyası ile basit yapılandırma

- 🔍 **Çok Kaynaklı Trend Toplama**: GitHub Trending (Python, JavaScript, Node.js), Dev.to ve Hacker News
- 🎛️ **7 Stil Seçeneği**: Hikaye, Haberci, Meraklandırma, Kısa-Öz, Akademik, Maddeler, Karşılaştırma
- 🔄 **Edit/Dismiss Akışı**: Beğenmediğini “d” ile bir daha gösterme; farklı stil veya manuel edit sonrası yeniden onay menüsü
- 📏 **Uzun/Kısa Toggle**: 2–3 cümle veya 4–5 cümle seçimi (CLI ve Streamlit)
- 🧭 **Özel Trendler**: Manuel trend ekleme/silme, geçmiş/dismiss takibi
- 🖥️ **Streamlit UI**: Sidebar kontrolleri, önizleme, stil seçici, geçmiş görüntüleme
- 📚 **Akıllı Geçmiş**: Aynı linki yeniden sunmaz; `history.json` ile kayıt
- 💾 **Dosya + Pano**: İçerik `linkedin_post.txt` dosyasına yazılır, pano kopyası desteklenir
- `json` - Geçmiş takibi

## 📦 Kurulum

### 1. Klasöre Gidin

```bash
cd d:\Python\linkedin_post
```

- `streamlit` - Web arayüzü
### 2. Sanal Ortam Oluşturun (Önerilen)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Yapılandırın

Örnek yapılandırma dosyasını kopyalayın ve API anahtarlarınızı ekleyin:

```bash
copy .env.example .env
```

Edit `.env` and add your API keys:

```env
DEEPSEEK_API_KEY=sk-your-actual-deepseek-key-here
```

**Not**: LinkedIn kimlik bilgilerine ihtiyaç yoktur. İçerik otomatik olarak dosyaya kaydedilir ve panoya kopyalanır, siz manuel olarak LinkedIn'e eklersiniz.

## 🚀 Kullanım

Otomasyon aracını çalıştırın:

```bash
python main.py
```

### İş Akışı

1. **Trend Keşfi**: Araç GitHub Trending ve Hacker News'i tarar
### CLI
3. **AI İçerik Üretimi**: Türkçe, samimi bir LinkedIn gönderisi oluşturur
4. **Önizleme & Onay**: İçeriği görürsünüz:
python -X utf8 main.py
   - `n` - Bu konuyu atla
   - `e` - İçeriği manuel olarak düzenle
5. **Kaydetme**: İçerik dosyaya kaydedilir ve panoya kopyalanır
### Streamlit UI
6. **Manuel Paylaşım**: LinkedIn'e gidip Ctrl+V ile paylaşın!
```bash
streamlit run app.py
```

Tarayıcı: http://localhost:8501

### Örnek Çıktı

```
┌─────────────────────────────────────────┐
│  LinkedIn Content Automation            │
│  Automating your daily tech content 🚀  │
└─────────────────────────────────────────┘

🔍 Searching for trending topics on GitHub...
✓ Found 5 trending repositories
✓ Selected trend: microsoft/semantic-kernel

🤖 Generating post content with AI...
✓ Content generated successfully

┌─ 📝 Generated LinkedIn Post ────────────┐
│                                          │
│  Just discovered Semantic Kernel 🧠      │
│  Microsoft's new SDK for integrating     │
│  LLMs into your apps. The orchestration  │
│  features look incredible for building   │
│  AI agents. Worth checking out!          │
│                                          │
│  https://github.com/microsoft/semantic-  │
│  kernel                                  │
│                                          │
└──────────────────────────────────────────┘

What would you like to do? (y/n/e) [y]:
```

## 📁 Proje Yapısı

```
linkedin_post/
│
├── main.py              # Ana otomasyon scripti
├── requirements.txt     # Python bağımlılıkları
├── .env                 # API anahtarlarınız (COMMIT ETMEYİN)
├── .env.example         # Yapılandırma şablonu
├── linkedin_post.txt    # Otomatik oluşturulan içerik (son)
├── history.json         # Geçmiş kaydı (otomatik oluşur)
└── README.md            # Bu dosya
```

## 🔧 Yapılandırma Seçenekleri

### DeepSeek API Key (Gerekli)
├── main.py               # CLI giriş noktası (modüler import'lar)
├── app.py                # Streamlit arayüzü
├── core/
│   ├── styles.py         # 7 PromptStyle sınıfı
│   ├── scrapers.py       # Tüm trend kaynakları (GitHub, Dev.to, HN)
│   └── __init__.py       # Ortak export'lar
├── utils/                # Yardımcı modüller için yer
├── history.json          # Geçmiş (otomatik oluşur)
├── custom_trends.json    # Manuel eklenen trendler (UI/CLI)
├── linkedin_post.txt     # Son oluşturulan içerik
├── requirements.txt      # Bağımlılıklar
├── .env / .env.example   # Yapılandırma
└── README.md

### AI Prompt'ı Özelleştirme

`generate_post_content()` metodundaki `system_prompt`'u düzenleyerek ton ve stili değiştirebilirsiniz:
- 📖 Hikaye Anlatma
- 📰 Haberci/Teknik
- ✨ Meraklandırma/Etki
- ⚡ Kısa ve Öz
- 🔬 Akademik/Derinlemesine
- 📋 Maddeler ile Anlatım
- ⚖️ Karşılaştırma Analizi

```python
system_prompt = """Kendi talimatlarınız..."""
- GitHub Trending: Python, JavaScript, Node.js (genel)
- Dev.to teknoloji haberleri
- Hacker News (fallback)
```

### Trend Kaynaklarını Değiştirme
- `DEEPSEEK_API_KEY` zorunlu
- `STYLE_GUIDE_PATH` (opsiyonel) özel stil rehberi yolu
- CLI uzun/kısa format sorusu: 4–5 cümle veya 2–3 cümle
- Streamlit: Sidebar checkbox ile uzun/kısa seçimi

Farklı diller veya konular aramak için `scrape_github_trending()`'i düzenleyin:

```python
url = "https://github.com/trending/javascript?since=daily"  # JavaScript yerine
```

### Trend Sayısını Ayarlama

Scraping metodlarındaki dilimi değiştirin:

```python
articles = soup.find_all('article', class_='Box-row')[:10]  # İlk 10'u al
```

## 🐛 Sorun Giderme

### "DEEPSEEK_API_KEY not found"
`.env` dosyasını oluşturduğunuzdan (`.env.example` değil) ve gerçek DeepSeek API anahtarinizi eklediğinizden emin olun.

### "No trends found"
GitHub HTML yapısını değiştirmiş olabilir. Araç otomatik olarak Hacker News'e geçecektir.

### Panoya Kopyalama Çalışmıyor
`pip install pyperclip` komutunu çalıştırın. Linux'ta `xclip` veya `xsel` kurulu olmalıdır.

## 📝 Geçmiş Dosya Formatı

`history.json` dosyası kullanılan içerikleri saklar:

```json
{
  "posts": [
    {
      "url": "https://github.com/...",
      "content": "Gönderi içeriğiniz...",
      "timestamp": "2026-01-26T10:30:00"
    }
  ]
}
```

Geçmişi sıfırlamak veya belirli girişleri kaldırmak için bu dosyayı manuel olarak düzenleyebilirsiniz.

## 🔐 Güvenlik Notları

- **Asla `.env` dosyasını commit etmeyin** - versiyon kontrolüne eklemeyin
- `.env` dosyasını `.gitignore`'a ekleyin
- DeepSeek API anahtarinizi güvende tutun
- Hassas bilgilerinizi koruyun

## 📜 Lisans

Bu kişisel bir otomasyon aracıdır. Kullanım riski size aittir. LinkedIn'ın kullanım koşullarına ve sınırlamalarına saygı gösterin.

## 🤝 Katkıda Bulunma

Bu, kişisel kullanım için tasarlanmış tek dosyalık bir script'tir. İhtiyacınıza göre fork'layıp özelleştirebilirsiniz!

## 💡 İpuçları

- Bu aracı sabah rutininizin bir parçası olarak her gün çalıştırın
- Otomatik çalışma için Windows Görev Zamanlayıcı veya `cron` kullanın
- Kendi sesinizi bulmak için farklı AI prompt'ıları deneyin
- Otantikliği korumak için gönderileri gözden geçirin ve düzenleyin

## 📞 Destek

Sorunlar için:
- **DeepSeek API**: [DeepSeek Dokümantasyonu](https://platform.deepseek.com/docs)'nu kontrol edin
- **Web Scraping**: GitHub ve Hacker News HTML yapılarını değiştirebilir
- **Genel Sorular**: GitHub Issues kullanabilirsiniz

---

**İyi Paylaşımlar! 🎉**
