import streamlit as st
import pandas as pd
import numpy as np

# Sayfa yapılandırması
st.set_page_config(page_title="INR Simülatörü", layout="centered", page_icon="🩸")

# Başlık ve Açıklama
st.title("🩸 İğnesiz INR Ölçüm Parametreleri Simülatörü")
st.markdown("""
TÜBİTAK 2209-A projesi kapsamında **Elektroporasyon** ve **Ters İyontoforez** optimizasyonu.
Deri direncini kırma ve sinyal kalitesini izlemek için tasarlanmıştır.
""")

# Yan Panel (Kontrol Merkezi)
st.sidebar.header("⚙️ Kontrol Paneli")
st.sidebar.write("Parametreleri değiştirerek ölçümü optimize edin.")

ep_voltage = st.sidebar.slider("Elektroporasyon Voltajı (V)", 0, 120, 40)
ri_current = st.sidebar.slider("Ters İyontoforez Akımı (mA)", 0.0, 1.0, 0.2, step=0.1)
ph_calibration = st.sidebar.checkbox("pH Kalibrasyon Algoritması", value=True)

# Hesaplama Motoru
efficiency = min((ep_voltage / 100) * 55 + (ri_current) * 40, 98.0)

# Durum Kartları
col1, col2 = st.columns(2)
with col1:
    st.metric("Tahmini Verimlilik", f"%{efficiency:.1f}")
with col2:
    if ep_voltage <= 60:
        st.success("Güvenlik Durumu: ✅ Güvenli")
    else:
        st.error("Güvenlik Durumu: ⚠️ Riskli Seviye")

st.write("---")
st.subheader("📊 Gerçek Zamanlı Sinyal Analizi")

# Simülasyon Verisi
time_steps = np.arange(0, 15, 1) 
ideal_signal = 100 * (1 - np.exp(-time_steps/4)) * (efficiency/100)

# Kalibrasyon durumuna göre gürültü ayarı
noise_level = 1.5 if ph_calibration else 8.5
noise = np.random.normal(0, noise_level, len(time_steps))

# Grafik Verisi Hazırlama
chart_data = pd.DataFrame({
    "Ölçülen Ham Sinyal": ideal_signal + noise,
    "Filtrelenmiş İdeal Sinyal": ideal_signal
}, index=time_steps)

st.line_chart(chart_data)

# Bilgi Notu
st.info(f"💡 pH Kalibrasyonu sayesinde gürültü seviyesi {noise_level} değerine düşürüldü.")

st.markdown("""
---
**Proje Sahibi:** Azize Demirel  
**Kurum:** Bakırçay Üniversitesi - Biyomedikal Mühendisliği  
*TÜBİTAK 2209-A Araştırma Projesi Sunumu*
""")
