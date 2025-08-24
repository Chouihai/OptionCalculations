import streamlit as st
from mvp import black_scholes as bs

def show_home_page():
    st.markdown('<h1 class="main-header">Option Pricing Calculator</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### Welcome to the Option Pricing Calculator! 📈
        
        This interactive tool helps you understand option pricing using the Black-Scholes-Merton model.
        
        **Features:**
        - 🎯 **Real-time option pricing** with all Greeks
        - 📊 **Interactive charts** showing price behavior
        - 🔍 **Implied volatility solver** from market prices
        - 📱 **Mobile-friendly** interface
        
        **Get Started:**
        - Use the sidebar to navigate between features
        - Adjust parameters with the sliders
        - Watch results update in real-time
        """)
        
        st.info("💡 **Tip:** Start with the Option Pricing page to explore how different parameters affect option prices and Greeks.")
        
        # Quick example
        st.markdown("### Quick Example")
        with st.expander("Show a sample calculation"):
            spot, strike, rate, vol, days = 100, 100, 0.04, 0.25, 30
            price, greeks = bs.price_and_greeks(spot, strike, rate, 0.0, vol, days/365, "call")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Call Price", f"${price:.4f}")
            with col2:
                st.metric("Delta", f"{greeks['delta']:.4f}")
            
            st.markdown(f"""
            **Parameters:** S=${spot}, K=${strike}, r={rate*100}%, σ={vol*100}%, T={days} days
            
            **Greeks:**
            - Delta: {greeks['delta']:.4f}
            - Gamma: {greeks['gamma']:.4f}
            - Vega: {greeks['vega']:.4f}
            - Theta: {greeks['theta']:.4f} per year
            - Rho: {greeks['rho']:.4f}
            """)
