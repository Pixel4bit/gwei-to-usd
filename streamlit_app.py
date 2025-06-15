import streamlit as st
import requests

# --- Conversion Functions (reused from original script) ---

@st.cache_data(ttl=3600) # Cache results for 1 hour to avoid excessive API calls
def get_eth_price_usd():
    """Fetches the real-time price of Ethereum (ETH) in USD from CoinGecko API."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()['ethereum']['usd']
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch ETH price automatically: {e}")
        return None

@st.cache_data(ttl=3600) # Cache results for 1 hour
def get_btc_price_usd():
    """Fetches the real-time price of Bitcoin (BTC) in USD from CoinGecko API."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['bitcoin']['usd']
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch BTC price automatically: {e}")
        return None

def gwei_to_eth(gwei):
    """Converts Gwei to Ethereum."""
    return gwei / 1_000_000_000

def sats_to_btc(sats):
    """Converts Satoshis to Bitcoin."""
    return sats / 100_000_000

# --- Streamlit Application Layout ---

st.set_page_config(layout="centered", page_title="Blockchain Gas Fee Converter", page_icon="⛽")

st.title("⛽ Blockchain Gas Fee Converter")
st.markdown("Convert between Gwei, Satoshis, USD, and IDR.")

default_usd_to_idr = 16200

# Initialize session state variables if not already present
if 'selected_conversion' not in st.session_state:
    st.session_state.selected_conversion = 'Gwei to USD/IDR'
if 'eth_price' not in st.session_state:
    st.session_state.eth_price = None
if 'btc_price' not in st.session_state:
    st.session_state.btc_price = None
if 'usd_to_idr_rate' not in st.session_state:
    st.session_state.usd_to_idr_rate = float(default_usd_to_idr) # Initialize with default as float
if 'gwei_input_val' not in st.session_state:
    st.session_state.gwei_input_val = 0.0
if 'sats_input_val' not in st.session_state:
    st.session_state.sats_input_val = 0.0

# Main conversion selection
st.session_state.selected_conversion = st.radio(
    "Choose Conversion Type:",
    ('Gwei to USD/IDR', 'Sats to USD/IDR', 'Sats/Gwei Conversion'),
    index=['Gwei to USD/IDR', 'Sats to USD/IDR', 'Sats/Gwei Conversion'].index(st.session_state.selected_conversion)
)

# --- Gwei to USD/IDR Conversion ---
if st.session_state.selected_conversion == 'Gwei to USD/IDR':
    st.header("Gwei to USD/IDR")

    with st.form("gwei_to_usd_form"):
        # ETH Price Input
        st.markdown("**ETH Price (USD)**")
        auto_eth_price = get_eth_price_usd()
        
        if auto_eth_price is not None:
            st.session_state.eth_price = st.number_input(
                "Real-time ETH Price:",
                value=float(auto_eth_price),
                format="%.2f",
                key="gwei_eth_price_auto",
                help="Automatically fetched ETH price. You can edit this if needed."
            )
        else:
            st.session_state.eth_price = st.number_input(
                "Enter ETH Price (USD) manually:",
                min_value=0.01,
                value=st.session_state.eth_price if st.session_state.eth_price is not None else 2000.00, # Default if auto fails
                format="%.2f",
                key="gwei_eth_price_manual",
                help="Failed to fetch real-time ETH price. Please enter manually."
            )

        # USD to IDR Rate Input (Revised)
        st.markdown("**USD to IDR Exchange Rate**")
        st.session_state.usd_to_idr_rate = st.number_input(
            "Enter USD to IDR Rate:",
            min_value=1.0,
            value=float(st.session_state.usd_to_idr_rate), # Use current session state value or default
            format="%.2f",
            key="gwei_usd_idr_manual",
            help=f"Default: {default_usd_to_idr:,.2f}. You can change this."
        )

        # Gwei Input
        st.session_state.gwei_input_val = st.number_input(
            "Enter Gwei Amount:",
            min_value=0.0,
            value=st.session_state.gwei_input_val,
            format="%.9f",
            key="gwei_amount_input"
        )
        
        submit_button = st.form_submit_button(label="Convert Gwei")

        if submit_button:
            if st.session_state.eth_price is None or st.session_state.eth_price <= 0:
                st.error("Please provide a valid ETH price (must be greater than 0).")
            elif st.session_state.gwei_input_val <= 0:
                st.error("Gwei amount must be greater than 0.")
            else:
                eth_amount = gwei_to_eth(st.session_state.gwei_input_val)
                usd_val = eth_amount * st.session_state.eth_price
                idr_val = usd_val * st.session_state.usd_to_idr_rate

                st.success(f"{st.session_state.gwei_input_val} Gwei = {eth_amount:.9f} ETH")
                st.info(f"Equivalent: **${usd_val:.6f} USD**")
                st.info(f"Equivalent: **Rp{idr_val:,.2f} IDR**")


