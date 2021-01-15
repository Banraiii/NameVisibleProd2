from django.urls import path
from .views import *


app_name = 'core'
urlpatterns = [
    path('', Newspage.as_view(), name='news-list'),
    path('news/<slug>/', NewsDetailView.as_view(), name='news-detail'),
    path('list/', HomeView.as_view(), name='home'),
    path('list/chechout/', CheckoutView.as_view(), name="checkout"),
    path('list/order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('list/product/<slug>', ItemDetaleView.as_view(), name='product'),
    path('list/add_to_cart/<slug>', add_to_cart, name='add-to-cart'),
    path('list/remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('list/remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment')
]
