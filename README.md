# 🚀 LinkedIn İçerik Otomasyonu

Günlük LinkedIn içeriklerinizi otomatikleştiren bir Python CLI aracı. Trend teknoloji konularını bulur, DeepSeek AI ile **Türkçe** içerik oluşturur ve sizin manuel olarak LinkedIn'e eklemeniz için hazırlar.

## ✨ Özellikler

- 🔍 **Trend Avcılığı**: GitHub Trending (Python) ve Hacker News'den otomatik konu bulma
- 🤖 **Türkçe İçerik**: DeepSeek AI ile samimi, ilgi çekici Türkçe LinkedIn gönderileri
- 📝 **Manuel Paylaşım**: İçeriği gözden geçirip kendiniz LinkedIn'e ekleyin
- � **Otomatik Kopyalama**: İçerik panoya kopyalanır, direkt Ctrl+V ile yapıştırın
- 💾 **Dosyaya Kaydetme**: Her içerik `linkedin_post.txt` dosyasına kaydedilir
- 📚 **Akıllı Geçmiş**: Aynı konuları tekrar kullanmamak için geçmiş takibi
- 🎨 **Güzel Terminal Arayüzü**: Rich kütüphanesi ile renkli ve şık çıktılar
- ⚡ **Kolay Kurulum**: `.env` dosyası ile basit yapılandırma

## 🛠️ Teknoloji Stack

- Python 3.8+
- `requests` & `beautifulsoup4` - Web scraping
- `openai` - DeepSeek AI entegrasyonu (OpenAI-uyumlu SDK)
- `rich` - Güzel terminal çıktıları
- `python-dotenv` - Yapılandırma yönetimi
- `pyperclip` - Panoya otomatik kopyalama
- `json` - Geçmiş takibi

## 📦 Kurulum

### 1. Klasöre Gidin

```bash
cd d:\Python\linkedin_post
```

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
2. **Geçmiş Kontrolü**: Daha önce kullandığınız konuları atlar
3. **AI İçerik Üretimi**: Türkçe, samimi bir LinkedIn gönderisi oluşturur
4. **Önizleme & Onay**: İçeriği görürsünüz:
   - `y` - Kaydet ve kullan
   - `n` - Bu konuyu atla
   - `e` - İçeriği manuel olarak düzenle
5. **Kaydetme**: İçerik dosyaya kaydedilir ve panoya kopyalanır
6. **Manuel Paylaşım**: LinkedIn'e gidip Ctrl+V ile paylaşın!

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

API anahtarinizi [DeepSeek Platform](https://platform.deepseek.com/api_keys) adresinden alın
### LinkedIn Credentials (Gerekmez)

Manuel paylaşım kullandığınız için LinkedIn kimlik bilgilerine ihtiyaç yoktur.

## 🎯 Gelişmiş Kullanım

### AI Prompt'ı Özelleştirme

`generate_post_content()` metodundaki `system_prompt`'u düzenleyerek ton ve stili değiştirebilirsiniz:

```python
system_prompt = """Kendi talimatlarınız..."""
```

### Trend Kaynaklarını Değiştirme

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
