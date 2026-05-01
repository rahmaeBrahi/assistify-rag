import uuid
from django.db import models
from django.conf import settings


class Order(models.Model):

    class Status(models.TextChoices):
        PLACED = "placed", "Order Placed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentMethod(models.TextChoices):
        CARD = "card", "Credit/Debit Card"
        COD = "cod", "Cash on Delivery"

    order_number = models.CharField(max_length=50, unique=True, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    customer_email = models.EmailField()

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.COD)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    delivery_address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    tracking_number = models.CharField(max_length=50, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        from django.utils import timezone
        import random
        year = timezone.now().year
        num = random.randint(1, 9999)
        return f"ORD-{year}-{str(num).zfill(4)}"

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "products.Product", on_delete=models.SET_NULL, null=True, related_name="order_items"
    )
    product_name = models.CharField(max_length=255)
    product_emoji = models.CharField(max_length=10, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "order_items"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.order.order_number} — {self.product_name} x{self.quantity}"


class TrackingUpdate(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tracking_updates")
    date = models.DateField()
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255)

    class Meta:
        db_table = "tracking_updates"
        ordering = ["date"]

    def __str__(self):
        return f"{self.order.order_number} — {self.status} @ {self.location}"


class Review(models.Model):

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="review")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    rating = models.PositiveSmallIntegerField() 
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"

    def __str__(self):
        return f"Review for {self.order.order_number} — {self.rating}★"
