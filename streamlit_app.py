import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go # Daha profesyonel grafikler için

# Sayfa yapılandırması (Geniş mod)
st.set_page_config(page_title="Gelişmiş INR Biyosensör Simülatörü", layout="wide", page_icon="🔬")

# --- BAŞLIK BÖLÜMÜ ---
st.title("🔬 Gelişmiş İğnesiz INR Biyosensör Parametreleri Simülatörü")
st.markdown("""
TÜBİTAK 2209-A Projesi: **Aptamer Tabanlı Empedansmetrik ve İyontoforetik INR Ölçüm Sistemi**.
Bu arayüz, biyosensörün farklı fizyolojik ve elektriksel parametreler altındaki performansını simüle eder.
""")
st.write("---")

# --- YAN PANEL (GİRDİLER) ---
st.sidebar.header("⚙️ Sistem Parametreleri")

# 1. Biyolojik Parametreler
st.sidebar.subheader("🩸 Kan Parametreleri")
target_inr = st.sidebar.slider("Hedef INR Değeri", 0.8, 5.0, 2.5, step=0.1, help="Hastanın gerçek kan INR değeri.")
hematocrit = st.sidebar.slider("Hematokrit (%)", 30, 55, 42, help="Kanın şekilli eleman oranı (sinyal gürültüsünü etkiler).")

# 2. Sensör Parametreleri
st.sidebar.subheader("🔬 Sensör Arayüzü")
aptamer_density = st.sidebar.slider("Aptamer Yüzey Yoğunluğu (%)", 0, 100, 80, help="Elektrot yüzeyindeki aktif aptamer oranı.")
incubation_time = st.sidebar.slider("İnkübasyon Süresi (sn)", 10, 300, 60, help="Kanın sensörle temas süresi.")

# 3. Elektriksel Parametreler
st.sidebar.subheader("⚡ Elektriksel Uyarım")
ri_current_input = st.sidebar.slider("Ters İyontoforez Akımı (µA)", 0, 1000, 200, step=10, help="Molekülleri çekmek için uygulanan akım.")
eis_frequency = st.sidebar.select_slider("EIS Frekansı (Hz)", options=[1, 10, 100, 1000, 10000], value=100, help="Empedans ölçüm frekansı.")

# --- HESAPLAMA MOTORU (Fiziksel Modellere Dayalı Simülasyon) ---

# 1. Empedans Modelleme (Aptamer-Trombin Etkileşimi)
# INR arttıkça trombin artar, aptamerlere daha çok bağlanır, empedans (Rct) artar.
base_resistance = 1000 # Ohm
impedance_increase = target_inr * (aptamer_density / 100) * 500 # INR başına direnç artışı
noise_hematocrit = (hematocrit - 42) * 10 # Hematokrit sapma gürültüsü
total_impedance = base_resistance + impedance_increase + noise_hematocrit + np.random.normal(0, 50)

# 2. Akım Modelleme (Ters İyontoforez Verimliliği)
# Uygulanan akım artarsa çekilen molekül artar, ancak doyuma ulaşır.
ionto_efficiency = 0.6 # Baz verimlilik
current_signal = (ri_current_input * ionto_efficiency) * (1 - np.exp(-incubation_time/100)) + np.random.normal(0, 10)

# 3. SNR (Sinyal-Gürültü Oranı) Hesaplaması
# Sinyal: total_impedance, Gürültü: Hematokrit ve ortam bazlı
signal_power = total_impedance
noise_power = 100 + abs(noise_hematocrit)
snr_db = 10 * np.log10(signal_power / noise_power) if signal_power > 0 else 0

# --- ANA PANEL (GÖSTERGELER VE GRAFİKLER) ---

# 1. Özet Metrikler
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Ölçülen Toplam Empedans (Z)", value=f"{total_impedance:.1f} Ω", delta=f"{impedance_increase:.1f} Ω (Aptamer Etkisi)")
col2.metric(label="Çekilen İyontoforetik Akım", value=f"{current_signal:.1f} µA")
col3.metric(label="Sinyal-Gürültü Oranı (SNR)", value=f"{snr_db:.1f} dB", help=">20 dB ideal kabul edilir.")
col4.metric(label="Sistem Durumu", value="✅ Kararlı" if snr_db > 15 else "⚠️ Düşük SNR")

st.write("---")

# 2. Canlı Grafikler Bölümü
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 Zamanla Empedans Değişimi (İnkübasyon)")
    # Zaman serisi verisi oluşturma
    time_arr = np.linspace(0, incubation_time, 50)
    # Aptamer bağlanma kinetiği (üstel artış)
    z_t = base_resistance + impedance_increase * (1 - np.exp(-time_arr / (30 + noise_hematocrit/10)))
    # Gürültü ekleme
    z_t_noisy = z_t + np.random.normal(0, 15, len(time_arr))
    
    # Plotly ile grafik
    fig_z = go.Figure()
    fig_z.add_trace(go.Scatter(x=time_arr, y=z_t_noisy, mode='lines+markers', name='Ham Veri', line=dict(color='#FF4B4B', width=1)))
    fig_z.add_trace(go.Scatter(x=time_arr, y=z_t, mode='lines', name='Filtrelenmiş Trend', line=dict(color='white', width=2, dash='dash')))
    fig_z.update_layout(title="Aptamer-Hedef Bağlanma Kinetiği", xaxis_title="Zaman (sn)", yaxis_title="Empedans (Ω)", template="plotly_dark", height=400)
    st.plotly_chart(fig_z, use_container_width=True)

with col_chart2:
    st.subheader("📡 Frekans Analizi ve SNR Modu")
    
    # Frekans spektrumu verisi
    frequencies = [1, 10, 100, 1000, 10000]
    # Frekans arttıkça empedans düşer (tipik EIS davranışı)
    z_freq = total_impedance / (1 + (np.array(frequencies) / eis_frequency)**0.5)
    
    # SNR Görselleştirmesi
    fig_snr = go.Figure()
    fig_snr.add_trace(go.Bar(x=frequencies, y=z_freq, name='Sinyal Gücü', marker_color='#00CC96'))
    fig_snr.add_trace(go.Scatter(x=frequencies, y=[noise_power]*len(frequencies), mode='lines', name='Gürültü Tabanı', line=dict(color='#EF553B', width=2, dash='dot')))
    
    fig_snr.update_layout(title="EIS Frekans Spektrumu ve Gürültü Seviyesi", xaxis_title="Frekans (Hz)", yaxis_title="Genlik", xaxis_type="log", template="plotly_dark", height=400)
    st.plotly_chart(fig_snr, use_container_width=True)

# --- ALT BİLGİ ---
st.write("---")
st.markdown(f"""
**Teknik Analiz Notu:** Şu anki simülasyonda, **INR {target_inr}** ve **Aptamer Yoğunluğu %{aptamer_density}** iken, sistem **{eis_frequency} Hz** frekansta **{snr_db:.1f} dB** SNR ile çalışmaktadır. 
Hematokritin %{hematocrit} olması, sinyal gürültü tabanını {noise_power:.1f} Ω seviyesine çekmiştir.
""")