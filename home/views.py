from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from django.urls import reverse
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Sale, Credit
from django.db.models import Sum,Q

# Create your views here.
#view for indexpage
def index(request):
    return render(request, 'home/index.html')

def is_owner_check(user):
    return user.is_owner

def is_manager_check(user):
    return user.is_manager

def is_salesagent_check(user):
    return user.is_salesagent

@login_required
@user_passes_test(is_manager_check)
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
@user_passes_test(is_salesagent_check, is_manager_check)
def addsales(request, pk):
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
            return redirect('allsales')
    return render(request,'home/addsales.html',{'sales_form':sales_form})


def editsales(request, pk):
    tx_to_edit = get_object_or_404(Sale, pk=pk)
    all_stock_items = Stock.objects.all()  # Fetch all available stock items

    if request.method == 'POST':
        data = request.POST
        stock_id = data.get('product_name')
        try:
            stock_instance = Stock.objects.get(id=stock_id)
            tx_to_edit.product_name = stock_instance
            tx_to_edit.tonnage = data.get('tonnage')
            tx_to_edit.amount_paid = data.get('amount_paid')
            tx_to_edit.buyers_name = data.get('buyers_name')
            tx_to_edit.date_and_time = data.get('date_and_time')
            tx_to_edit.salesagent_name = data.get('salesagent_name')
            tx_to_edit.method_of_payment = data.get('method_of_payment')
            tx_to_edit.unit_price = data.get('unit_price')
            tx_to_edit.amount_received = data.get('amount_received')
            tx_to_edit.save()
            return redirect('/view/' + str(tx_to_edit.pk))
        except Stock.DoesNotExist:
            # Handle the case where the submitted stock_id is invalid
            error_message = "Selected product does not exist."
            return render(request, 'home/editsales.html', {'edit_details': tx_to_edit, 'all_stock_items': all_stock_items, 'error': error_message})

    else:
        # For GET request, display the edit form
        return render(request, 'home/editsales.html', {'edit_details': tx_to_edit, 'all_stock_items': all_stock_items})

def viewsales(request, pk):
    database_id = pk
    tx = Sale.objects.get(pk=database_id)
    context = {
        'details': tx
    }
    return render(request, 'home/viewsales.html', context)

def delete(request, pk):
    to_delete = Sale.objects.get(pk=pk)
    if request.method == 'POST':
        data = request.POST
        to_delete.delete()
        return redirect('/')
    context = {
        'delete_details': to_delete
    }
    return render(request, 'home/delete.html', context)



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
def issue_item(request, pk):
    # creating a variable issued item and accessing all entries in the stock model
    issued_item = Stock.objects.get(id=pk)
    # accessing our form from forms.py
    sales_form = AddSaleForm(request.POST)
    if request.method == 'POST':
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.product_name = issued_item
            new_sale.item_name = issued_item.item_name
            
            # to keep track of the stock after sales
            issued_quantity = int(sales_form.cleaned_data['tonnage'])

            if issued_quantity <= issued_item.tonnage:
                issued_item.tonnage -= issued_quantity  # Subtract the sold quantity
                issued_item.total_quantity = issued_quantity  # Update the total quantity
                issued_item.save()

            new_sale.save()
            return redirect('receipt')
    return render(request, 'home/issue_item.html', {'sales_form': sales_form}) # Pass issued_item to the template (might be useful)

@login_required
def receipt_detail(request, receipt_id):
    receipt = Sale.objects.get(id=receipt_id)
    return render(request, 'home/receipt_detail.html',{'receipt':receipt})

#logout view
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/')
    return render(request, 'home/logout.html')

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


@login_required
@user_passes_test(is_manager_check)
def manager(request):
    total_cash_sales = Sale.objects.filter(method_of_payment='Cash').aggregate(
        total_cash=Sum('amount_received')
    )['total_cash'] or 0

    total_credit_sales = Credit.objects.aggregate(
        total_credit=Sum('amount_due')
    )['total_credit'] or 0 

    total_sales = total_cash_sales + total_credit_sales

    total_stock = Stock.objects.aggregate(
        total_quantity = Sum('tonnage')
    )['total_quantity'] or 0
    context = {
        'total_sales': total_sales,
        'total_cash_sales': total_cash_sales,
        'total_credit_sales': total_credit_sales,
        'total_stock': total_stock,
    }
    return render(request, 'home/dashboard2.html', context)

