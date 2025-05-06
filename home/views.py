from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from django.urls import reverse
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, Q

# Authentication helper functions
def is_owner_check(user):
    """Check if user has owner role"""
    return user.is_owner

def is_manager_check(user):
    """Check if user has manager role"""
    return user.is_manager

def is_salesagent_check(user):
    """Check if user has sales agent role"""
    return user.is_salesagent

def index(request):
    """Landing page view"""
    return render(request, 'home/index.html')

@login_required
@user_passes_test(is_manager_check)
def addstock(request, pk):
    """
    Allow managers to add quantity to existing stock items.
    Validates branch assignment and updates stock quantities.
    """
    issued_item = get_object_or_404(Stock, id=pk)
    
    # Verify the stock belongs to manager's branch
    if issued_item.branch_name != request.user.assigned_branch.branch_name:
        messages.error(request, 'You can only add stock to your assigned branch')
        return redirect('allstock')
        
    if request.method == 'POST':
        form = UpdateStockForm(user=request.user, data=request.POST, instance=issued_item)
        if form.is_valid():
            added_quantity = form.cleaned_data['received_quantity']
            issued_item.tonnage += added_quantity
            issued_item.save()
            messages.success(request, f'Successfully added {added_quantity} units to stock')
            return redirect('allstock')
    else:
        form = UpdateStockForm(user=request.user, instance=issued_item)
            
    return render(request, 'home/addstock.html', {
        'form': form,
        'item': issued_item
    })

@login_required
@user_passes_test(is_salesagent_check)
def addsales(request, pk):
    """
    Record new sales transactions.
    Validates stock availability and updates inventory quantities.
    """
    # Get stock item and verify it belongs to user's branch
    issued_item = get_object_or_404(Stock, id=pk)
    if issued_item.branch_name != request.user.assigned_branch.branch_name:
        messages.error(request, 'You can only add sales for your assigned branch')
        return redirect('allstock')

    if request.method == 'POST':
        sales_form = AddSaleForm(request.POST)
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.product_name = issued_item
            new_sale.unit_price = issued_item.unit_price
            new_sale.salesagent_name = request.user.username

            # Validate stock quantity
            issued_quantity = int(request.POST['tonnage'])
            if issued_quantity > issued_item.tonnage:
                messages.error(request, 'Cannot sell more than available stock')
                return render(request, 'home/addsales.html', {'sales_form': sales_form})

            # Update stock and save sale
            issued_item.tonnage -= issued_quantity
            issued_item.save()
            new_sale.save()
            messages.success(request, 'Sale recorded successfully')
            return redirect('allsales')
    else:
        sales_form = AddSaleForm()
    return render(request, 'home/addsales.html', {'sales_form': sales_form})

def editsales(request, pk):
    """
    Edit existing sales records.
    Validates user permissions and branch assignments.
    """
    tx_to_edit = get_object_or_404(Sale, pk=pk)
    
    # Check if user has permission to edit this sale
    if request.user.is_manager or request.user.is_salesagent:
        if tx_to_edit.product_name.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only edit sales from your assigned branch')
            return redirect('allsales')
    
    # Filter stock items by branch for managers and sales agents
    if request.user.is_manager or request.user.is_salesagent:
        all_stock_items = Stock.objects.filter(branch_name=request.user.assigned_branch.branch_name)
    else:
        all_stock_items = Stock.objects.all()

    if request.method == 'POST':
        try:
            # Update sale details
            stock_instance = Stock.objects.get(id=request.POST.get('product_name'))
            if request.user.is_manager or request.user.is_salesagent:
                if stock_instance.branch_name != request.user.assigned_branch.branch_name:
                    messages.error(request, 'You can only select products from your assigned branch')
                    return render(request, 'home/editsales.html', 
                                {'edit_details': tx_to_edit, 'all_stock_items': all_stock_items})

            # Update sale record with new values
            tx_to_edit.product_name = stock_instance
            tx_to_edit.tonnage = request.POST.get('tonnage')
            tx_to_edit.amount_paid = request.POST.get('amount_paid')
            tx_to_edit.buyers_name = request.POST.get('buyers_name')
            tx_to_edit.date_and_time = request.POST.get('date_and_time')
            tx_to_edit.salesagent_name = request.user.username
            tx_to_edit.method_of_payment = request.POST.get('method_of_payment')
            tx_to_edit.unit_price = request.POST.get('unit_price')
            tx_to_edit.amount_received = request.POST.get('amount_received')
            tx_to_edit.save()
            
            messages.success(request, 'Sale updated successfully')
            return redirect('/view/' + str(tx_to_edit.pk))
        except Stock.DoesNotExist:
            messages.error(request, "Selected product does not exist.")
            return render(request, 'home/editsales.html', 
                        {'edit_details': tx_to_edit, 'all_stock_items': all_stock_items})

    return render(request, 'home/editsales.html', 
                {'edit_details': tx_to_edit, 'all_stock_items': all_stock_items})

