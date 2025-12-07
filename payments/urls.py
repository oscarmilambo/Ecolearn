from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('plans/', views.payment_plans, name='payment_plans'),
    path('pay/<int:plan_id>/', views.initiate_payment, name='initiate_payment'),
    path('status/<str:payment_id>/', views.payment_status, name='payment_status'),
    path('history/', views.payment_history, name='payment_history'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('webhook/<str:provider>/', views.webhook_handler, name='webhook_handler'),
]
