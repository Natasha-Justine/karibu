from django.db import models
from django.contrib.auth.models import AbstractUser


# Create User table called user profile using Abstract user from line 3
class Userprofile(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Supports three roles: Owner, Manager, and Sales Agent.
    Users can be assigned to specific branches.
    """
    is_salesagent = models.BooleanField(default=True, null=True)
    is_manager = models.BooleanField(default=True, null=True)
    is_owner = models.BooleanField(default=True, null=True)
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(max_length=254)  # Use 254 for EmailField
    address = models.CharField(max_length=50, blank=True, null=True, default="")
    phonenumber = models.CharField(max_length=20, blank=True, null=True, default="")
    gender = models.CharField(max_length=10, blank=True, null=True, default="")
    assigned_branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username


# model for branch
class Branch(models.Model):
    """
    Represents a business branch/location.
    Each branch can have its own stock, sales agents, and manager.
    """
    branch_name = models.CharField(max_length=25)
    location = models.CharField(max_length=50)

    def __str__(self):
        return self.branch_name


class Category(models.Model):
    category_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.category_name


# stock model
class Stock(models.Model):
    """
    Represents inventory items in stock.
    Tracks quantities, prices, and branch assignment.
    """
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    item_name = models.CharField(max_length=25, default="", blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    time_of_produce = models.DateField(auto_now_add=True)
    tonnage = models.IntegerField(blank=True, null=True, default=0)
    total_quantity = models.IntegerField(blank=True, null=True, default=0)
    cost = models.IntegerField(blank=True, null=True, default=0)
    name_of_dealer = models.CharField(blank=True, null=True, max_length=255)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=25)
    unit_price = models.IntegerField(default=0)
    unit_cost = models.IntegerField(default=0)
    current_stock = models.IntegerField()
    received_quantity = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.item_name


# sales table called sales
class Sale(models.Model):
    """
    Records sales transactions.
    Links to stock items and tracks payment details.
    """
    product_name = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    tonnage = models.IntegerField(blank=True, null=True, default=0)
    amount_paid = models.IntegerField(default=0, blank=True, null=True)
    buyers_name = models.CharField(max_length=35, blank=False, null=False, default="")
    date_and_time = models.DateTimeField(auto_now_add=True)  # Changed from DateField to DateTimeField
    salesagent_name = models.CharField(blank=True, null=True, max_length=255, default="")
    method_of_payment = models.CharField(
        choices=[("Cash", "Cash"), ("Credit", "Credit")], blank=True, null=True, max_length=255, default="Cash"
    )
    unit_price = models.IntegerField(default=0, blank=True, null=True)
    amount_received = models.FloatField(default=0, blank=True, null=True)

    def total_sales(self):
        if self.product_name:
           expected_sales = self.tonnage * self.product_name.unit_price
           return int(expected_sales)
        else:
              return 0

    def get_change(self):
        if self.amount_received is  not None:
           change = self.amount_received - self.total_sales()
           return int(change)
        else:
            return 0

    def __str__(self):
        return self.buyers_name


# credit table
class Credit(models.Model):
    """
    Manages credit transactions for sales on credit.
    Tracks buyer information and payment schedules.
    """
    buyer_name = models.CharField(blank=True, max_length=255, null=True, default="")
    NIN = models.CharField(unique=True, max_length=25, blank=True, null=True, default="")
    location = models.CharField(blank=True, null=True, max_length=255, default="")
    contact = models.IntegerField(default=0)
    amount_due = models.IntegerField(default=0, null=True)
    due_date = models.DateField(null=True, blank=True)  # Remove auto_now_add
    product_name = models.CharField(blank=True, null=True, max_length=255)
    salesagent_name = models.CharField(max_length=25, blank=True, null=True)
    type_of_produce = models.IntegerField(default=0, blank=True, null=True)
    tonnage = models.IntegerField(blank=True, null=True, default=0)
    Dispatch_date = models.DateField(null=True, blank=True)  # Remove auto_now_add
    branch_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.buyer_name
