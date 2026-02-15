
from django.db.models import Max

# Berfungsi untuk menangani permintaan API terkait produk dan pesanan
from django.shortcuts import get_object_or_404

# Import serializers dan models yang diperlukan
from api.serializers import ProductSerializer, OrderSerializer, ProductInfoSerializer, OrderCreateSerializer

# Import models Product dan Order
from api.models import Product, Order

# Import modul-modul dari DRF yang diperlukan
from rest_framework import filters
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

# Import permission untuk mengamankan tampilan API
from rest_framework.permissions import (
    IsAuthenticated, 
    IsAdminUser, 
    AllowAny
)

# Import model_to_dict jika diperlukan untuk mengonversi model ke dictionary
from django.forms.models import model_to_dict

# Import filter dari modul filters
from api.filters import ProductFilter, InStockFilterBackend, OrderFilter

# Import DjangoFilterBackend
from django_filters.rest_framework import DjangoFilterBackend


# New Views
class ProductListCreateAPIView(generics.ListCreateAPIView):
   
    # filterset_fields = ['name', 'price']
    # pagination_class = PageNumberPagination
    # pagination_class.page_size =2
    # pagination_class.page_query_param = 'pagenum'
    # pagination_class.page_size_query_param = 'size'
    # pagination_class.max_page_size = '1000'

    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = PageNumberPagination

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in [ 'PUT', 'PATCH', 'DELETE' ]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price':  products.aggregate(max_price=Max('price'))['max_price']
        })
        return Response(serializer.data)

