from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDestroyView, OfferListView

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list"),
    path("<int:pk>/", ProductRetrieveUpdateDestroyView.as_view(), name="product-detail"),
    path("offers/", OfferListView.as_view(), name="offer-list"),
]