# --- Sats to USD/IDR Conversion ---
elif st.session_state.selected_conversion == 'Sats to USD/IDR':
    st.header("Sats to USD/IDR")

    with st.form("sats_to_usd_form"):
        # BTC Price Input
        st.markdown("**BTC Price (USD)**")
        auto_btc_price = get_btc_price_usd()

        if auto_btc_price is not None:
            st.session_state.btc_price = st.number_input(
                "Real-time BTC Price:",
                value=float(auto_btc_price),
                format="%.2f",
                key="sats_btc_price_auto",
                help="Automatically fetched BTC price. You can edit this if needed."
            )
        else:
            st.session_state.btc_price = st.number_input(
                "Enter BTC Price (USD) manually:",
                min_value=0.01,
                value=st.session_state.btc_price if st.session_state.btc_price is not None else 30000.00, # Default if auto fails
                format="%.2f",
                key="sats_btc_price_manual",
                help="Failed to fetch real-time BTC price. Please enter manually."
            )
        
        # USD to IDR Rate Input (Revised)
        st.markdown("**USD to IDR Exchange Rate**")
        st.session_state.usd_to_idr_rate = st.number_input(
            "Enter USD to IDR Rate:",
            min_value=1.0,
            value=float(st.session_state.usd_to_idr_rate), # Use current session state value or default
            format="%.2f",
            key="sats_usd_idr_manual",
            help=f"Default: {default_usd_to_idr:,.2f}. You can change this."
        )

        # Sats Input
        st.session_state.sats_input_val = st.number_input(
            "Enter Satoshis Amount:",
            min_value=0.0,
            value=st.session_state.sats_input_val,
            format="%.0f", # Sats are usually integer, but for display might allow float
            key="sats_amount_input"
        )
        
        submit_button = st.form_submit_button(label="Convert Satoshis")

        if submit_button:
            if st.session_state.btc_price is None or st.session_state.btc_price <= 0:
                st.error("Please provide a valid BTC price (must be greater than 0).")
            elif st.session_state.sats_input_val <= 0:
                st.error("Satoshis amount must be greater than 0.")
            else:
                btc_amount = sats_to_btc(st.session_state.sats_input_val)
                usd_val = btc_amount * st.session_state.btc_price
                idr_val = usd_val * st.session_state.usd_to_idr_rate

                st.success(f"{st.session_state.sats_input_val} Satoshis = {btc_amount:.8f} BTC")
                st.info(f"Equivalent: **${usd_val:.6f} USD**")
                st.info(f"Equivalent: **Rp{idr_val:,.2f} IDR**")


