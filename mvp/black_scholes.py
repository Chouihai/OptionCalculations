import math
from typing import Dict, Literal, Tuple


OptionType = Literal["call", "put"]


SQRT_2PI = math.sqrt(2.0 * math.pi)


def _norm_pdf(x: float) -> float:
	return math.exp(-0.5 * x * x) / SQRT_2PI


def _norm_cdf(x: float) -> float:
	# Numerically stable CDF using error function
	return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _d1(
	spot: float,
	strike: float,
	rate: float,
	dividend_yield: float,
	vol: float,
	time_years: float,
) -> float:
	return (
		math.log(spot / strike)
		+ (rate - dividend_yield + 0.5 * vol * vol) * time_years
	) / (vol * math.sqrt(time_years))


def _d2(d1: float, vol: float, time_years: float) -> float:
	return d1 - vol * math.sqrt(time_years)


def _forward_price(spot: float, rate: float, dividend_yield: float, time_years: float) -> float:
	return spot * math.exp((rate - dividend_yield) * time_years)


def price(
	spot: float,
	strike: float,
	rate: float,
	dividend_yield: float,
	vol: float,
	time_years: float,
	option_type: OptionType,
) -> float:
	"""Black–Scholes–Merton price with continuous dividend yield.

	- spot: current underlying price (S)
	- strike: strike price (K)
	- rate: risk-free rate (annualized, continuously compounded)
	- dividend_yield: continuous dividend yield (q)
	- vol: volatility (sigma), e.g. 0.2 for 20%
	- time_years: time to expiry in years (T)
	- option_type: "call" or "put"
	"""
	if time_years <= 0.0:
		intrinsic = max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
		return intrinsic

	if vol <= 0.0:
		# Degenerate case: deterministic forward
		se_qt = spot * math.exp(-dividend_yield * time_years)
		ke_rt = strike * math.exp(-rate * time_years)
		if option_type == "call":
			return max(se_qt - ke_rt, 0.0)
		else:
			return max(ke_rt - se_qt, 0.0)

	d1 = _d1(spot, strike, rate, dividend_yield, vol, time_years)
	d2 = _d2(d1, vol, time_years)
	se_qt = spot * math.exp(-dividend_yield * time_years)
	ke_rt = strike * math.exp(-rate * time_years)

	if option_type == "call":
		return se_qt * _norm_cdf(d1) - ke_rt * _norm_cdf(d2)
	else:
		return ke_rt * _norm_cdf(-d2) - se_qt * _norm_cdf(-d1)


def greeks(
	spot: float,
	strike: float,
	rate: float,
	dividend_yield: float,
	vol: float,
	time_years: float,
	option_type: OptionType,
) -> Dict[str, float]:
	"""Analytical Black–Scholes Greeks. Returns per 1.00 (not per 1%). Theta is per year."""
	if time_years <= 0.0 or vol <= 0.0:
		# Handle edge cases simply; most greeks go to 0 as T->0 or sigma->0 except delta step.
		if option_type == "call":
			delta = 1.0 if spot > strike else (0.0 if spot < strike else 0.5)
		else:
			delta = -1.0 if spot < strike else (0.0 if spot > strike else -0.5)
		return {
			"delta": delta * math.exp(-dividend_yield * max(time_years, 0.0)),
			"gamma": 0.0,
			"vega": 0.0,
			"theta": 0.0,
			"rho": 0.0,
		}

	d1 = _d1(spot, strike, rate, dividend_yield, vol, time_years)
	d2 = _d2(d1, vol, time_years)
	se_qt = spot * math.exp(-dividend_yield * time_years)
	ke_rt = strike * math.exp(-rate * time_years)
	pdf_d1 = _norm_pdf(d1)
	sqrt_T = math.sqrt(time_years)

	if option_type == "call":
		delta = math.exp(-dividend_yield * time_years) * _norm_cdf(d1)
		theta = (
			-(se_qt * pdf_d1 * vol) / (2.0 * sqrt_T)
			- rate * ke_rt * _norm_cdf(d2)
			+ dividend_yield * se_qt * _norm_cdf(d1)
		)
		rho = time_years * ke_rt * _norm_cdf(d2)
	else:
		delta = -math.exp(-dividend_yield * time_years) * _norm_cdf(-d1)
		theta = (
			-(se_qt * pdf_d1 * vol) / (2.0 * sqrt_T)
			+ rate * ke_rt * _norm_cdf(-d2)
			- dividend_yield * se_qt * _norm_cdf(-d1)
		)
		rho = -time_years * ke_rt * _norm_cdf(-d2)

	gamma = (math.exp(-dividend_yield * time_years) * pdf_d1) / (spot * vol * sqrt_T)
	vega = se_qt * pdf_d1 * sqrt_T

	return {
		"delta": float(delta),
		"gamma": float(gamma),
		"vega": float(vega),
		"theta": float(theta),  # per year
		"rho": float(rho),
	}


def price_and_greeks(
	spot: float,
	strike: float,
	rate: float,
	dividend_yield: float,
	vol: float,
	time_years: float,
	option_type: OptionType,
) -> Tuple[float, Dict[str, float]]:
	return price(spot, strike, rate, dividend_yield, vol, time_years, option_type), greeks(
		spot, strike, rate, dividend_yield, vol, time_years, option_type
	)


def theoretical_bounds(
	spot: float, strike: float, rate: float, dividend_yield: float, time_years: float, option_type: OptionType
) -> Tuple[float, float]:
	"""Return (min_price, max_price) for a European option under BSM assumptions."""
	se_qt = spot * math.exp(-dividend_yield * time_years)
	ke_rt = strike * math.exp(-rate * time_years)
	if option_type == "call":
		return (max(se_qt - ke_rt, 0.0), se_qt)
	else:
		return (max(ke_rt - se_qt, 0.0), ke_rt)