@login_required
def viewsales(request, pk):
    """View details of a specific sale"""
    sale = get_object_or_404(Sale, pk=pk)
    
    # Check if user has permission to view this sale
    if request.user.is_manager or request.user.is_salesagent:
        if sale.product_name.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only view sales from your assigned branch')
            return redirect('allsales')
            
    return render(request, 'home/viewsales.html', {'details': sale})

@login_required
def delete(request, pk):
    """Delete a sale record with confirmation"""
    to_delete = get_object_or_404(Sale, pk=pk)
    
    # Check if user has permission to delete this sale
    if request.user.is_manager or request.user.is_salesagent:
        if to_delete.product_name.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only delete sales from your assigned branch')
            return redirect('allsales')
    
    if request.method == 'POST':
        to_delete.delete()
        messages.success(request, 'Sale deleted successfully')
        return redirect('allsales')
        
    return render(request, 'home/delete.html', {'delete_details': to_delete})

@login_required
def receipt(request):
    """
    View all receipts.
    Filters by branch for managers and sales agents.
    """
    if request.user.is_authenticated and (request.user.is_manager or request.user.is_salesagent):
        sales = Sale.objects.filter(
            product_name__branch_name=request.user.assigned_branch.branch_name
        ).order_by('-id')
    else:
        sales = Sale.objects.all().order_by('-id')
    return render(request, 'home/receipt.html', {'sales': sales})

@login_required
def receipt_detail(request, receipt_id):
    """View details of a specific receipt"""
    receipt = get_object_or_404(Sale, id=receipt_id)
    
    # Check if user has permission to view this receipt
    if request.user.is_manager or request.user.is_salesagent:
        if receipt.product_name.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only view receipts from your assigned branch')
            return redirect('receipt')
            
    return render(request, 'home/receipt_detail.html', {'receipt': receipt})

@login_required
def all_stock(request):
    """
    View all stock items.
    Filters by branch for managers and sales agents.
    """
    if request.user.is_authenticated and (request.user.is_manager or request.user.is_salesagent):
        stock = Stock.objects.filter(
            branch_name=request.user.assigned_branch.branch_name
        ).order_by('-id')
    else:
        stock = Stock.objects.all().order_by('-id')
    return render(request, 'home/allstock.html', {'stock': stock})

@login_required
def all_sales(request):
    """
    View all sales records.
    Filters by branch for managers and sales agents.
    """
    if request.user.is_manager or request.user.is_salesagent:
        sales = Sale.objects.filter(
            product_name__branch_name=request.user.assigned_branch.branch_name
        ).order_by('-id')
    else:
        sales = Sale.objects.all().order_by('-id')
    return render(request, 'home/allsales.html', {'sales': sales})

