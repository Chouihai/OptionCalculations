import streamlit as st
from mvp import black_scholes as bs


def show_pricing_page():
    st.markdown('<h1 class="main-header">Option Pricing Calculator</h1>', unsafe_allow_html=True)
    
    # Create two columns: parameters (1/3) and results (2/3)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameters")
        
        # Single column for parameters
        option_type = st.selectbox("Option Type", ["call", "put"])
        spot_input = st.text_input("Spot Price (S)", value="100.00")
        strike_input = st.text_input("Strike Price (K)", value="100.00")
        days_input = st.text_input("Days to Expiry", value="30")
        div_yield_input = st.text_input("Dividend Yield (q) - Enter as decimal (e.g., 0.01 for 1%)", value="0.00")
        vol_input = st.text_input("Volatility (σ) - Enter as decimal (e.g., 0.25 for 25%)", value="0.25")
        rate_input = st.text_input("Risk-free Rate (r) - Enter as decimal (e.g., 0.04 for 4%)", value="0.04")
    
    with col2:
        st.subheader("Results")
        
        # Parse inputs and calculate price and Greeks
        try:
            spot = float(spot_input) if spot_input else 100.0
            strike = float(strike_input) if strike_input else 100.0
            rate = float(rate_input) if rate_input else 0.04
            div_yield = float(div_yield_input) if div_yield_input else 0.0
            vol = float(vol_input) if vol_input else 0.25
            days = int(days_input) if days_input else 30
            T = days / 365.0

            price, greeks = bs.price_and_greeks(spot, strike, rate, div_yield, vol, T, option_type)
            
            # Main results
            col_price1, col_price2 = st.columns(2)
            with col_price1:
                st.metric("Option Price", f"${price:.4f}")
            with col_price2:
                moneyness = "ITM" if (option_type == "call" and spot > strike) or (option_type == "put" and spot < strike) else "OTM" if (option_type == "call" and spot < strike) or (option_type == "put" and spot > strike) else "ATM"
                st.metric("Moneyness", moneyness)
            
            # Intrinsic vs Time Value
            intrinsic = max(spot - strike, 0) if option_type == "call" else max(strike - spot, 0)
            time_value = price - intrinsic
            
            col_int, col_time = st.columns(2)
            with col_int:
                st.metric("Intrinsic Value", f"${intrinsic:.4f}")
            with col_time:
                st.metric("Time Value", f"${time_value:.4f}")
            
            # Greeks display
            st.markdown("### Greeks")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Delta", f"{greeks['delta']:.4f}")
                st.metric("Gamma", f"{greeks['gamma']:.4f}")
            
            with col2:
                st.metric("Vega", f"{greeks['vega']:.4f}")
                st.metric("Theta", f"{greeks['theta']:.4f}")
            
            with col3:
                st.metric("Rho", f"{greeks['rho']:.4f}")
                st.metric("Days to Expiry", f"{days}")

        except ValueError:
            st.info("Enter numeric values to see results.")
        except Exception as e:
            st.error(f"Error in calculation: {str(e)}")
