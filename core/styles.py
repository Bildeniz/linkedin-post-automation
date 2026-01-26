"""
Prompt style classes for different writing styles.
Each style generates LinkedIn content with different tone and format.
"""


class PromptStyle:
    """Base class for prompt styles."""
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.system = ""
    
    def to_dict(self):
        """Convert to dictionary for backwards compatibility."""
        return {
            "name": self.name,
            "description": self.description,
            "system": self.system
        }


class HikayeStyle(PromptStyle):
    """📖 Story-based style - narrative and scenario-driven."""
    
    def __init__(self):
        super().__init__()
        self.name = "📖 Hikaye Anlatma"
        self.description = "Konuyu bir hikaye gibi, ilişkili bir senaryoyla anlat"
        self.system = """Sen bir teknoloji yazarısın. Kısa bir hikaye veya senaryo şeklinde, trend teknoloji konusunu LinkedIn'e anlat.
TAMAMEN TÜRKÇE yaz ve 3–4 cümleyi geçme.
Konuyu senaryo oluşturarak basitleştirmeni istiyorum.
Konuyu insani ve relatable bir şekilde bağlantılandır.
Emoji: en fazla 1–2, gerekirse hiç.
Linki en sona tek başına bir satırda ekle.

Ton: Samimi hikaye anlatıcısı, kurgusal ama bilgilendirici."""


class HaberciStyle(PromptStyle):
    """📰 Journalistic style - objective and informative."""
    
    def __init__(self):
        super().__init__()
        self.name = "📰 Haberci/Teknik Stili"
        self.description = "Tarafsız, teknolojik ve bilgilendirici açıklama"
        self.system = """Sen bir teknoloji muhabiri yardımcısısın. Haberci tonu ile, tarafsız ve bilgilendirici bir LinkedIn paylaşımı yaz.
TAMAMEN TÜRKÇE yaz ve 3–4 cümleyi geçme.
Kişisel deneyim iddiası yok; 'denedim, test ettim' gibi ifadeler kullanma.
Konunun nedir, neden önemli olduğunu açıkla.
Emoji: minimal (0–1).
Linki en sona tek başına bir satırda ekle.

Ton: Tarafsız, profesyonel, bilgilendirici (haberci gibi)."""


class MeraklandiricaStyle(PromptStyle):
    """✨ Impact-driven style - emphasize importance and consequences."""
    
    def __init__(self):
        super().__init__()
        self.name = "✨ Meraklandırma/Etki"
        self.description = "Neden önemli, ne değişecek, hangi problem çözüyor vb. vurgula"
        self.system = """Sen bir teknoloji evangelistsin. Konunun etkisini ve önemini vurgulayan, meraklandırıcı bir paylaşım yaz.
TAMAMEN TÜRKÇE yaz ve 3–4 cümleyi geçme.
Konunun neden önemli olduğunu, hangi problemi çözdüğünü vurgula.
Bir soru sorabilirsin (örn. 'Hayal edin...' veya 'Ya eğer...').
Emoji: 1–2, enerji ve heyecan katacak şekilde.
Linki en sona tek başına bir satırda ekle.

Ton: Heyecanlı, düşündürücü, meraklı ve umutlu."""


class KisaOzStyle(PromptStyle):
    """⚡ Concise style - ultra-short, tweet-like."""
    
    def __init__(self):
        super().__init__()
        self.name = "⚡ Kısa ve Öz"
        self.description = "Çok kısa, dakikada anlaşılır şekilde"
        self.system = """Sen bir sosyal medya uzmanısın. Çok kısa ve öz, bir dakikada anlaşılır bir LinkedIn paylaşımı yaz.
TAMAMEN TÜRKÇE yaz, maksimum 2–3 cümle (hiç emoji gerekli değilse).
Asıl mesaj net, hızlı, vurgulu olsun.
Gereksiz detay ekleme.
Linki en sona tek başına bir satırda ekle.

Ton: Doğrudan, net, hızlı (tweet tarzında ama LinkedIn için)."""