@login_required
@user_passes_test(is_owner_check)
def owner(request):
    total_cash_sales = Sale.objects.filter(method_of_payment='Cash').aggregate(
        total_cash=Sum('amount_received')
    )['total_cash'] or 0
 
    total_credit_sales = Credit.objects.aggregate(
        total_credit=Sum('amount_due')
    )['total_credit'] or 0

    total_sales = total_cash_sales + total_credit_sales

    total_stock = Stock.objects.aggregate(
        total_quantity=Sum('tonnage')
    )['total_quantity'] or 0

    all_stocks = Stock.objects.all()
    grouped_stocks = {}
    
    for stock in all_stocks:
        if stock.item_name not in grouped_stocks:
            grouped_stocks[stock.item_name] = {
                'name': stock.item_name,
                'branches': {},
                'total_quantity': 0
            }
        
        branch_name = stock.branch_name if stock.branch_name else 'Unknown'
        if branch_name not in grouped_stocks[stock.item_name]['branches']:
            grouped_stocks[stock.item_name]['branches'][branch_name] = 0
        
        grouped_stocks[stock.item_name]['branches'][branch_name] += stock.tonnage
        grouped_stocks[stock.item_name]['total_quantity'] += stock.tonnage

    combined_stocks = list(grouped_stocks.values())
    recent_sales = Sale.objects.all().order_by('-id')[:10]

    context = {
        'total_sales': total_sales,
        'total_cash_sales': total_cash_sales,
        'total_credit_sales': total_credit_sales,
        'total_stock': total_stock,
        'recent_sales': recent_sales,
        'combined_stocks': combined_stocks
    }

    return render(request, 'home/dashboard1.html', context)

@login_required
@user_passes_test(is_salesagent_check)
def salesagent(request):
    total_cash_sales = Sale.objects.filter(method_of_payment='Cash').aggregate(
        total_cash=Sum('amount_received')
    )['total_cash'] or 0

    total_credit_sales = Credit.objects.aggregate(
        total_credit=Sum('amount_due')
    )['total_credit'] or 0 

    total_sales = total_cash_sales + total_credit_sales

    total_stock = Stock.objects.aggregate(
        total_quantity = Sum('tonnage')
    )['total_quantity'] or 0
    context = {
        'total_sales': total_sales,
        'total_cash_sales': total_cash_sales,
        'total_credit_sales': total_credit_sales,
        'total_stock': total_stock,
    }
    return render(request, 'home/dashboard3.html', context)


def credit(request):
    credit = Credit.objects.all().order_by('-id')
    print('Credit Records:', credit)
    return render(request, 'home/credit.html', {'credit': credit})

@login_required
def credit_add(request):
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Credit transaction added successfully!')
            return redirect('/credit/')
        else:
            messages.error(request, 'There was an error adding the credit transaction.')
    else:
        form = CreditForm()
    return render(request, 'home/credit_add.html', {'form': form})

@login_required
def credit_edit(request, pk):
    credit_record = get_object_or_404(Credit, pk=pk)
    if request.method == 'POST':
        form = CreditForm(request.POST, instance=credit_record)
        if form.is_valid():
            form.save()
            return redirect('/credit/')
        else:
            return render(request, 'home/credit_edit.html', {'form': form, 'credit_record': credit_record})
    else:
        form = CreditForm(instance=credit_record)
    return render(request, 'home/credit_edit.html', {'form': form, 'credit_record': credit_record})

@login_required
def credit_delete(request, pk):
    credit_record = get_object_or_404(Credit, pk=pk)
    if request.method == 'POST':
        credit_record.delete()
        return redirect('/credit/')
    return render(request, 'home/credit_delete.html', {'credit_record': credit_record})