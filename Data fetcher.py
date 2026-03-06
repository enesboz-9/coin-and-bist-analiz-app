"""
modules/data_fetcher.py
Veri çekme modülü: yfinance üzerinden BIST ve Kripto verileri
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from typing import Optional, Dict, Tuple

# ─── Sabitler ──────────────────────────────────────────────────────────────
BIST_SEMBOLLER = [
    "THYAO.IS", "GARAN.IS", "EREGL.IS", "SISE.IS", "AKBNK.IS",
    "KCHOL.IS", "BIMAS.IS", "PGSUS.IS", "TUPRS.IS", "TOASO.IS",
    "SAHOL.IS", "YKBNK.IS", "HALKB.IS", "ISCTR.IS", "VAKBN.IS",
    "ASELS.IS", "FROTO.IS", "TAVHL.IS", "EKGYO.IS", "ARCLK.IS",
    "KOZAL.IS", "KORDS.IS", "MGROS.IS", "SOKM.IS", "TCELL.IS",
    "TTKOM.IS", "DOHOL.IS", "ENKAI.IS", "OTKAR.IS", "ULKER.IS",
]

KRIPTO_SEMBOLLER = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "AVAX-USD", "DOT-USD", "MATIC-USD", "LINK-USD",
    "ATOM-USD", "NEAR-USD", "LTC-USD", "BCH-USD", "UNI-USD",
]

ZAMAN_DILIMLERI = {
    "1 Saatlik": {"period": "60d", "interval": "1h"},
    "4 Saatlik": {"period": "60d", "interval": "4h"},  
    "Günlük":    {"period": "1y",  "interval": "1d"},
    "Haftalık":  {"period": "5y",  "interval": "1wk"},
}


# ─── Veri Çekme Fonksiyonları ───────────────────────────────────────────────

@st.cache_data(ttl=300)  # 5 dakika cache
def hisse_verisi_cek(sembol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
    """yfinance üzerinden OHLCV verisi çeker."""
    try:
        ticker = yf.Ticker(sembol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return None
        
        # Sütun isimlerini standartlaştır
        df.columns = [c.lower() for c in df.columns]
        df.index.name = "datetime"
        
        # NaN satırlarını temizle
        df.dropna(subset=["open", "high", "low", "close", "volume"], inplace=True)
        
        return df
    
    except Exception as e:
        st.error(f"Veri çekme hatası ({sembol}): {str(e)}")
        return None


@st.cache_data(ttl=300)
def hisse_bilgisi_cek(sembol: str) -> Dict:
    """Şirket temel bilgilerini çeker."""
    try:
        ticker = yf.Ticker(sembol)
        info = ticker.info
        
        return {
            "ad": info.get("longName", info.get("shortName", sembol)),
            "sektor": info.get("sector", "Bilinmiyor"),
            "sanayi": info.get("industry", "Bilinmiyor"),
            "piyasa_degeri": info.get("marketCap", 0),
            "pe_orani": info.get("trailingPE", None),
            "pb_orani": info.get("priceToBook", None),
            "eps": info.get("trailingEps", None),
            "temettü": info.get("dividendYield", None),
            "52h_yuksek": info.get("fiftyTwoWeekHigh", None),
            "52h_dusuk": info.get("fiftyTwoWeekLow", None),
            "ortalama_hacim": info.get("averageVolume", None),
            "beta": info.get("beta", None),
            "aciklama": info.get("longBusinessSummary", ""),
            "web": info.get("website", ""),
            "para_birimi": info.get("currency", "TRY" if ".IS" in sembol else "USD"),
        }
    
    except Exception as e:
        return {"ad": sembol, "hata": str(e)}


@st.cache_data(ttl=1800)  # 30 dakika cache
def haber_basliklari_cek(sembol: str) -> list:
    """yfinance üzerinden haber başlıklarını çeker."""
    try:
        ticker = yf.Ticker(sembol)
        haberler = ticker.news
        
        if not haberler:
            return []
        
        sonuc = []
        for haber in haberler[:10]:  # İlk 10 haber
            sonuc.append({
                "baslik": haber.get("title", ""),
                "kaynak": haber.get("publisher", ""),
                "link": haber.get("link", ""),
                "tarih": datetime.fromtimestamp(haber.get("providerPublishTime", 0)).strftime("%Y-%m-%d %H:%M"),
            })
        
        return sonuc
    
    except Exception as e:
        return []


def coklu_sembol_verisi_cek(semboller: list, period: str = "1y", interval: str = "1d") -> Dict[str, pd.DataFrame]:
    """Birden fazla sembol için veri çeker."""
    sonuclar = {}
    
    for sembol in semboller:
        df = hisse_verisi_cek(sembol, period, interval)
        if df is not None and not df.empty:
            sonuclar[sembol] = df
    
    return sonuclar


def anlık_fiyat_cek(semboller: list) -> Dict[str, Dict]:
    """Anlık fiyat bilgisi çeker."""
    try:
        data = yf.download(semboller, period="2d", interval="1d", progress=False)
        
        sonuclar = {}
        for sembol in semboller:
            try:
                ticker = yf.Ticker(sembol)
                info = ticker.fast_info
                sonuclar[sembol] = {
                    "son_fiyat": info.last_price,
                    "önceki_kapanis": info.previous_close,
                    "degisim": ((info.last_price - info.previous_close) / info.previous_close * 100) if info.previous_close else 0,
                }
            except:
                pass
        
        return sonuclar
    
    except Exception as e:
        return {}


def sembol_dogrula(sembol: str) -> bool:
    """Sembolün geçerli olup olmadığını kontrol eder."""
    try:
        ticker = yf.Ticker(sembol)
        df = ticker.history(period="5d", interval="1d")
        return not df.empty
    except:
        return False
