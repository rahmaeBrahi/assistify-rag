from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Offer
from .serializers import ProductSerializer, ProductWriteSerializer, OfferSerializer


class IsAdminUserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin_user


class ProductListCreateView(generics.ListCreateAPIView):


    queryset = Product.objects.filter(is_active=True).prefetch_related("benefits", "related_products")
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductWriteSerializer
        return ProductSerializer


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):


    queryset = Product.objects.prefetch_related("benefits", "related_products")
    permission_classes = [IsAdminUserOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProductWriteSerializer
        return ProductSerializer

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_active = False
        product.save()
        return Response({"message": "Product deactivated."})


class OfferListView(generics.ListAPIView):

    queryset = Offer.objects.filter(is_active=True).select_related("product")
    serializer_class = OfferSerializer
    permission_classes = [permissions.AllowAny]
