import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy.stats import norm
import os
import requests
from mvp import black_scholes as bs
from mvp.implied_vol import solve_iv


def show_heatmap_page():
    st.markdown('<h1 class="main-header">Profit Calculator</h1>', unsafe_allow_html=True)

    # Create two columns: parameters (1/3) and results (2/3)
    col1, col2 = st.columns([1, 2])

    # Initialize defaults for controlled inputs
    if 'spot_input' not in st.session_state:
        st.session_state.spot_input = "97.50"

    with col1:
        st.subheader("Inputs")

        # Condensed input layout in rows
        r1c1, r1c2 = st.columns(2)
        option_type = r1c1.selectbox("Option Type", ["call", "put"])
        days_input = r1c2.text_input("Days to Expiry", value="14")

        # Ticker + Fetch + Price (single row)
        # Header row for alignment
        h1, h2, h3 = st.columns([2, 1, 2])
        with h1:
            st.markdown("Ticker")
        with h2:
            st.markdown("&nbsp;", unsafe_allow_html=True)
        with h3:
            st.markdown("Price")

        r_tkr1, r_tkr2, r_tkr3 = st.columns([2, 1, 2])
        r_tkr1.text_input("Ticker", key="ticker_symbol", placeholder="AAPL", label_visibility="collapsed")

        # Helpers for fetching live price
        def _fetch_and_set():
            sym = (st.session_state.get('ticker_symbol') or '').strip().upper()
            if not sym:
                st.warning("Enter a ticker symbol to fetch its latest price.")
                return
            price, err = _get_live_price(sym)
            if err:
                st.error(err)
                return
            st.session_state.spot_input = f"{price:.2f}"
            # Also set a sensible default price range around the live price
            st.session_state.range_min = f"{price - 2.0:.2f}"
            st.session_state.range_max = f"{price + 2.0:.2f}"
            st.success(f"Fetched {sym} last price: ${price:.2f}")

        r_tkr2.button("Fetch", on_click=_fetch_and_set, use_container_width=True)
        r_tkr3.text_input("Price", key="spot_input", label_visibility="collapsed", placeholder="e.g. 97.50")
        st.caption("Enter a ticker and click Fetch, or input the price manually.")

        # Option price and strike on one row
        r2c1, r2c2 = st.columns(2)
        market_price_input = r2c1.text_input("Option Price", value="2.33")
        strike_input = r2c2.text_input("Strike", value="97.50")

        # Rates row: risk-free and dividend yield together
        r3c1, r3c2 = st.columns(2)
        rate_input = r3c1.text_input("Risk-free Rate (r)", value="0.04")
        div_yield_input = r3c2.text_input("Dividend Yield (q)", value="0.00")

        # Solve for IV and calculate probability of profit
        if st.button("Calculate", type="primary"):
            try:
                # Parse inputs at submission time to avoid jitter while typing
                market_price = float(market_price_input) if market_price_input else 2.33
                spot = float(st.session_state.get('spot_input') or spot_input or 97.50)
                strike = float(strike_input) if strike_input else 97.50
                rate = float(rate_input) if rate_input else 0.04
                div_yield = float(div_yield_input) if div_yield_input else 0.0
                days = int(days_input) if days_input else 14
                T = days / 365.0

                # Validate basic inputs for calculate only; price range handled in heatmap panel
                if spot <= 0 or strike <= 0:
                    st.error("Spot and Strike must be positive.")
                    return

                result = solve_iv(market_price, spot, strike, rate, div_yield, T, option_type)

                if result["converged"] and result["vol"] is not None:
                    st.success("Profit calculation successful.")

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
                    st.error(f"IV calculation failed: {result['message']}")

            except Exception as e:
                st.error(f"Error in calculation: {str(e)}")

        # After calculation, show key metrics under inputs
        if 'iv_result' in st.session_state and 'prob_profit' in st.session_state:
            mc1, mc2 = st.columns(2)
            with mc1:
                st.metric("Implied Volatility", f"{st.session_state.iv_result['vol']*100:.2f}%")
            with mc2:
                st.metric("Probability of Profit", f"{st.session_state.prob_profit:.1%}")

    with col2:

        # Metrics are now displayed under the inputs; no duplicate metrics here

        # Create heatmap if we have results
        if 'heatmap_params' in st.session_state:
            params = st.session_state.heatmap_params
            iv = st.session_state.iv_result['vol']

            # Price range controls directly above the heatmap (condensed single row)
            if 'spot_range' not in st.session_state:
                st.session_state.spot_range = (params['spot'] - 2.0, params['spot'] + 2.0)
            if 'range_min' not in st.session_state:
                st.session_state.range_min = f"{st.session_state.spot_range[0]:.2f}"
            if 'range_max' not in st.session_state:
                st.session_state.range_max = f"{st.session_state.spot_range[1]:.2f}"

            pr_c1, pr_c2 = st.columns(2)
            pr_c1.text_input("Min Price ($)", key="range_min")
            pr_c2.text_input("Max Price ($)", key="range_max")

            # Create date range (similar to the reference image)
            start_date = datetime.now()
            dates = []
            for i in range(params['days'] + 1):
                date = start_date + timedelta(days=i)
                dates.append(date.strftime('%b %d'))

            # Create spot price range (user-configurable via inputs above)
            try:
                spot_min = float(st.session_state.range_min)
                spot_max = float(st.session_state.range_max)
                if spot_min >= spot_max:
                    raise ValueError
            except Exception:
                # Fallback to last good range or default
                spot_min, spot_max = st.session_state.spot_range

            # Persist last used/valid spot range
            st.session_state.spot_range = (spot_min, spot_max)

            # Use a fixed resolution for the heatmap (41 points)
            spot_prices = np.linspace(spot_min, spot_max, num=41)
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

                        # Calculate PnL for a long option: future option value minus initial cost
                        pnl = opt_price - params['market_price']
                        row.append(float(pnl))  # Keep full precision for display
                    except:
                        row.append(np.nan)
                pnl_matrix.append(row)

            # Create heatmap with numerical values
            fig = go.Figure(data=go.Heatmap(
                z=pnl_matrix,
                x=dates,
                y=spot_prices,
                colorscale=[
                    [0.0, '#b71c1c'],  # deeper red at min PnL
                    [0.25, '#ef9a9a'], # lighter red approaching 0
                    [0.5, '#ffffff'],  # white near 0 PnL
                    [0.75, '#b9f6ca'], # light green near 0
                    [1.0, '#2ecc71']   # green at max PnL (not too dark)
                ],
                zmid=0,               # center colors around breakeven (0)
                showscale=False,      # hide color bar
                text=[[f"{val:,.2f}" if not np.isnan(val) else "" for val in row] for row in pnl_matrix],
                texttemplate="%{text}",
                textfont={"size": 10, "color": "black"},
                hoverinfo='text',
                hovertemplate='Spot: $%{y:.2f}<br>Date: %{x}<br>PnL: $%{z:,.2f}<extra></extra>'
            ))

            fig.update_layout(
                title="Estimated Returns",
                xaxis_title="Date",
                yaxis_title="Spot Price ($)",
                width=800,
                height=800,  # Square aspect ratio for 1:1 cells
                                 yaxis=dict(autorange=True)  # Lowest to highest price
            )

            st.plotly_chart(fig, use_container_width=True)

            # Persist last used spot range (already updated above)

        else:
            st.info("Enter market data and click 'Calculate' to generate the visualization.")


