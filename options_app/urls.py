from django.urls import path
from .views import calculate_payoff

urlpatterns = [
    path('calculate/', calculate_payoff),
]
