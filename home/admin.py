from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class UserProfileAdmin(UserAdmin):
    """
    Customizes the admin interface for UserProfile model.
    Adds custom fields to list display and fieldsets.
    """
    list_display = ('username', 'email', 'is_manager', 'is_salesagent', 'is_owner', 'assigned_branch')
    list_filter = ('is_manager', 'is_salesagent', 'is_owner', 'assigned_branch')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('is_manager', 'is_salesagent', 'is_owner', 'assigned_branch', 
                      'address', 'phonenumber', 'gender')
        }),
    )

class StockAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for Stock model.
    Provides list display, search, and filtering options.
    """
    list_display = ('item_name', 'branch_name', 'tonnage', 'unit_price')
    list_filter = ('branch_name',)
    search_fields = ('item_name', 'branch_name')

class SaleAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for Sale model.
    Shows transaction details and provides filtering options.
    """
    list_display = ('product_name', 'buyers_name', 'tonnage', 'amount_paid', 
                   'salesagent_name', 'date_and_time')
    list_filter = ('method_of_payment', 'date_and_time', 'salesagent_name')
    search_fields = ('buyers_name', 'salesagent_name', 'product_name__item_name')

class CreditAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for Credit model.
    Shows payment details and due dates with filtering options.
    """
    list_display = ('buyer_name', 'branch_name', 'amount_due', 'due_date')
    list_filter = ('branch_name', 'due_date')
    search_fields = ('buyer_name', 'NIN', 'branch_name')

class BranchAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for Branch model.
    Shows branch details with search functionality.
    """
    list_display = ('branch_name', 'location')
    search_fields = ('branch_name', 'location')

# Register models with their custom admin classes
admin.site.register(Userprofile, UserProfileAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Category)