# --- Sats/Gwei Conversion ---
elif st.session_state.selected_conversion == 'Sats/Gwei Conversion':
    st.header("Sats/Gwei Cross Conversion")

    with st.form("sats_gwei_cross_form"):
        # BTC Price Input (auto then manual)
        st.markdown("**BTC Price (USD)**")
        auto_btc_price = get_btc_price_usd()
        if auto_btc_price is not None:
            st.session_state.btc_price = st.number_input(
                "Real-time BTC Price:",
                value=float(auto_btc_price),
                format="%.2f",
                key="cross_btc_price_auto",
                help="Automatically fetched BTC price. You can edit this if needed."
            )
        else:
            st.session_state.btc_price = st.number_input(
                "Enter BTC Price (USD) manually:",
                min_value=0.01,
                value=st.session_state.btc_price if st.session_state.btc_price is not None else 30000.00,
                format="%.2f",
                key="cross_btc_price_manual",
                help="Failed to fetch real-time BTC price. Please enter manually."
            )

        # ETH Price Input (auto then manual)
        st.markdown("**ETH Price (USD)**")
        auto_eth_price = get_eth_price_usd()
        if auto_eth_price is not None:
            st.session_state.eth_price = st.number_input(
                "Real-time ETH Price:",
                value=float(auto_eth_price),
                format="%.2f",
                key="cross_eth_price_auto",
                help="Automatically fetched ETH price. You can edit this if needed."
            )
        else:
            st.session_state.eth_price = st.number_input(
                "Enter ETH Price (USD) manually:",
                min_value=0.01,
                value=st.session_state.eth_price if st.session_state.eth_price is not None else 2000.00,
                format="%.2f",
                key="cross_eth_price_manual",
                help="Failed to fetch real-time ETH price. Please enter manually."
            )
        
        # USD to IDR Rate Input (Revised)
        st.markdown("**USD to IDR Exchange Rate**")
        st.session_state.usd_to_idr_rate = st.number_input(
            "Enter USD to IDR Rate:",
            min_value=1.0,
            value=float(st.session_state.usd_to_idr_rate), # Use current session state value or default
            format="%.2f",
            key="cross_usd_idr_manual",
            help=f"Default: {default_usd_to_idr:,.2f}. You can change this."
        )
                
        # Conversion Direction
        conversion_direction = st.radio(
            "Convert from:",
            ('Satoshis (Sats)', 'Gwei'),
            key="cross_conversion_direction"
        )
        
        # Input based on direction
        if conversion_direction == 'Satoshis (Sats)':
            st.session_state.sats_input_val = st.number_input(
                "Enter Satoshis Amount:",
                min_value=0.0,
                value=st.session_state.sats_input_val,
                format="%.0f",
                key="cross_sats_input"
            )
            submit_button = st.form_submit_button(label="Convert Sats to Gwei")
            
            if submit_button:
                if (st.session_state.btc_price is None or st.session_state.btc_price <= 0) or \
                   (st.session_state.eth_price is None or st.session_state.eth_price <= 0):
                    st.error("Please provide valid BTC and ETH prices (must be greater than 0).")
                elif st.session_state.sats_input_val <= 0:
                    st.error("Satoshis amount must be greater than 0.")
                else:
                    try:
                        btc_amount = sats_to_btc(st.session_state.sats_input_val)
                        usd_from_sats = btc_amount * st.session_state.btc_price
                        idr_from_sats = usd_from_sats * st.session_state.usd_to_idr_rate

                        eth_from_usd = usd_from_sats / st.session_state.eth_price
                        gwei_equivalent = eth_from_usd * 1_000_000_000

                        st.success(f"{st.session_state.sats_input_val} Satoshis = ${usd_from_sats:.6f} USD = Rp{idr_from_sats:,.2f} IDR")
                        st.info(f"Equivalent: **{gwei_equivalent:.2f} Gwei**")
                    except ZeroDivisionError:
                        st.error("ETH price cannot be zero for this conversion.")

        elif conversion_direction == 'Gwei':
            st.session_state.gwei_input_val = st.number_input(
                "Enter Gwei Amount:",
                min_value=0.0,
                value=st.session_state.gwei_input_val,
                format="%.9f",
                key="cross_gwei_input"
            )
            submit_button = st.form_submit_button(label="Convert Gwei to Sats")

            if submit_button:
                if (st.session_state.btc_price is None or st.session_state.btc_price <= 0) or \
                   (st.session_state.eth_price is None or st.session_state.eth_price <= 0):
                    st.error("Please provide valid BTC and ETH prices (must be greater than 0).")
                elif st.session_state.gwei_input_val <= 0:
                    st.error("Gwei amount must be greater than 0.")
                else:
                    try:
                        eth_amount = gwei_to_eth(st.session_state.gwei_input_val)
                        usd_from_gwei = eth_amount * st.session_state.eth_price
                        idr_from_gwei = usd_from_gwei * st.session_state.usd_to_idr_rate

                        btc_from_usd = usd_from_gwei / st.session_state.btc_price
                        sats_equivalent = btc_from_usd * 100_000_000

                        st.success(f"{st.session_state.gwei_input_val} Gwei = ${usd_from_gwei:.6f} USD = Rp{idr_from_gwei:,.2f} IDR")
                        st.info(f"Equivalent: **{sats_equivalent:.4f} Satoshis**") # Retain .4f for Sats
                    except ZeroDivisionError:
                        st.error("BTC price cannot be zero for this conversion.")
