import sys
from typing import Optional

from . import black_scholes as bs
from .implied_vol import solve_iv


def _prompt_str(prompt: str, default: Optional[str] = None) -> str:
	while True:
		text = input(f"{prompt}{f' [{default}]' if default is not None else ''}: ").strip()
		if text:
			return text
		if default is not None:
			return default
		print("Please enter a value.")


def _prompt_float(prompt: str, default: Optional[float] = None) -> float:
	while True:
		text = input(f"{prompt}{f' [{default}]' if default is not None else ''}: ").strip()
		if not text and default is not None:
			return float(default)
		try:
			return float(text)
		except ValueError:
			print("Invalid number. Try again.")


def _prompt_percent(prompt: str, default: Optional[float] = None) -> float:
	val = _prompt_float(prompt + " (%)", default)
	return val / 100.0


def single_option_flow() -> None:
	print("\n=== Single Option (Black–Scholes–Merton) ===")
	spot = _prompt_float("Spot price (S)")
	strike = _prompt_float("Strike price (K)")
	rate = _prompt_percent("Risk-free rate (r)", 4.0)
	div_yield = _prompt_percent("Dividend yield (q)", 0.0)
	vol = _prompt_percent("Volatility (sigma)", 25.0)
	days = _prompt_float("Days to expiry", 30.0)
	T = days / 365.0
	opt_type = _prompt_str("Option type [call/put]", "call").lower()
	if opt_type not in ("call", "put"):
		print("Invalid option type. Defaulting to 'call'.")
		opt_type = "call"

	px, g = bs.price_and_greeks(spot, strike, rate, div_yield, vol, T, opt_type)  # type: ignore[arg-type]
	print("\n--- Results ---")
	print(f"Price: {px:.6f}")
	print("Greeks (per 1.00):")
	print(f"  Delta: {g['delta']:.6f}")
	print(f"  Gamma: {g['gamma']:.6f}")
	print(f"  Vega:  {g['vega']:.6f}")
	print(f"  Theta: {g['theta']:.6f} per year")
	print(f"  Rho:   {g['rho']:.6f}")

	# Optional IV solve
	try_iv = _prompt_str("Enter market option price to solve IV (blank to skip)", "").strip()
	if try_iv:
		mkt = float(try_iv)
		res = solve_iv(mkt, spot, strike, rate, div_yield, T, opt_type)  # type: ignore[arg-type]
		if res.get("vol") is not None and res.get("converged"):
			print(f"Implied Vol: {res['vol']:.6f} ({res['vol']*100:.2f}%) in {res['iterations']} iterations")
		else:
			print(f"IV solve failed: {res.get('message')}")


def main() -> None:
	print("Option Pricing MVP (console)")
	while True:
		print("\nChoose an action:")
		print("  1) Single Option (BSM)")
		print("  2) Quit")
		choice = _prompt_str("Enter choice", "1")
		if choice == "1":
			single_option_flow()
		elif choice == "2":
			print("Goodbye!")
			return
		else:
			print("Unknown choice. Try again.")


if __name__ == "__main__":
	main()



