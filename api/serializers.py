from django.db import transaction
from rest_framework  import serializers
from .models import Product, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 
            'description', 
            'price', 
            'stock', 
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Harga Tidak Boleh Negatif.")
        return value
    
class OrderItemSerializer(serializers.ModelSerializer):
    # product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=3)
    class Meta:
        model = OrderItem
        fields = [
            'product_id',
            'product_name',
            'product_price',
            'quantity', 
            'item_subtotal',
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = [
                'product',
                'quantity',
            ]

    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemCreateSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items')
        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if orderitem_data is not None:
                instance.items.all().delete()
                for item in orderitem_data:
                    OrderItem.objects.create(
                        order=instance,
                        **item,
                    )

        return instance   
    
    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item in orderitem_data:
                OrderItem.objects.create(
                    order=order,
                    **item,
                )
        return order

    class Meta:
        model = Order
        fields = [
            'order_id',
            'status',
            'items',
        ]
        extra_kwargs = {
            'user': {'read_only': True}
        }

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')

    def total(self, obj):
        order_items = obj.items.all()
        return sum(item.item_subtotal for item in order_items)
    
    class Meta:
        model = Order
        fields = [
            'order_id', 
            'user', 
            'products', 
            'created_at', 
            'status', 
            'items', 
            'total_price'
        ]

class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()