def _resolve_api_key() -> str:
    """Resolve Finnhub API key from several sources: session, env, Streamlit secrets."""
    # Session-scoped (optional future use)
    key = (st.session_state.get("finnhub_api_key") or "").strip()
    if key:
        return key
    # Environment variables (case-insensitive on Windows, but check typical variants)
    for name in ("FINNHUB_API_KEY", "finnhub_api_key", "FINNHUB_TOKEN", "finnhub_token"):
        val = os.environ.get(name)
        if isinstance(val, str) and val.strip():
            return val.strip()
    # Streamlit secrets
    try:
        import types
        sec = getattr(st, "secrets", {})
        if isinstance(sec, dict):
            for name in ("FINNHUB_API_KEY", "finnhub_api_key"):
                if name in sec and str(sec[name]).strip():
                    return str(sec[name]).strip()
            # nested form: { finnhub = { api_key = "..." } }
            if "finnhub" in sec and isinstance(sec["finnhub"], dict):
                v = sec["finnhub"].get("api_key")
                if isinstance(v, str) and v.strip():
                    return v.strip()
    except Exception:
        pass
    return ""


def _get_live_price(symbol: str):
    """Fetch latest price via Finnhub REST. Returns (price, error)."""
    api_key = _resolve_api_key()
    if not api_key:
        return None, (
            "Finnhub API key not found. Set environment variable FINNHUB_API_KEY, "
            "or add it to .streamlit/secrets.toml (FINNHUB_API_KEY='...')."
        )
    try:
        resp = requests.get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": symbol, "token": api_key},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json() or {}
        price = data.get("c")
        ts = data.get("t", 0)
        if price is None or not ts:
            return None, f"No price available for {symbol}."
        return float(price), None
    except requests.RequestException as e:
        return None, f"Error fetching price: {e}"
