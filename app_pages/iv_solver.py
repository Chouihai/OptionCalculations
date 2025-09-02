import streamlit as st
import numpy as np
import pandas as pd
from mvp import black_scholes as bs
from mvp.implied_vol import solve_iv

def show_iv_solver_page():
    st.markdown('<h1 class="main-header">Implied Volatility Solver</h1>', unsafe_allow_html=True)
    
    # Create two columns: parameters (1/3) and results (2/3)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parameters")

        # Single column for parameters
        option_type = st.selectbox("Option Type", ["call", "put"])
        market_price_input = st.text_input("Market Option Price", value="2.33")
        spot_input = st.text_input("Spot Price (S)", value="100.00")
        strike_input = st.text_input("Strike Price (K)", value="100.00")
        div_yield_input = st.text_input("Dividend Yield (q) - Enter as decimal (e.g., 0.01 for 1%)", value="0.00")
        rate_input = st.text_input("Risk-free Rate (r) - Enter as decimal (e.g., 0.04 for 4%)", value="0.04")
        days_input = st.text_input("Days to Expiry", value="30")
        
        # Solve for IV
        if st.button("Solve for Implied Volatility", type="primary"):
            try:
                # Parse on submit to avoid input jitter
                market_price = float(market_price_input) if market_price_input else 2.33
                spot = float(spot_input) if spot_input else 100.0
                strike = float(strike_input) if strike_input else 100.0
                rate = float(rate_input) if rate_input else 0.04
                div_yield = float(div_yield_input) if div_yield_input else 0.0
                days = int(days_input) if days_input else 30
                T = days / 365.0

                result = solve_iv(market_price, spot, strike, rate, div_yield, T, option_type)
                
                if result["converged"] and result["vol"] is not None:
                    st.success("IV calculation successful.")
                    
                    col_iv, col_iter = st.columns(2)
                    with col_iv:
                        st.metric("Implied Volatility", f"{result['vol']:.4f} ({result['vol']*100:.2f}%)")
                    with col_iter:
                        st.metric("Iterations", result["iterations"])
                    
                    # Show theoretical price with solved IV
                    theo_price = bs.price(spot, strike, rate, div_yield, result["vol"], T, option_type)
                    st.metric("Theoretical Price", f"${theo_price:.4f}")
                    st.metric("Price Difference", f"${abs(market_price - theo_price):.6f}")
                    
                else:
                    st.error(f"IV calculation failed: {result['message']}")
                    
            except Exception as e:
                st.error(f"Error in IV calculation: {str(e)}")
    
    with col2:
        st.subheader("IV Analysis")
        
        # Create IV curve for different strikes
        if 'result' in locals() and result["converged"]:
            # Generate IV curve
            strikes_range = st.slider("Strike Range", min_value=spot*0.5, max_value=spot*1.5, value=(spot*0.8, spot*1.2), step=1.0)
            
            strikes = np.linspace(strikes_range[0], strikes_range[1], 20)
            ivs = []
            
            for k in strikes:
                try:
                    iv_result = solve_iv(market_price, spot, k, rate, div_yield, T, option_type)
                    if iv_result["converged"] and iv_result["vol"] is not None:
                        ivs.append(iv_result["vol"])
                    else:
                        ivs.append(np.nan)
                except:
                    ivs.append(np.nan)
            
            # Create DataFrame for plotting
            df_iv = pd.DataFrame({
                'Strike': strikes,
                'Implied Volatility': ivs
            })
            
            # Plot
            st.line_chart(df_iv.set_index('Strike'))
            
            # Show current point
            if result["converged"] and result["vol"] is not None:
                st.markdown(f"**Current Point:** K=${strike}, IV={result['vol']:.4f}")
