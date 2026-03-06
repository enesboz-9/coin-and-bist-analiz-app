"""
app.py — Finansal Analiz & Sinyal Terminali
Ana uygulama dosyası

Kullanım:
  streamlit run app.py

API Anahtarları:
  .streamlit/secrets.toml veya .env dosyasına ekleyin:
    GROQ_API_KEY = "..."
    GEMINI_API_KEY = "..."
    ANTHROPIC_API_KEY = "..."
"""

import sys
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import os

# Streamlit Cloud path fix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─── Sayfa Yapılandırması ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Finansal Analiz Terminali",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Modülleri İçe Aktar ─────────────────────────────────────────────────
from modules.data_fetcher import (
    hisse_verisi_cek, hisse_bilgisi_cek, haber_basliklari_cek,
    coklu_sembol_verisi_cek, BIST_SEMBOLLER, KRIPTO_SEMBOLLER, ZAMAN_DILIMLERI
)
from modules.technical_analysis import (
    tum_indiktorleri_hesapla, ozet_istatistikler,
    rsi_asiri_satis_filtrele, golden_cross_filtrele,
    yuksek_hacim_filtrele, trend_yukari_filtrele
)
from modules.ai_engine import (
    groq_teknik_analiz, gemini_temel_analiz, claude_strateji_olustur
)
from modules.visualizer import (
    ana_grafik_olustur, skor_gauge_olustur,
    coklu_skor_grafigi, indikatör_ozet_tablosu
)

