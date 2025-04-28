from django.db import models
from django.contrib.auth.models import AbstractUser


# Create User table called user profile using Abstract user from line 3
class Userprofile(AbstractUser):
    is_salesagent = models.BooleanField(default=True, null=True)
    is_manager = models.BooleanField(default=True, null=True)
    is_owner = models.BooleanField(default=True, null=True)
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(max_length=254)  # Use 254 for EmailField
    address = models.CharField(max_length=50, blank=True, null=True, default="")
    phonenumber = models.CharField(max_length=20, blank=True, null=True, default="")
    gender = models.CharField(max_length=10, blank=True, null=True, default="")

    def __str__(self):
        return self.username


# model for branch
class Branch(models.Model):
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
    product_name = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True)
    tonnage = models.IntegerField(blank=True, null=True, default=0)
    amount_paid = models.IntegerField(default=0, blank=True, null=True)
    buyers_name = models.CharField(max_length=35, blank=False, null=False, default="")  # Added default
    date_and_time = models.DateField(auto_now_add=True)
    salesagent_name = models.CharField(blank=True, null=True, max_length=255, default="") #added default
    method_of_payment = models.CharField(
        choices=[("Cash", "Cash"), ("Credit", "Credit")], blank=True, null=True, max_length=255, default="Cash" #added default
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
        change = self.amount_received - self.total_sales()  # Corrected logic
        return abs(int(change))

    def __str__(self):
        return self.buyers_name


# credit table
class Credit(models.Model):
    buyer_name = models.CharField(blank=True, max_length=255, null=True, default="")
    NIN = models.IntegerField(unique=True)
    location = models.IntegerField(blank=True, null=True)
    contact = models.IntegerField(default=0)
    amount_due = models.IntegerField(default=0, null=True)
    due_date = models.DateField(auto_now_add=True)
    product_name = models.CharField(blank=True, null=True, max_length=255)
    salesagent_name = models.CharField(max_length=25, blank=True, null=True)
    type_of_produce = models.IntegerField(default=0, blank=True, null=True)
    tonnage = models.IntegerField(blank=True, null=True, default=0)
    Dispatch_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.buyer_name
