from django.forms import ModelForm
from django import forms
#accessing our models to create co-oresponding forms
#importing all forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

#its mandetory to add Form at the end of the class
class AddStockForm(ModelForm):
    class Meta:
        model = Stock
        #fields= ['product_name','quantity','cost', 'supplier_name', 'date', 'type_of_stock', 'unit_price', 'unit_cost']
        fields = '__all__'

class AddSaleForm(ModelForm):
    class Meta:
        model = Sale
        #fields = '__all__' returns all fields from our models
        fields = '__all__'

class UpdateStockForm(ModelForm):
    class Meta:
        model = Stock
        fields = ['received_quantity']

class UserCreation(UserCreationForm):
    class Meta:
        model = Userprofile
        fields = '__all__'
    def save(self, commit=True):
        user = super(UserCreation, self).save(commit=False)
        if commit:
            user.is_active = True
            user.is_staff = True
            user.save()
        return user

class CreditForm(ModelForm):
    class Meta:
        model = Credit
        fields = '__all__'
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'Dispatch_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SalesForm(ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'