# ─── Özel CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-card: #1c2030;
        --accent-green: #00ff88;
        --accent-red: #ff4466;
        --accent-amber: #ffaa00;
        --accent-blue: #00d4ff;
        --accent-purple: #7b2fff;
        --text-primary: #e6edf3;
        --text-muted: #8b949e;
        --border: #30363d;
    }
    
    .stApp {
        background-color: var(--bg-primary);
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Header Banner */
    .terminal-header {
        background: linear-gradient(135deg, #0d1117 0%, #1a1f35 50%, #0d1117 100%);
        border: 1px solid var(--border);
        border-bottom: 2px solid var(--accent-green);
        padding: 20px 30px;
        margin-bottom: 20px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .terminal-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 700;
        color: var(--accent-green);
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 0 0 20px rgba(0,255,136,0.4);
    }
    
    .terminal-subtitle {
        font-size: 13px;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1px;
    }
    
    /* Metrik Kartları */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        border-color: var(--accent-blue);
        box-shadow: 0 0 15px rgba(0,212,255,0.1);
    }
    
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: var(--text-muted);
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    /* Sinyal Rozetleri */
    .badge-al {
        background: rgba(0,255,136,0.15);
        color: #00ff88;
        border: 1px solid rgba(0,255,136,0.4);
        padding: 6px 18px;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 2px;
        display: inline-block;
    }
    
    .badge-sat {
        background: rgba(255,68,102,0.15);
        color: #ff4466;
        border: 1px solid rgba(255,68,102,0.4);
        padding: 6px 18px;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 2px;
        display: inline-block;
    }
    
    .badge-tut {
        background: rgba(255,170,0,0.15);
        color: #ffaa00;
        border: 1px solid rgba(255,170,0,0.4);
        padding: 6px 18px;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 2px;
        display: inline-block;
    }
    
    /* AI Panel */
    .ai-panel {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .ai-panel-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: var(--text-muted);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border);
    }
    
    /* Tablo Stili */
    .stDataFrame {
        background: var(--bg-card) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: var(--bg-secondary) !important;
    }
    
    /* Ticker şeridi */
    .ticker-strip {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 10px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
        margin-bottom: 16px;
    }
    
    .ticker-item { display: flex; gap: 8px; align-items: center; }
    .ticker-symbol { color: var(--text-muted); }
    .ticker-price { color: var(--text-primary); font-weight: 500; }
    .ticker-up { color: var(--accent-green); }
    .ticker-down { color: var(--accent-red); }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Genel input stili */
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }
    
    /* Tab stili */
    .stTabs [data-baseweb="tab"] {
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1px;
    }
    
    /* Bölüm başlığı */
    .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: var(--accent-blue);
        letter-spacing: 3px;
        text-transform: uppercase;
        margin: 20px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border);
    }
    
    /* Strateji kutusu */
    .strategy-box {
        background: linear-gradient(135deg, rgba(123,47,255,0.08), rgba(0,212,255,0.05));
        border: 1px solid rgba(123,47,255,0.3);
        border-left: 3px solid var(--accent-purple);
        border-radius: 8px;
        padding: 24px;
        line-height: 1.8;
        font-size: 14px;
    }
    
    /* İndikatör tablo renkleri */
    .ind-yukari { color: #00ff88; }
    .ind-asagi  { color: #ff4466; }
    .ind-notr   { color: #ffaa00; }

    /* Pulse animasyonu (canlı) */
    @keyframes pulse {
        0%  { opacity: 1; }
        50% { opacity: 0.4; }
        100%{ opacity: 1; }
    }
    .live-dot {
        width: 8px; height: 8px;
        background: var(--accent-green);
        border-radius: 50%;
        display: inline-block;
        animation: pulse 1.5s infinite;
        margin-right: 6px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)


# ─── Yardımcı Fonksiyonlar ────────────────────────────────────────────────

def sinyal_badge(sinyal: str) -> str:
    s = (sinyal or "").upper()
    css = "badge-al" if s == "AL" else "badge-sat" if s == "SAT" else "badge-tut"
    return f'<span class="{css}">{s}</span>'


def para_formatla(deger, para_birimi="TRY") -> str:
    if deger is None or deger == 0:
        return "N/A"
    if deger >= 1e12:
        return f"{deger/1e12:.2f}T {para_birimi}"
    elif deger >= 1e9:
        return f"{deger/1e9:.2f}B {para_birimi}"
    elif deger >= 1e6:
        return f"{deger/1e6:.2f}M {para_birimi}"
    return f"{deger:,.2f} {para_birimi}"


def degisim_renk(degisim: float) -> str:
    if degisim > 0:
        return f'<span class="ticker-up">▲ {degisim:.2f}%</span>'
    elif degisim < 0:
        return f'<span class="ticker-down">▼ {abs(degisim):.2f}%</span>'
    return f'<span style="color:#8b949e">── {degisim:.2f}%</span>'


# ─── SIDEBAR ──────────────────────────────────────────────────────────────

def sidebar_olustur():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:16px 0; border-bottom:1px solid #30363d; margin-bottom:20px;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:16px; color:#00ff88; letter-spacing:3px; font-weight:700;">
                📊 TERMINAL
            </div>
            <div style="font-size:11px; color:#8b949e; margin-top:4px; font-family:'JetBrains Mono',monospace;">
                v2.0 — AI-Powered
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ─── Sembol Seçimi ─────────────────────────────────────────────
        st.markdown("**🎯 Piyasa Seçimi**")
        piyasa = st.radio("", ["🇹🇷 BIST", "₿ Kripto", "✏️ Manuel"], horizontal=True, label_visibility="collapsed")
        
        if "BIST" in piyasa:
            sembol_listesi = BIST_SEMBOLLER
            varsayilan_idx = 0
        elif "Kripto" in piyasa:
            sembol_listesi = KRIPTO_SEMBOLLER
            varsayilan_idx = 0
        else:
            sembol_listesi = None
        
        if sembol_listesi:
            secilen_sembol = st.selectbox("Sembol Seç", sembol_listesi, index=varsayilan_idx)
        else:
            secilen_sembol = st.text_input("Sembol Gir (örn: AAPL, MSFT):", value="AAPL").upper().strip()
        
        st.divider()
        
        # ─── Zaman Dilimi ──────────────────────────────────────────────
        st.markdown("**⏱️ Zaman Dilimi**")
        secilen_zaman = st.selectbox("", list(ZAMAN_DILIMLERI.keys()), index=2, label_visibility="collapsed")
        
        st.divider()
        
        # ─── Filtreleme ────────────────────────────────────────────────
        st.markdown("**🔍 Hisse Tarayıcı**")
        
        tarama_piyasa = st.selectbox("Taranacak Piyasa", ["BIST", "Kripto"], key="tarama_piyasa")
        
        filtreler = st.multiselect(
            "Filtreler",
            [
                "RSI < 30 (Aşırı Satım)",
                "RSI > 70 (Aşırı Alım)",
                "Golden Cross (EMA50>200)",
                "Yüksek Hacim (>1.5x Ort.)",
                "Yükseliş Trendi",
            ],
            default=["RSI < 30 (Aşırı Satım)"],
        )
        
        if st.button("🔎 Tara", use_container_width=True):
            st.session_state["tara"] = True
            st.session_state["tarama_piyasa"] = tarama_piyasa
            st.session_state["filtreler"] = filtreler
        
        st.divider()
        
        # ─── AI Ayarları ───────────────────────────────────────────────
        st.markdown("**🤖 AI Analiz**")
        
        groq_aktif   = st.toggle("Groq (Teknik)", value=True)
        gemini_aktif = st.toggle("Gemini (Temel)", value=True)
        claude_aktif = st.toggle("Claude (Strateji)", value=True)
        
        st.divider()
        
        # ─── Son Güncelleme ─────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center; color:#8b949e; font-family:'JetBrains Mono',monospace; font-size:10px;">
            <span class="live-dot"></span> CANLI<br>
            {datetime.now().strftime('%H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
    
    return secilen_sembol, secilen_zaman, groq_aktif, gemini_aktif, claude_aktif


# ─── TARAYICI PANELİ ──────────────────────────────────────────────────────

def tarayici_goster():
    if not st.session_state.get("tara"):
        return
    
    with st.expander("🔍 TARAYICI SONUÇLARI", expanded=True):
        filtreler = st.session_state.get("filtreler", [])
        piyasa    = st.session_state.get("tarama_piyasa", "BIST")
        
        sembol_listesi = BIST_SEMBOLLER[:20] if piyasa == "BIST" else KRIPTO_SEMBOLLER[:10]
        
        with st.spinner(f"{len(sembol_listesi)} sembol taranıyor..."):
            zaman_config = ZAMAN_DILIMLERI["Günlük"]
            veri_dict = coklu_sembol_verisi_cek(
                sembol_listesi,
                period=zaman_config["period"],
                interval=zaman_config["interval"],
            )
            
            # İndikatörleri hesapla
            analiz_dict = {}
            for sembol, df in veri_dict.items():
                analiz_dict[sembol] = tum_indiktorleri_hesapla(df, "Günlük")
        
        # Filtreleme
        sonuc_semboller = set(analiz_dict.keys())
        
        if "RSI < 30 (Aşırı Satım)" in filtreler:
            sonuc_semboller &= set(rsi_asiri_satis_filtrele(analiz_dict, 30))
        if "RSI > 70 (Aşırı Alım)" in filtreler:
            asiri_alim = [s for s, df in analiz_dict.items()
                          if "rsi_14" in df.columns and pd.notna(df["rsi_14"].iloc[-1])
                          and df["rsi_14"].iloc[-1] > 70]
            sonuc_semboller &= set(asiri_alim)
        if "Golden Cross (EMA50>200)" in filtreler:
            sonuc_semboller &= set(golden_cross_filtrele(analiz_dict))
        if "Yüksek Hacim (>1.5x Ort.)" in filtreler:
            sonuc_semboller &= set(yuksek_hacim_filtrele(analiz_dict))
        if "Yükseliş Trendi" in filtreler:
            sonuc_semboller &= set(trend_yukari_filtrele(analiz_dict))
        
        if not sonuc_semboller:
            st.info("Seçilen filtreler için eşleşen sembol bulunamadı.")
            return
        
        st.success(f"✅ {len(sonuc_semboller)} sembol bulundu")
        
        # Sonuç tablosu
        satirlar = []
        skor_dict = {}
        
        for sembol in sorted(sonuc_semboller):
            df = analiz_dict[sembol]
            ist = ozet_istatistikler(df)
            son_fiyat = df["close"].iloc[-1]
            degisim = ((son_fiyat - df["close"].iloc[-2]) / df["close"].iloc[-2] * 100) if len(df) > 1 else 0
            
            skor = ist.get("teknik_skor", 50)
            skor_dict[sembol] = skor
            sinyal = "AL" if skor >= 60 else "SAT" if skor <= 40 else "TUT"
            
            satirlar.append({
                "Sembol": sembol,
                "Fiyat": f"{son_fiyat:.4f}" if son_fiyat < 1 else f"{son_fiyat:.2f}",
                "Değişim%": f"{degisim:+.2f}%",
                "RSI(14)": f"{ist.get('rsi_14', 0):.1f}",
                "ADX": f"{ist.get('adx', 0):.1f}",
                "Trend": ist.get("trend_yonu", "N/A"),
                "Skor": f"{skor:.0f}/100",
                "Sinyal": sinyal,
            })
        
        tablo_df = pd.DataFrame(satirlar)
        st.dataframe(tablo_df, use_container_width=True, hide_index=True)
        
        # Karşılaştırma grafiği
        st.plotly_chart(
            coklu_skor_grafigi(skor_dict),
            use_container_width=True,
        )
        
        st.session_state["tara"] = False


# ─── ANA İÇERİK ───────────────────────────────────────────────────────────

def ana_analiz_goster(sembol, zaman_dilimi, groq_aktif, gemini_aktif, claude_aktif):
    
    zaman_config = ZAMAN_DILIMLERI[zaman_dilimi]
    
    # ─── Veri Çekme ────────────────────────────────────────────────────
    with st.spinner(f"📡 {sembol} verisi çekiliyor..."):
        df_ham = hisse_verisi_cek(sembol, zaman_config["period"], zaman_config["interval"])
    
    if df_ham is None or df_ham.empty:
        st.error(f"❌ **{sembol}** için veri alınamadı. Sembolü kontrol edin.")
        return
    
    # ─── Teknik Analiz ─────────────────────────────────────────────────
    with st.spinner("🔧 İndikatörler hesaplanıyor..."):
        df = tum_indiktorleri_hesapla(df_ham, zaman_dilimi)
        istatistikler = ozet_istatistikler(df)
    
    son_fiyat    = df["close"].iloc[-1]
    onceki_fiyat = df["close"].iloc[-2] if len(df) > 1 else son_fiyat
    degisim      = (son_fiyat - onceki_fiyat) / onceki_fiyat * 100
    
    # ─── Başlık Bandı ───────────────────────────────────────────────────
    st.markdown(f"""
    <div class="terminal-header">
        <div>
            <div class="terminal-title">{sembol}</div>
            <div class="terminal-subtitle">{zaman_dilimi} • Veriler canlı</div>
        </div>
        <div style="margin-left:auto; text-align:right;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:28px; font-weight:700; color:{'#00ff88' if degisim >= 0 else '#ff4466'};">
                {son_fiyat:,.4f}
            </div>
            <div style="font-size:14px; color:{'#00ff88' if degisim >= 0 else '#ff4466'};">
                {'▲' if degisim >= 0 else '▼'} {abs(degisim):.2f}%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ─── Üst Metrikler ─────────────────────────────────────────────────
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    metriks = [
        (m1, "RSI (14)", f"{istatistikler.get('rsi_14', 0):.1f}",
         "#ff4466" if istatistikler.get('rsi_14', 50) > 70 else
         "#00ff88" if istatistikler.get('rsi_14', 50) < 30 else "#e6edf3"),
        
        (m2, "ADX", f"{istatistikler.get('adx', 0):.1f}",
         "#00d4ff" if istatistikler.get('adx', 0) > 25 else "#8b949e"),
        
        (m3, "MFI", f"{istatistikler.get('mfi', 0):.1f}",
         "#ff4466" if istatistikler.get('mfi', 50) > 80 else
         "#00ff88" if istatistikler.get('mfi', 50) < 20 else "#e6edf3"),
        
        (m4, "ATR%", f"{istatistikler.get('atr_pct', 0):.2f}%", "#ffaa00"),
        
        (m5, "Trend", istatistikler.get("trend_yonu", "N/A"),
         "#00ff88" if istatistikler.get("trend_yonu") == "YUKARI" else "#ff4466"),
        
        (m6, "Tek. Skor", f"{istatistikler.get('teknik_skor', 50):.0f}/100",
         "#00ff88" if istatistikler.get('teknik_skor', 50) >= 60 else
         "#ff4466" if istatistikler.get('teknik_skor', 50) <= 40 else "#ffaa00"),
    ]
    
    for col, etiket, deger, renk in metriks:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{etiket}</div>
                <div class="metric-value" style="color:{renk};">{deger}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ─── SEKMELER ─────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Grafik & Analiz",
        "🤖 AI Sinyaller",
        "📋 İndikatörler",
        "🏢 Şirket Bilgisi",
    ])
    
    # ─── TAB 1: Grafik ─────────────────────────────────────────────────
    with tab1:
        grafik = ana_grafik_olustur(df, sembol, zaman_dilimi)
        st.plotly_chart(grafik, use_container_width=True)
        
        # Hızlı istatistik tablosu
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown('<div class="section-title">📊 Fiyat İstatistikleri</div>', unsafe_allow_html=True)
            fiyat_stats = {
                "Son Kapanış": f"{son_fiyat:,.4f}",
                "Günlük Değişim": f"{degisim:+.2f}%",
                "52H Yüksek": f"{df['high'].max():,.4f}",
                "52H Düşük": f"{df['low'].min():,.4f}",
                "Ort. Hacim (20G)": f"{df['volume'].rolling(20).mean().iloc[-1]:,.0f}",
                "Son Hacim": f"{df['volume'].iloc[-1]:,.0f}",
                "Hacim / Ort.": f"{df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]:.2f}x",
            }
            for k, v in fiyat_stats.items():
                col1, col2 = st.columns([2, 1])
                col1.markdown(f"<small style='color:#8b949e;'>{k}</small>", unsafe_allow_html=True)
                col2.markdown(f"<small style='color:#e6edf3; font-family:monospace;'>{v}</small>", unsafe_allow_html=True)
        
        with col_b:
            st.markdown('<div class="section-title">📡 BB & Momentum</div>', unsafe_allow_html=True)
            bb_stats = {
                "BB Üst":     f"{df.get('bb_upper', pd.Series([None])).iloc[-1]:,.4f}" if "bb_upper" in df.columns else "N/A",
                "BB Orta":    f"{df.get('bb_mid', pd.Series([None])).iloc[-1]:,.4f}" if "bb_mid" in df.columns else "N/A",
                "BB Alt":     f"{df.get('bb_lower', pd.Series([None])).iloc[-1]:,.4f}" if "bb_lower" in df.columns else "N/A",
                "BB Width":   f"{istatistikler.get('bb_pct', 0):.4f}",
                "EMA 50":     f"{df['ema_50'].iloc[-1]:,.4f}" if "ema_50" in df.columns else "N/A",
                "EMA 200":    f"{df['ema_200'].iloc[-1]:,.4f}" if "ema_200" in df.columns else "N/A",
                "VWAP":       f"{df['vwap'].iloc[-1]:,.4f}" if "vwap" in df.columns else "N/A",
            }
            for k, v in bb_stats.items():
                col1, col2 = st.columns([2, 1])
                col1.markdown(f"<small style='color:#8b949e;'>{k}</small>", unsafe_allow_html=True)
                col2.markdown(f"<small style='color:#e6edf3; font-family:monospace;'>{v}</small>", unsafe_allow_html=True)
    
    # ─── TAB 2: AI Sinyaller ───────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">🤖 YAPAY ZEKA SİNYAL MERKEZİ</div>', unsafe_allow_html=True)
        
        col_g, col_gem, col_cl = st.columns(3)
        
        # ── Groq ──
        groq_sonuc   = {"sinyal": "—", "skor": 50, "kisa_ozet": "Devre dışı"}
        temel_sonuc  = {"temel_skor": 50, "sinyal": "—", "ozet": "Devre dışı"}
        
        with col_g:
            st.markdown("""
            <div class="ai-panel">
                <div class="ai-panel-header">⚡ GROQ — TEKNİK ANALİZ</div>
            """, unsafe_allow_html=True)
            
            if groq_aktif:
                with st.spinner("Groq analiz ediyor..."):
                    groq_sonuc = groq_teknik_analiz(sembol, istatistikler, zaman_dilimi)
                
                st.plotly_chart(
                    skor_gauge_olustur(groq_sonuc.get("skor", 50), "Teknik Skor"),
                    use_container_width=True,
                )
                
                st.markdown(sinyal_badge(groq_sonuc.get("sinyal", "TUT")), unsafe_allow_html=True)
                st.markdown(f"**Güç:** {groq_sonuc.get('guc', 'N/A')}")
                
                if groq_sonuc.get("kisa_ozet"):
                    st.info(groq_sonuc["kisa_ozet"])
                
                if groq_sonuc.get("guclu_sinyaller"):
                    st.markdown("**✅ Güçlü Sinyaller:**")
                    for s in groq_sonuc["guclu_sinyaller"]:
                        st.markdown(f"  • {s}")
                
                if groq_sonuc.get("zayif_sinyaller"):
                    st.markdown("**⚠️ Zayıf Sinyaller:**")
                    for s in groq_sonuc["zayif_sinyaller"]:
                        st.markdown(f"  • {s}")
            else:
                st.warning("Groq devre dışı")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ── Gemini ──
        with col_gem:
            st.markdown("""
            <div class="ai-panel">
                <div class="ai-panel-header">🌟 GEMINI — TEMEL ANALİZ</div>
            """, unsafe_allow_html=True)
            
            if gemini_aktif:
                with st.spinner("Şirket bilgisi ve haberler çekiliyor..."):
                    sirket_bilgisi = hisse_bilgisi_cek(sembol)
                    haberler = haber_basliklari_cek(sembol)
                
                with st.spinner("Gemini analiz ediyor..."):
                    temel_sonuc = gemini_temel_analiz(sembol, sirket_bilgisi, haberler)
                
                st.plotly_chart(
                    skor_gauge_olustur(temel_sonuc.get("temel_skor", 50), "Temel Skor"),
                    use_container_width=True,
                )
                
                st.markdown(sinyal_badge(temel_sonuc.get("sinyal", "TUT")), unsafe_allow_html=True)
                
                col_d, col_h = st.columns(2)
                col_d.metric("Değerleme", temel_sonuc.get("degerleme", "N/A"))
                col_h.metric("Duyarlılık", temel_sonuc.get("haber_duyarlilik", "N/A"))
                
                if temel_sonuc.get("ozet"):
                    st.info(temel_sonuc["ozet"])
                
                if temel_sonuc.get("guclu_yonler"):
                    st.markdown("**✅ Güçlü Yönler:**")
                    for s in temel_sonuc["guclu_yonler"]:
                        st.markdown(f"  • {s}")
                
                if temel_sonuc.get("riskler"):
                    st.markdown("**🚨 Riskler:**")
                    for r in temel_sonuc["riskler"]:
                        st.markdown(f"  • {r}")
                
                if haberler:
                    with st.expander(f"📰 Son Haberler ({len(haberler)})"):
                        for haber in haberler[:5]:
                            st.markdown(f"**[{haber['tarih']}]** {haber['baslik']}")
                            st.caption(haber['kaynak'])
                            st.divider()
            else:
                st.warning("Gemini devre dışı")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ── Bileşik Skor ──
        with col_cl:
            st.markdown("""
            <div class="ai-panel">
                <div class="ai-panel-header">⚖️ BİLEŞİK AI SKORU</div>
            """, unsafe_allow_html=True)
            
            tek_skor  = groq_sonuc.get("skor", 50)
            tem_skor  = temel_sonuc.get("temel_skor", 50)
            bil_skor  = round(tek_skor * 0.6 + tem_skor * 0.4, 1)
            
            st.plotly_chart(
                skor_gauge_olustur(bil_skor, "Bileşik Skor"),
                use_container_width=True,
            )
            
            sinyal_metni = "AL" if bil_skor >= 60 else "SAT" if bil_skor <= 40 else "TUT"
            st.markdown(sinyal_badge(sinyal_metni), unsafe_allow_html=True)
            
            st.markdown("")
            col_t, col_te = st.columns(2)
            col_t.metric("Teknik (%60)", f"{tek_skor:.0f}")
            col_te.metric("Temel (%40)", f"{tem_skor:.0f}")
            
            # Skor çubuğu
            st.progress(int(bil_skor))
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ── Claude Strateji ──
        st.markdown('<div class="section-title">🧠 CLAUDE — NİHAİ STRATEJİ RAPORU</div>', unsafe_allow_html=True)
        
        if claude_aktif:
            if st.button("🚀 Claude ile Strateji Oluştur", use_container_width=True, type="primary"):
                with st.spinner("Claude kapsamlı strateji raporu hazırlıyor... Bu 20-40 saniye sürebilir."):
                    sirket_bilgisi_cl = hisse_bilgisi_cek(sembol) if not gemini_aktif else sirket_bilgisi
                    
                    strateji = claude_strateji_olustur(
                        sembol=sembol,
                        zaman_dilimi=zaman_dilimi,
                        teknik_sonuc=groq_sonuc,
                        temel_sonuc=temel_sonuc,
                        istatistikler=istatistikler,
                        sirket_bilgisi=sirket_bilgisi_cl,
                    )
                
                st.markdown(f'<div class="strategy-box">{strateji}</div>', unsafe_allow_html=True)
        else:
            st.info("Claude API devre dışı. Sidebar'dan aktifleştirin.")
    
    # ─── TAB 3: İndikatörler ───────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">📋 KAPSAMLI İNDİKATÖR PANELİ</div>', unsafe_allow_html=True)
        
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            ozet_df = indikatör_ozet_tablosu(istatistikler)
            st.dataframe(ozet_df, use_container_width=True, hide_index=True,
                         column_config={
                             "İndikatör": st.column_config.TextColumn("İndikatör", width="medium"),
                             "Değer":     st.column_config.TextColumn("Değer",     width="small"),
                             "Yorum":     st.column_config.TextColumn("Yorum",     width="medium"),
                         })
        
        with col_i2:
            st.markdown("**Ichimoku Bulutu**")
            ich_data = {}
            for col_name, display_name in [
                ("ich_tenkan", "Tenkan-sen (9)"),
                ("ich_kijun",  "Kijun-sen (26)"),
                ("ich_spanA",  "Senkou Span A"),
                ("ich_spanB",  "Senkou Span B"),
            ]:
                if col_name in df.columns:
                    val = df[col_name].iloc[-1]
                    ich_data[display_name] = f"{val:,.4f}" if pd.notna(val) else "N/A"
                    col1, col2 = st.columns([2, 1])
                    col1.markdown(f"<small style='color:#8b949e;'>{display_name}</small>", unsafe_allow_html=True)
                    col2.markdown(f"<small style='color:#e6edf3; font-family:monospace;'>{ich_data[display_name]}</small>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("**Hacim Analizi**")
            obv_val = istatistikler.get("obv", 0)
            cmf_val = istatistikler.get("cmf", 0)
            
            st.metric("OBV", f"{obv_val:,.0f}" if obv_val else "N/A")
            st.metric("CMF", f"{cmf_val:.4f}" if cmf_val else "N/A",
                      delta="Para Girişi" if cmf_val and cmf_val > 0 else "Para Çıkışı")
            
            son_hacim = df["volume"].iloc[-1]
            ort_hacim = df["volume"].rolling(20).mean().iloc[-1]
            
            st.metric("Hacim/Ortalama", f"{son_hacim/ort_hacim:.2f}x",
                      delta="Yüksek" if son_hacim > ort_hacim * 1.5 else "Normal")
        
        # Ham veri
        with st.expander("📊 Ham Veri (Son 50 Bar)"):
            st.dataframe(df.tail(50)[[
                "open", "high", "low", "close", "volume",
                "ema_50", "ema_200", "rsi_14", "macd", "macd_signal",
                "stoch_k", "adx", "atr", "bb_upper", "bb_lower",
                "teknik_skor"
            ]].round(4), use_container_width=True)
    
    # ─── TAB 4: Şirket Bilgisi ─────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">🏢 ŞİRKET PROFİLİ</div>', unsafe_allow_html=True)
        
        with st.spinner("Şirket bilgisi yükleniyor..."):
            bilgi = hisse_bilgisi_cek(sembol)
        
        if "hata" in bilgi:
            st.error(f"Şirket bilgisi alınamadı: {bilgi['hata']}")
        else:
            col_b1, col_b2, col_b3 = st.columns(3)
            
            with col_b1:
                st.markdown(f"**{bilgi.get('ad', sembol)}**")
                st.caption(f"Sektör: {bilgi.get('sektor', 'N/A')}")
                st.caption(f"Sanayi: {bilgi.get('sanayi', 'N/A')}")
                if bilgi.get("web"):
                    st.caption(f"[Website]({bilgi['web']})")
            
            with col_b2:
                st.metric("Piyasa Değeri", para_formatla(bilgi.get("piyasa_degeri"), bilgi.get("para_birimi", "")))
                st.metric("F/K Oranı", f"{bilgi.get('pe_orani', 'N/A'):.2f}" if bilgi.get("pe_orani") else "N/A")
                st.metric("F/DD Oranı", f"{bilgi.get('pb_orani', 'N/A'):.2f}" if bilgi.get("pb_orani") else "N/A")
            
            with col_b3:
                st.metric("Beta", f"{bilgi.get('beta', 'N/A'):.2f}" if bilgi.get("beta") else "N/A")
                st.metric("EPS", f"{bilgi.get('eps', 'N/A'):.4f}" if bilgi.get("eps") else "N/A")
                temettü = bilgi.get("temettü")
                st.metric("Temettü Verimi", f"{temettü*100:.2f}%" if temettü else "N/A")
            
            if bilgi.get("aciklama"):
                with st.expander("📝 Şirket Hakkında"):
                    st.write(bilgi["aciklama"])
        
        # Haberler
        st.markdown('<div class="section-title">📰 SON HABERLER</div>', unsafe_allow_html=True)
        
        haberler_tab = haber_basliklari_cek(sembol)
        if haberler_tab:
            for h in haberler_tab:
                col_haber_a, col_haber_b = st.columns([4, 1])
                with col_haber_a:
                    if h.get("link"):
                        st.markdown(f"**[{h['baslik']}]({h['link']})**")
                    else:
                        st.markdown(f"**{h['baslik']}**")
                with col_haber_b:
                    st.caption(h.get("tarih", ""))
                st.caption(f"📌 {h.get('kaynak', '')}")
                st.divider()
        else:
            st.info("Bu sembol için haber bulunamadı.")


# ─── ANA PROGRAM ──────────────────────────────────────────────────────────

def main():
    # Header
    st.markdown("""
    <div style="text-align:center; padding:8px; background:linear-gradient(90deg,#0d1117,#1a1f35,#0d1117); 
         border-bottom:1px solid #30363d; margin-bottom:0; font-family:'JetBrains Mono',monospace;
         font-size:11px; color:#8b949e; letter-spacing:3px;">
        <span class="live-dot"></span>
        FİNANSAL ANALİZ & SİNYAL TERMİNALİ &nbsp;|&nbsp; GROQ + GEMİNİ + CLAUDE &nbsp;|&nbsp; BIST + KRİPTO
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    sembol, zaman_dilimi, groq_aktif, gemini_aktif, claude_aktif = sidebar_olustur()
    
    # Tarayıcı paneli (sidebar'dan tetiklenirse)
    tarayici_goster()
    
    # Ana analiz
    if sembol:
        ana_analiz_goster(sembol, zaman_dilimi, groq_aktif, gemini_aktif, claude_aktif)
    else:
        st.info("Lütfen sol menüden bir sembol seçin veya girin.")


if __name__ == "__main__":
    main()
