from django.db import models

class Product(models.Model):
    """
    Medical device product as seen in chatData.js.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="EGP")
    emoji = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New rich metadata fields
    features = models.JSONField(default=list, blank=True, help_text="List of product features")
    suitable_for = models.JSONField(default=list, blank=True, help_text="List of user types or conditions this is suitable for")
    use_cases = models.JSONField(default=list, blank=True, help_text="List of scenarios where this product is used")

    related_products = models.ManyToManyField(
        "self", blank=True, symmetrical=True, related_name="related_to"
    )

    class Meta:
        db_table = "products"
        ordering = ["id"]

    def __str__(self):
        return self.name


class ProductBenefit(models.Model):
    """Bullet-point benefit lines for a product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="benefits")
    text = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "product_benefits"
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name}: {self.text}"


class Offer(models.Model):
    """
    Discounted price offer for a product (mirrors chatData.js offers array).
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="offer")
    discount_percent = models.PositiveSmallIntegerField()
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "offers"

    def __str__(self):
        return f"{self.product.name} — {self.discount_percent}% off"
