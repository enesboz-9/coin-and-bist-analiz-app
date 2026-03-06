# 📊 Finansal Analiz & Sinyal Terminali

> BIST ve Kripto piyasaları için **Groq + Gemini + Claude** destekli AI analiz platformu.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 🗂️ Repo Yapısı

```
├── app.py                    # Ana uygulama girişi
├── requirements.txt          # Python bağımlılıkları
├── packages.txt              # Sistem bağımlılıkları
├── .gitignore
├── .streamlit/
│   └── config.toml           # Tema ve sunucu ayarları
└── modules/
    ├── __init__.py
    ├── data_fetcher.py       # yfinance veri modülü
    ├── technical_analysis.py # 25+ teknik indikatör
    ├── ai_engine.py          # Groq + Gemini + Claude
    └── visualizer.py         # Plotly grafikleri
```

---

## 🚀 Streamlit Cloud'a Deploy

### Adım 1 — Bu repoyu fork veya clone et
```bash
git clone https://github.com/KULLANICI_ADI/REPO_ADI.git
cd REPO_ADI
```

### Adım 2 — [share.streamlit.io](https://share.streamlit.io) adresine git
1. GitHub hesabınla giriş yap
2. **"New app"** butonuna tıkla
3. Repo, branch (`main`) ve dosya (`app.py`) seç
4. **"Advanced settings"** → **"Secrets"** bölümüne API anahtarlarını ekle:

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"
GEMINI_API_KEY = "AIzaSyxxxxxxxxxxxxxxxxx"
ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxxxxx"
```

5. **"Deploy!"** butonuna tıkla ✅

---

## 🔑 API Anahtarları — Nereden Alınır?

| Servis | Ücretsiz | Link |
|--------|----------|------|
| **Groq** | ✅ Ücretsiz + hızlı | [console.groq.com](https://console.groq.com) |
| **Gemini** | ✅ Ücretsiz tier | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Claude** | ✅ $5 kredi ile başla | [console.anthropic.com](https://console.anthropic.com) |

---

## 🤖 AI Mimarisi

```
Piyasa Verisi (yfinance)
        ↓
Teknik Analiz (pandas_ta — 25+ indikatör)
        ↓
    ┌───────────────────────────────┐
    │  GROQ (llama-3.3-70b)        │  → Teknik Skor (0-100)
    │  Hızlı teknik değerlendirme  │
    └───────────────────────────────┘
    ┌───────────────────────────────┐
    │  GEMINI (gemini-1.5-flash)   │  → Temel Skor (0-100)
    │  Haber + fundamentals analiz │
    └───────────────────────────────┘
                ↓
    ┌───────────────────────────────┐
    │  CLAUDE (claude-sonnet)      │  → Nihai Strateji Raporu
    │  Birleşik karar + risk       │
    └───────────────────────────────┘
```

---

## 📐 İndikatörler

| Kategori | İndikatörler |
|----------|-------------|
| **Trend** | EMA 9/21/50/100/200, SMA 20/50/200, MACD, Ichimoku, PSAR, Golden/Death Cross |
| **Momentum** | RSI (9+14), Stochastic K/D, StochRSI, Williams %R, CCI, ROC, Momentum |
| **Volatilite** | Bollinger Bantları, ATR & ATR%, Keltner Kanalları, BB Squeeze |
| **Hacim** | VWAP, OBV, MFI, CMF, VWMA |
| **Trend Gücü** | ADX, +DI, -DI |

---

## ⚠️ Yasal Uyarı

Bu uygulama yatırım tavsiyesi değildir. Tüm yatırım kararları için profesyonel mali danışmana başvurun.
