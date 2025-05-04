from django.forms import ModelForm
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class AddStockForm(ModelForm):
    """
    Form for adding new stock items to inventory.
    Automatically sets the branch name based on the user's assigned branch.
    """
    class Meta:
        model = Stock
        fields = '__all__'
        
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set branch name automatically based on user's assigned branch
        if user and (user.is_manager or user.is_salesagent):
            self.instance.branch_name = user.assigned_branch.branch_name

class AddSaleForm(ModelForm):
    """
    Form for recording new sales transactions.
    Product choices are filtered based on user's assigned branch.
    """
    class Meta:
        model = Sale
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filter product choices to only show products from user's branch
        if user and (user.is_manager or user.is_salesagent):
            branch_name = user.assigned_branch.branch_name
            self.fields['product_name'].queryset = Stock.objects.filter(branch_name=branch_name)

class UpdateStockForm(ModelForm):
    """
    Form for updating existing stock quantities.
    Includes validation to ensure users can only update stock from their assigned branch.
    """
    received_quantity = forms.IntegerField(min_value=1, label='Quantity to Add')
    
    class Meta:
        model = Stock
        fields = ['received_quantity']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean()
        # Validate that user can only update stock from their assigned branch
        if self.user and (self.user.is_manager or self.is_salesagent):
            stock_instance = self.instance
            if stock_instance and stock_instance.branch_name != self.user.assigned_branch.branch_name:
                raise forms.ValidationError("You can only update stock from your assigned branch")
        return cleaned_data

class UserCreation(UserCreationForm):
    """
    Custom user creation form that extends Django's UserCreationForm.
    Handles role-based branch assignments and validates role-specific requirements.
    """
    class Meta:
        model = Userprofile
        fields = ['username', 'email', 'password1', 'password2', 'is_manager', 
                 'is_salesagent', 'is_owner', 'assigned_branch', 'address', 
                 'phonenumber', 'gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configure branch assignment field
        self.fields['assigned_branch'].required = False
        self.fields['assigned_branch'].widget = forms.Select(
            choices=[('', '---------')] + [(branch.id, branch.branch_name) 
                                         for branch in Branch.objects.all()]
        )
        self.fields['assigned_branch'].label = "Branch Assignment (Required for Managers)"
        self.fields['is_manager'].help_text = "If selected, you must choose a branch below"
        
    def clean(self):
        cleaned_data = super().clean()
        is_manager = cleaned_data.get('is_manager')
        assigned_branch = cleaned_data.get('assigned_branch')
        
        # Ensure managers have an assigned branch
        if is_manager and not assigned_branch:
            raise forms.ValidationError("Branch assignment is required for managers")
        return cleaned_data

    def save(self, commit=True):
        user = super(UserCreation, self).save(commit=False)
        if commit:
            user.is_active = True
            user.is_staff = True
            user.save()
        return user

class CreditForm(ModelForm):
    """
    Form for managing credit transactions.
    Includes date widgets for improved date input handling.
    """
    class Meta:
        model = Credit
        fields = '__all__'
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'Dispatch_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SalesForm(ModelForm):
    """
    Form for managing sales records.
    """
    class Meta:
        model = Sale
        fields = '__all__'