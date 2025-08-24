from typing import Dict, Literal, Optional

from .black_scholes import OptionType, price, theoretical_bounds


def solve_iv(
	market_price: float,
	spot: float,
	strike: float,
	rate: float,
	dividend_yield: float,
	time_years: float,
	option_type: OptionType,
	low: float = 1e-6,
	high: float = 5.0,
	tol: float = 1e-8,
	max_iter: int = 100,
) -> Dict[str, Optional[float]]:
	"""Solve for implied volatility using bisection with safe bracketing.

	Returns dict with keys: vol, converged (1/0), iterations, message.
	"""
	min_theory, max_theory = theoretical_bounds(spot, strike, rate, dividend_yield, time_years, option_type)
	if market_price < min_theory - 1e-12 or market_price > max_theory + 1e-12:
		return {
			"vol": None,
			"converged": 0,
			"iterations": 0,
			"message": f"market price outside theoretical bounds [{min_theory:.6f}, {max_theory:.6f}]",
		}

	# Ensure bracketing
	fl = price(spot, strike, rate, dividend_yield, low, time_years, option_type) - market_price
	fh = price(spot, strike, rate, dividend_yield, high, time_years, option_type) - market_price
	bracket_expand = 0
	while fl * fh > 0.0 and bracket_expand < 10:
		# Expand the bracket progressively
		low *= 0.5
		high *= 2.0
		fl = price(spot, strike, rate, dividend_yield, low, time_years, option_type) - market_price
		fh = price(spot, strike, rate, dividend_yield, high, time_years, option_type) - market_price
		bracket_expand += 1

	if fl * fh > 0.0:
		return {
			"vol": None,
			"converged": 0,
			"iterations": 0,
			"message": "failed to bracket root for volatility",
		}

	# Bisection
	iterations = 0
	for i in range(max_iter):
		mid = 0.5 * (low + high)
		fm = price(spot, strike, rate, dividend_yield, mid, time_years, option_type) - market_price
		iterations = i + 1
		if abs(fm) < tol:
			return {"vol": mid, "converged": 1, "iterations": iterations, "message": "ok"}
		if fl * fm <= 0.0:
			high = mid
			fh = fm
		else:
			low = mid
			fl = fm

	return {
		"vol": 0.5 * (low + high),
		"converged": 0,
		"iterations": iterations,
		"message": "max iterations reached",
	}


