from django.shortcuts import render, redirect
from .models import *
from django.urls import reverse
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
# Create your views here.
#view for indexpage
def index(request):
    return render(request, 'home/index.html')

@login_required
def addstock(request, pk):
    issued_item = Stock.objects.get(id=pk)
    form = UpdateStockForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            added_quantity = int(request.POST['received_quantity'])
            issued_item.tonnage += added_quantity
            issued_item.save()
            #to add to the remaining stock quantity is increasing
            print(added_quantity)
            print(issued_item.tonnage)
            return redirect('allstock')
            
    return render(request, 'home/addstock.html', {'form': form})

@login_required
def addsales(request):

    return render(request, 'home/addsales.html')

@login_required
def receipt(request):
    sales = Sale.objects.all().order_by('-id')
    return render(request, 'home/receipt.html',{'sales': sales})

def all_stock(request):
    stock=Stock.objects.all().order_by('-id')
    return render(request, 'home/allstock.html',{'stock':stock})

@login_required
def all_sales(request):
    sales = Sale.objects.all().order_by('-id')
    #sales = Sale.objects.filter(salesagent_name=request.user.username).order_by('-id')
    return render(request, 'home/allsales.html', {'sales': sales})


#aview to handle a link for a particular item to sell
@login_required
def stock_detail(request, stock_id):
    stock = Stock.objects.get(id=stock_id)
    return render(request, 'home/detail.html',{'stock':stock})
@login_required
def issue_item(request,pk):
    #creating a variable issued item and accessing all enteries inthe stock model
    issued_item = Stock.objects.get(id=pk)
    #accessing our form from forms.py
    sales_form = AddSaleForm(request.POST)
    if request.method== 'POST':
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.item_name = issued_item
            new_sale.unit_price = issued_item.unit_price
            new_sale.save()
            #to keep track of the stock after sales
            issued_quantity = int(request.POST['tonnage'])
            issued_item.total_quantity = issued_quantity
            issued_item.save()
            print(issued_item.item_name)
            print(request.POST['tonnage'])
            print(issued_item.total_quantity)
            return redirect('receipt')
    return render(request,'home/issue_item.html',{'sales_form':sales_form})

@login_required
def receipt_detail(request, receipt_id):
    receipt = Sale.objects.get(id=receipt_id)
    return render(request, 'home/receipt_detail.html',{'receipt':receipt})

#login view
def custom_logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        #checking in the logging in user
        user = authenticate(request, username=username, password=password)
        #checking if the user is the owner of the system
        if user is not None and user.is_owner == True:
            form = login(request, user)
            return redirect('/dashboard1/')
        
        if user is not None and user.is_salesagent == True:
            form = login(request, user)
            return redirect('/dashboard3/')
        
        if user is not None and user.is_manager == True:
            form = login(request, user)
            return redirect('/dashboard2/')
        else:
            print('Something went wrong')
    form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form, 'title': 'Login'})

def signup(request):
    if request.method == 'POST':
        form = UserCreation(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            return redirect('/login/')
    else:
        form = UserCreation()
    return render(request, 'home/signup.html', {'form': form})

def manager(request):
    return render(request, 'home/dashboard2.html')

def owner(request):
    return render(request, 'home/dashboard1.html')

def salesagent(request):
    return render(request, 'home/dashboard3.html')