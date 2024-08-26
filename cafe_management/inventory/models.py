from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Model to represent item categories, e.g., Beverages, Snacks, etc.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    """
    Model to represent individual items in the cafe inventory.
    Each item belongs to a category.
    """
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_managed = models.BooleanField(default=False)  # Flag to indicate if the item has inventory tracking
    stock_quantity = models.IntegerField(default=0)  # Field to maintain the stock count

    def __str__(self):
        return f"{self.name} ({self.category.name}) - {self.price}"


class Bill(models.Model):
    """
    Model to represent a bill generated for a customer.
    """
    customer_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The staff who created the bill
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    extra_items = models.TextField(blank=True, null=True)  # Field to describe extra items
    extra_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Extra amount to be added to total


    def __str__(self):
        return f"Bill {self.id} - {self.customer_name} - {self.total_amount} - {self.date_created.strftime('%Y-%m-%d')}"

class BillItem(models.Model):
    """
    Model to represent items included in a particular bill.
    It uses a Many-to-Many relationship through this model.
    """
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='bill_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.item.name} - Bill {self.bill.id}"

    def get_item_total(self):
        return self.item.price * self.quantity
