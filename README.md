# Option Pricing Calculator

An interactive web application for option pricing using the Black-Scholes-Merton model, built with Streamlit.

## Features

- **Real-time Option Pricing**: Calculate option prices and Greeks with live updates
- **Interactive Charts**: Visualize price curves and option behavior
- **Implied Volatility Solver**: Solve for implied volatility from market prices
- **Educational Tool**: Perfect for learning option pricing theory

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## Usage

### Option Pricing Page
- Adjust parameters using sliders and input fields
- Watch results update in real-time
- View interactive price curves
- See all Greeks (Delta, Gamma, Vega, Theta, Rho)

### IV Solver Page
- Enter market option price
- Set other parameters
- Solve for implied volatility
- View IV curves across different strikes

## Project Structure

```
OptionCalculations/
├── streamlit_app.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── mvp/                 # Core option pricing modules
│   ├── __init__.py
│   ├── black_scholes.py # Black-Scholes implementation
│   ├── implied_vol.py   # IV solver
│   ├── cli.py          # Console interface
│   └── __main__.py     # Console entry point
└── backend/            # Django backend (for future use)
```

## Mathematical Models

### Black-Scholes-Merton Model
The app implements the Black-Scholes-Merton formula with continuous dividend yield:

**Call Option:**
```
C = S*e^(-qT)*N(d1) - K*e^(-rT)*N(d2)
```

**Put Option:**
```
P = K*e^(-rT)*N(-d2) - S*e^(-qT)*N(-d1)
```

Where:
- `d1 = [ln(S/K) + (r-q+σ²/2)T] / (σ√T)`
- `d2 = d1 - σ√T`
- `S` = Spot price
- `K` = Strike price
- `r` = Risk-free rate
- `q` = Dividend yield
- `σ` = Volatility
- `T` = Time to expiry

### Greeks
- **Delta**: Rate of change of option price with respect to underlying
- **Gamma**: Rate of change of delta with respect to underlying
- **Vega**: Rate of change of option price with respect to volatility
- **Theta**: Rate of change of option price with respect to time
- **Rho**: Rate of change of option price with respect to interest rate

## Development

### Console Version
For a command-line interface, run:
```bash
python -m mvp
```

### Adding Features
The modular structure makes it easy to add:
- American options (binomial trees)
- More sophisticated models (Heston, SABR)
- Risk metrics (VaR, probability calculations)
- Market data integration

## Deployment

The app can be deployed to Streamlit Cloud:
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy automatically

## License

Educational tool - feel free to use and modify for learning purposes.
