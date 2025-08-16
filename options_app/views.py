from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
import numpy as np
import pandas as pd

@api_view(['POST'])
def calculate_payoff(request):
    """
    Expects JSON:
    {
      "legs": [
        {"type": "call", "strike": 100, "premium": 5, "qty": 1}
      ],
      "price_range": [50, 150]
    }
    """
    legs = request.data.get("legs", [])
    price_range = request.data.get("price_range", [50, 150])

    S = np.linspace(price_range[0], price_range[1], 101)
    total_payoff = np.zeros_like(S)

    for leg in legs:
        if leg['type'] == 'call':
            payoff = np.maximum(S - leg['strike'], 0) - leg['premium']
        else:
            payoff = np.maximum(leg['strike'] - S, 0) - leg['premium']
        total_payoff += leg['qty'] * payoff

    df = pd.DataFrame({"stock_price": S, "payoff": total_payoff})
    return Response(df.to_dict(orient="records"))