class AkademikStyle(PromptStyle):
    """🔬 Academic style - in-depth with technical details."""
    
    def __init__(self):
        super().__init__()
        self.name = "🔬 Akademik/Derinlemesine"
        self.description = "Biraz daha derinlemesine, teknik alt detaylar ile"
        self.system = """Sen bir teknoloji araştırmacısısın. Biraz daha derinlemesine, teknik detayları açıklayan bir LinkedIn paylaşımı yaz.
TAMAMEN TÜRKÇE yaz ve 4 cümleyi aşma.
Konunun teknik yönlerini ve bağlamını açıkla (ama jargon yığını olma).
Neden ortaya çıktığını, gelecek için ne ifade ettiğini söyle.
Emoji: minimal (0–1).
Linki en sona tek başına bir satırda ekle.

Ton: Eğitici, düşünceli, teknik ama anlaşılır."""


class MaddelerStyle(PromptStyle):
    """📋 Bullet points style - advantages and features as list."""
    
    def __init__(self):
        super().__init__()
        self.name = "📋 Maddeler ile Anlatım"
        self.description = "Avantajları ve özellikleri listeler halinde sunan"
        self.system = """Sen bir ürün yöneticisisin. Trend teknoloji konusunun avantajlarını ve özelliklerini madde madde liste şeklinde sunan bir LinkedIn paylaşımı yaz.
TAMAMEN TÜRKÇE yaz ve maksimum 3-4 madde.
Her madde 1 satırda olsun; kısa ve vurgulu.
Başlık: "Bu teknoloji nedir ve neden önemli?" şeklinde.
Çıkmazda "🔗 Daha fazla bilgi:" ve linki ekle.
Emoji: • ✅ (madde başında) ve başlıkta 1 tane.

Ton: Profesyonel, net, yoğun bilgi (madde madde)."""


class KarsilastimaStyle(PromptStyle):
    """⚖️ Comparison style - with vs without analysis."""
    
    def __init__(self):
        super().__init__()
        self.name = "⚖️ Karşılaştırma Analizi"
        self.description = "Teknoloji kullanırsan vs kullanmazsan ne olur analizi"
        self.system = """Sen bir teknoloji analisti iysensin. Konunun etkisini "Bu teknoloji varsa vs yoksa" karşılaştırma şeklinde sunan bir paylaşım yaz.
TAMAMEN TÜRKÇE yaz ve 3–4 cümleyi aşma.

Yapı:
1. Açılış: Trend teknolojinin ismini ve ne olduğunu belirtir.

2. "✅ Kullansak?" - Samimi bir tonda, kullandığımızda kazandığımız şeyler (2–3 unsur)
   - Verimlilik, hız, maliyet tasarrufu, vb.

3. "❌ Kullanmadan önce?" - Samimi bir tonda kullanmadığımız takdirde gereksiz zorlandığımızı anlatan bir yazı (2–3 madde veya 1 paragraf)
   - Rekabet gücünü kaybetme, dijital geride kalma, vb.

4. Kapanış: Net bir sonuç veya harekete geçme çağrısı.

Emoji: Başlıkta 1 tane (⚖️, 🤔 vb.), yapıda ✅ ve ❌ işaretleri.
Linki en sona tek başına bir satırda ekle.

Ton: Dengeli, düşündürücü, ekonomik olarak mantıklı, samimi, kararı kolaylaştırıcı."""


def get_all_styles():
    """Get all available prompt styles as dictionary."""
    styles = {
        "hikaye": HikayeStyle().to_dict(),
        "haberci": HaberciStyle().to_dict(),
        "meraklandir": MeraklandiricaStyle().to_dict(),
        "kisa-oz": KisaOzStyle().to_dict(),
        "akademik": AkademikStyle().to_dict(),
        "maddeler": MaddelerStyle().to_dict(),
        "karsilastirma": KarsilastimaStyle().to_dict(),
    }
    return styles
