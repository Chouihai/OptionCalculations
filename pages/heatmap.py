import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy.stats import norm
from mvp import black_scholes as bs
from mvp.implied_vol import solve_iv

def show_heatmap_page():
    st.markdown('<h1 class="main-header">PnL Heatmap Analysis</h1>', unsafe_allow_html=True)
    
    # Create two columns: parameters (1/3) and results (2/3)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 Market Data")
        
        # Single column for parameters
        option_type = st.selectbox("Option Type", ["call", "put"])
        market_price = st.number_input("Market Option Price", min_value=0.0, max_value=10000.0, value=2.33, step=0.01)
        spot = st.number_input("Current Spot Price", min_value=0.01, max_value=10000.0, value=97.50, step=0.01)
        strike = st.number_input("Strike Price", min_value=0.01, max_value=10000.0, value=97.50, step=0.01)
        div_yield_input = st.text_input("Dividend Yield (q) - Enter as decimal (e.g., 0.01 for 1%)", value="0.00")
        rate_input = st.text_input("Risk-free Rate (r) - Enter as decimal (e.g., 0.04 for 4%)", value="0.04")
        days_input = st.text_input("Days to Expiry", value="14")
        
        # Convert text inputs to numbers with error handling
        try:
            rate = float(rate_input) if rate_input else 0.04
            div_yield = float(div_yield_input) if div_yield_input else 0.0
            days = int(days_input) if days_input else 14
        except ValueError:
            st.error("Please enter valid numbers for all parameters")
            rate, div_yield, days = 0.04, 0.0, 14
        
        T = days / 365.0
        
        # Solve for IV and calculate probability of profit
        if st.button("Calculate", type="primary"):
            try:
                result = solve_iv(market_price, spot, strike, rate, div_yield, T, option_type)
                
                if result["converged"] and result["vol"] is not None:
                    st.success("✅ IV calculation successful!")
                    
                    # Calculate probability of profit (simplified)
                    # For a call option, probability of profit = P(S_T > K)
                    # For a put option, probability of profit = P(S_T < K)
                    if option_type == "call":
                        # P(S_T > K) = N(d2)
                        d2 = (np.log(spot/strike) + (rate - div_yield - 0.5*result['vol']**2)*T) / (result['vol']*np.sqrt(T))
                        prob_profit = norm.cdf(d2)
                    else:
                        # P(S_T < K) = N(-d2)
                        d2 = (np.log(spot/strike) + (rate - div_yield - 0.5*result['vol']**2)*T) / (result['vol']*np.sqrt(T))
                        prob_profit = norm.cdf(-d2)
                    
                    with col_prob:
                        st.metric("Probability of Profit", f"{prob_profit:.1%}")
                    
                    # Store results in session state for heatmap
                    st.session_state.iv_result = result
                    st.session_state.prob_profit = prob_profit
                    st.session_state.heatmap_params = {
                        'option_type': option_type,
                        'market_price': market_price,
                        'spot': spot,
                        'strike': strike,
                        'rate': rate,
                        'div_yield': div_yield,
                        'days': days,
                        'T': T
                    }
                    
                else:
                    st.error(f"❌ IV calculation failed: {result['message']}")
                    
            except Exception as e:
                st.error(f"Error in calculation: {str(e)}")
    
    with col2:
        st.subheader("📊 PnL Heatmap")
        
        # Show IV at the top of the second column
        if 'iv_result' in st.session_state:
            st.metric("Implied Volatility", f"{st.session_state.iv_result['vol']:.4f} ({st.session_state.iv_result['vol']*100:.2f}%)")
        
        # Create heatmap if we have results
        if 'heatmap_params' in st.session_state:
            params = st.session_state.heatmap_params
            iv = st.session_state.iv_result['vol']
            
            # Create date range (similar to the reference image)
            start_date = datetime.now()
            dates = []
            for i in range(params['days'] + 1):
                date = start_date + timedelta(days=i)
                dates.append(date.strftime('%b %d'))
            
            # Create spot price range (similar to reference image)
            spot_prices = np.arange(params['spot'] - 1.9, params['spot'] + 1.3, 0.1)
            spot_prices = np.round(spot_prices, 2)
            
            # Calculate PnL matrix
            pnl_matrix = []
            for price in spot_prices:
                row = []
                for i, date in enumerate(dates):
                    try:
                        # Calculate option price at this spot and time
                        days_to_expiry = params['days'] - i
                        if days_to_expiry <= 0:
                            # At expiry, option value is intrinsic value
                            if params['option_type'] == 'call':
                                opt_price = max(price - params['strike'], 0)
                            else:
                                opt_price = max(params['strike'] - price, 0)
                        else:
                            opt_price = bs.price(price, params['strike'], params['rate'], 
                                               params['div_yield'], iv, days_to_expiry/365.0, params['option_type'])
                        
                        # Calculate PnL (market price - future price)
                        pnl = params['market_price'] - opt_price
                        row.append(round(pnl, 0))  # Round to whole numbers like in reference
                    except:
                        row.append(np.nan)
                pnl_matrix.append(row)
            
            # Create DataFrame for heatmap
            df_heatmap = pd.DataFrame(pnl_matrix, index=spot_prices, columns=dates)
            
            # Create heatmap with numerical values
            fig = go.Figure(data=go.Heatmap(
                z=pnl_matrix,
                x=dates,
                y=spot_prices,
                colorscale=[
                    [0, 'red'],      # Losses in red
                    [0.5, 'white'],  # Breakeven in white
                    [1, 'green']     # Profits in green
                ],
                zmid=0,  # Center the colorscale at 0
                text=[[f"{val:.0f}" if not np.isnan(val) else "" for val in row] for row in pnl_matrix],
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverinfo='text',
                hovertemplate='Spot: $%{y:.2f}<br>Date: %{x}<br>PnL: $%{z:.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{params['option_type'].title()} Option PnL Heatmap (IV: {iv:.1%})",
                xaxis_title="Date",
                yaxis_title="Spot Price ($)",
                width=800,
                height=800,  # Square aspect ratio for 1:1 cells
                                 yaxis=dict(autorange=True)  # Lowest to highest price
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add summary metrics
            col_sum1, col_sum2, col_sum3 = st.columns(3)
            with col_sum1:
                st.metric("Max Profit", f"${max([max(row) for row in pnl_matrix if any(not np.isnan(x) for x in row)]):.0f}")
            with col_sum2:
                st.metric("Max Loss", f"${min([min(row) for row in pnl_matrix if any(not np.isnan(x) for x in row)]):.0f}")
            with col_sum3:
                st.metric("Probability of Profit", f"{st.session_state.prob_profit:.1%}")
            

        else:
            st.info("👆 Enter market data and click 'Calculate' to generate the visualization.")
