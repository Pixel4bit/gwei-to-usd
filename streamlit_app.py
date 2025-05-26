import streamlit as st
import requests

def get_eth_price_usd():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['ethereum']['usd']
    except:
        return None

def gwei_to_eth(gwei):
    return gwei / 1_000_000_000

st.set_page_config(page_title="Gwei Converter", page_icon="⛽")
st.title("⛽ Konversi Gwei ke USD dan IDR")

# Pilih harga ETH
eth_price_option = st.radio("Gunakan harga ETH:", ("Real-time", "Manual"))
if eth_price_option == "Real-time":
    eth_price = get_eth_price_usd()
    if eth_price is None:
        st.error("❌ Gagal mengambil harga ETH real-time.")
        st.stop()
    else:
        st.success(f"Harga ETH real-time: ${eth_price}")
else:
    eth_price = st.number_input("Masukkan harga ETH manual (USD):", min_value=0.0, value=2500.0)

# Pilih kurs USD ke IDR
kurs_option = st.radio("Pilih kurs USD ke IDR:", ("Default (16.200)", "Manual"))
if kurs_option == "Default (16.200)":
    usd_to_idr = 16200
else:
    usd_to_idr = st.number_input("Masukkan kurs manual USD ke IDR:", min_value=0.0, value=16200.0)

# Input Gwei
gwei = st.number_input("Masukkan jumlah Gwei:", min_value=0.0, value=100.0)

# Konversi
eth_amount = gwei_to_eth(gwei)
usd = eth_amount * eth_price
idr = usd * usd_to_idr

# Output
st.markdown("### 💹 Hasil Konversi")
st.write(f"{gwei} Gwei = **{eth_amount:.9f} ETH** = **${usd:.6f} USD** = **Rp{idr:,.2f} IDR**")