from rest_framework import serializers
from .models import Order, OrderItem, TrackingUpdate, Review


class TrackingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingUpdate
        fields = ("date", "status", "location")


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "product_emoji", "unit_price", "quantity", "line_total")



class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class PlaceOrderSerializer(serializers.Serializer):

    customer_email = serializers.EmailField()
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    delivery_address = serializers.CharField(required=False, allow_blank=True, default="")
    phone = serializers.CharField(required=False, allow_blank=True, default="")
    items = OrderItemInputSerializer(many=True, min_length=1)

    def validate_items(self, items):
        from assistify.apps.products.models import Product

        validated = []
        for item in items:
            try:
                product = Product.objects.get(id=item["product_id"], is_active=True)
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product {item['product_id']} not found or inactive."
                )
            validated.append({"product": product, "quantity": item["quantity"]})
        return validated

    def create(self, validated_data):
        from decimal import Decimal
        from django.utils import timezone
        import datetime

        items_data = validated_data.pop("items")
        subtotal = sum(
            item["product"].price * item["quantity"] for item in items_data
        )
        shipping = Decimal("50.00")
        total = subtotal + shipping

        order = Order.objects.create(
            subtotal=subtotal,
            shipping_fee=shipping,
            total=total,
            estimated_delivery=(timezone.now().date() + datetime.timedelta(days=7)),
            **validated_data,
        )

        for item in items_data:
            product = item["product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_emoji=product.emoji,
                unit_price=product.price,
                quantity=item["quantity"],
            )

        TrackingUpdate.objects.create(
            order=order,
            date=timezone.now().date(),
            status="Order Placed",
            location="Warehouse",
        )

        return order



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking_updates = TrackingUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "customer_email",
            "status",
            "payment_method",
            "subtotal",
            "shipping_fee",
            "total",
            "delivery_address",
            "phone",
            "tracking_number",
            "estimated_delivery",
            "items",
            "tracking_updates",
            "created_at",
            "updated_at",
        )


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "order", "rating", "comment", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