@login_required
def stock_detail(request, stock_id):
    """View details of a specific stock item"""
    stock = get_object_or_404(Stock, id=stock_id)
    
    # Check if user has permission to view this stock
    if request.user.is_manager or request.user.is_salesagent:
        if stock.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only view stock from your assigned branch')
            return redirect('allstock')
            
    return render(request, 'home/detail.html', {'stock': stock})

def logout_view(request):
    """Handle user logout"""
    if request.method == 'POST':
        logout(request)
        return redirect('/')
    return render(request, 'home/logout.html')

def Login(request):
    """
    Handle user login.
    Redirects to appropriate dashboard based on user role.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user role
                if user.is_manager:
                    return redirect('/dashboard2/')
                elif user.is_salesagent:
                    return redirect('/dashboard3/')
                else:
                    return redirect('/dashboard1/')
    else:
        form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form})

def signup(request):
    """
    Handle user registration.
    Validates role-specific requirements and branch assignments.
    """
    if request.method == 'POST':
        form = UserCreation(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Ensure only one role is selected
            roles = [user.is_manager, user.is_salesagent, user.is_owner]
            if roles.count(True) != 1:
                messages.error(request, 'Please select exactly one role (Manager, Sales Agent, or Owner)')
                return render(request, 'home/signup.html', {'form': form})
            
            # Validate branch assignment for managers and sales agents
            if user.is_manager or user.is_salesagent:
                if not user.assigned_branch:
                    messages.error(request, f'Branch assignment is required for {"managers" if user.is_manager else "sales agents"}')
                    return render(request, 'home/signup.html', {'form': form})
                
                if user.is_manager:
                    # Check if another manager exists for this branch
                    existing_manager = Userprofile.objects.filter(
                        is_manager=True,
                        assigned_branch=user.assigned_branch
                    ).exists()
                    
                    if existing_manager:
                        messages.error(request, f'A manager already exists for {user.assigned_branch.branch_name}')
                        return render(request, 'home/signup.html', {'form': form})
                
                if user.is_salesagent:
                    # Check number of existing sales agents for this branch
                    existing_agents = Userprofile.objects.filter(
                        is_salesagent=True,
                        assigned_branch=user.assigned_branch
                    ).count()
                    
                    if existing_agents >= 2:
                        messages.error(request, f'Branch {user.assigned_branch.branch_name} already has the maximum number of sales agents (2)')
                        return render(request, 'home/signup.html', {'form': form})
            
            user.save()
            messages.success(request, f'Account created for {user.username}')
            return redirect('/login/')
    else:
        form = UserCreation()
    return render(request, 'home/signup.html', {'form': form})

@login_required
@user_passes_test(is_manager_check)
def manager(request):
    """
    Manager dashboard view.
    Shows sales statistics and low stock alerts for manager's branch.
    """
    # Get the manager's assigned branch
    manager_branch = request.user.assigned_branch
    if not manager_branch:
        messages.error(request, 'No branch assigned to this manager')
        return redirect('/')

    # Calculate statistics for the branch
    total_cash_sales = Sale.objects.filter(
        product_name__branch_name=manager_branch.branch_name,
        method_of_payment='Cash'
    ).aggregate(
        total_cash=Sum('amount_received')
    )['total_cash'] or 0

    total_credit_sales = Credit.objects.filter(
        branch_name=manager_branch.branch_name
    ).aggregate(
        total_credit=Sum('amount_due')
    )['total_credit'] or 0 

    total_sales = total_cash_sales + total_credit_sales

    total_stock = Stock.objects.filter(
        branch_name=manager_branch.branch_name
    ).aggregate(
        total_quantity=Sum('tonnage')
    )['total_quantity'] or 0

    low_stock_items = Stock.objects.filter(
        branch_name=manager_branch.branch_name,
        tonnage__lt=200
    )

    context = {
        'total_sales': total_sales,
        'total_cash_sales': total_cash_sales,
        'total_credit_sales': total_credit_sales,
        'total_stock': total_stock,
        'low_stock_items': low_stock_items,
        'branch_name': manager_branch.branch_name
    }
    return render(request, 'home/dashboard2.html', context)

@login_required
@user_passes_test(is_owner_check)
def owner(request):
    """
    Owner dashboard view.
    Shows company-wide statistics and stock levels across all branches.
    """
    # Get all branches
    branches = Branch.objects.all()
    branch_stats = {}
    
    # Calculate stats for each branch
    for branch in branches:
        cash_sales = Sale.objects.filter(
            product_name__branch_name=branch.branch_name,
            method_of_payment='Cash'
        ).aggregate(
            total_cash=Sum('amount_received')
        )['total_cash'] or 0
        
        credit_sales = Credit.objects.filter(
            branch_name=branch.branch_name
        ).aggregate(
            total_credit=Sum('amount_due')
        )['total_credit'] or 0
        
        total_stock = Stock.objects.filter(
            branch_name=branch.branch_name
        ).aggregate(
            total_quantity=Sum('tonnage')
        )['total_quantity'] or 0
        
        branch_stats[branch.branch_name] = {
            'cash_sales': cash_sales,
            'credit_sales': credit_sales,
            'total_sales': cash_sales + credit_sales,
            'total_stock': total_stock
        }
    
    # Calculate company-wide totals
    total_cash_sales = sum(stats['cash_sales'] for stats in branch_stats.values())
    total_credit_sales = sum(stats['credit_sales'] for stats in branch_stats.values())
    total_sales = total_cash_sales + total_credit_sales
    total_stock = sum(stats['total_stock'] for stats in branch_stats.values())

    # Group stocks by item name across branches
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
    low_stock_items = Stock.objects.filter(tonnage__lt=200)

    context = {
        'total_sales': total_sales,
        'total_cash_sales': total_cash_sales,
        'total_credit_sales': total_credit_sales,
        'total_stock': total_stock,
        'recent_sales': recent_sales,
        'combined_stocks': combined_stocks,
        'low_stock_items': low_stock_items,
        'branch_stats': branch_stats,
    }
    return render(request, 'home/dashboard1.html', context)

@login_required
@user_passes_test(is_salesagent_check)
def salesagent(request):
    """
    Sales agent dashboard view.
    Shows sales statistics for the agent's branch.
    """
    # Get the sales agent's assigned branch
    agent_branch = request.user.assigned_branch
    if not agent_branch:
        messages.error(request, 'No branch assigned to this sales agent')
        return redirect('/')

    # Calculate statistics for the branch
    total_cash_sales = Sale.objects.filter(
        product_name__branch_name=agent_branch.branch_name,
        method_of_payment='Cash'
    ).aggregate(
        total_cash=Sum('amount_received')
    )['total_cash'] or 0

    total_credit_sales = Credit.objects.filter(
        branch_name=agent_branch.branch_name
    ).aggregate(
        total_credit=Sum('amount_due')
    )['total_credit'] or 0 

    total_sales = total_cash_sales + total_credit_sales

    total_stock = Stock.objects.filter(
        branch_name=agent_branch.branch_name
    ).aggregate(
        total_quantity=Sum('tonnage')
    )['total_quantity'] or 0

    low_stock_items = Stock.objects.filter(
        branch_name=agent_branch.branch_name,
        tonnage__lt=200
    )

    context = {
        'total_sales': total_sales,
        'total_cash_sales': total_cash_sales,
        'total_credit_sales': total_credit_sales,
        'total_stock': total_stock,
        'low_stock_items': low_stock_items,
        'branch_name': agent_branch.branch_name
    }
    return render(request, 'home/dashboard3.html', context)

@login_required
def credit(request):
    """
    View credit transactions.
    Filters by branch for managers and sales agents.
    """
    if request.user.is_authenticated and (request.user.is_manager or request.user.is_salesagent):
        credit = Credit.objects.filter(
            branch_name=request.user.assigned_branch.branch_name
        ).order_by('-id')
    else:
        credit = Credit.objects.all().order_by('-id')
    return render(request, 'home/credit.html', {'credit': credit})

@login_required
def credit_add(request):
    """Add a new credit transaction"""
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            credit = form.save(commit=False)
            # Set the branch name based on the user's assigned branch
            if request.user.assigned_branch:
                credit.branch_name = request.user.assigned_branch.branch_name
            credit.save()
            messages.success(request, 'Credit transaction added successfully!')
            return redirect('/credit/')
        else:
            messages.error(request, 'There was an error adding the credit transaction.')
    else:
        form = CreditForm()
    return render(request, 'home/credit_add.html', {'form': form})

@login_required
def credit_edit(request, pk):
    """Edit an existing credit transaction"""
    credit_record = get_object_or_404(Credit, pk=pk)
    
    # Check if user has permission to edit this credit record
    if request.user.is_manager or request.user.is_salesagent:
        if credit_record.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only edit credit records from your assigned branch')
            return redirect('/credit/')

    if request.method == 'POST':
        form = CreditForm(request.POST, instance=credit_record)
        if form.is_valid():
            credit = form.save(commit=False)
            # Ensure branch name doesn't change
            if request.user.assigned_branch:
                credit.branch_name = request.user.assigned_branch.branch_name
            credit.save()
            messages.success(request, 'Credit record updated successfully')
            return redirect('/credit/')
        else:
            messages.error(request, 'There was an error updating the credit record')
    else:
        form = CreditForm(instance=credit_record)
    return render(request, 'home/credit_edit.html', {'form': form})

@login_required
def credit_view(request, pk):
    """View details of a credit transaction"""
    credit_record = get_object_or_404(Credit, pk=pk)
    
    # Check if user has permission to view this credit record
    if request.user.is_manager or request.user.is_salesagent:
        if credit_record.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only view credit records from your assigned branch')
            return redirect('/credit/')
            
    return render(request, 'home/credit_view.html', {'item': credit_record})

@login_required
def credit_delete(request, pk):
    """Delete a credit transaction with confirmation"""
    credit_record = get_object_or_404(Credit, pk=pk)
    
    # Check if user has permission to delete this credit record
    if request.user.is_manager or request.user.is_salesagent:
        if credit_record.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only delete credit records from your assigned branch')
            return redirect('/credit/')
            
    if request.method == 'POST':
        credit_record.delete()
        messages.success(request, 'Credit record deleted successfully')
        return redirect('/credit/')
    return render(request, 'home/credit_delete.html', {'credit_record': credit_record})

@login_required
def issue_item(request, pk):
    """
    Issue/sell an item from stock.
    Validates stock availability and updates quantities.
    """
    issued_item = get_object_or_404(Stock, id=pk)
    
    # Check if user has permission to issue this item
    if request.user.is_manager or request.user.is_salesagent:
        if issued_item.branch_name != request.user.assigned_branch.branch_name:
            messages.error(request, 'You can only issue items from your assigned branch')
            return redirect('allstock')

    if request.method == 'POST':
        sales_form = AddSaleForm(user=request.user, data=request.POST)
        if sales_form.is_valid():
            new_sale = sales_form.save(commit=False)
            new_sale.product_name = issued_item
            new_sale.item_name = issued_item.item_name
            new_sale.salesagent_name = request.user.username
            
            issued_quantity = int(sales_form.cleaned_data['tonnage'])
            if issued_quantity > issued_item.tonnage:
                messages.error(request, 'Cannot sell more than available stock')
                return render(request, 'home/issue_item.html', {'sales_form': sales_form})

            # Update stock and save sale
            issued_item.tonnage -= issued_quantity
            issued_item.save()
            new_sale.save()
            
            messages.success(request, 'Item issued successfully')
            return redirect('receipt')
    else:
        sales_form = AddSaleForm(user=request.user)
        
    return render(request, 'home/issue_item.html', {'sales_form': sales_form, 'item': issued_item})