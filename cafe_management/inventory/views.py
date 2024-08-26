# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Item, Bill, BillItem
from django.utils import timezone
from django.db.models import Q
from django.utils.dateparse import parse_date
from decimal import Decimal, InvalidOperation

@login_required
def home(request):
    categories = Category.objects.all()  # Get all categories
    category_id = request.GET.get('category')  # Get the selected category from the URL
    
    if category_id:
        items = Item.objects.filter(category_id=category_id).order_by('price') # Filter items by category
        selected_category = Category.objects.get(id=category_id)
        selected_category_name = selected_category.name
    else:
        items_by_category = {}  # Dictionary to hold items grouped by category
        for category in categories:
            items_by_category[category] = Item.objects.filter(category=category).order_by('price')
        selected_category_name = "All Items"
    
    context = {
        'categories': categories,
        'items_by_category': items_by_category if not category_id else None,
        'items': items if category_id else None,
        'selected_category_name': selected_category_name,
    }
    return render(request, 'home.html', context)


@login_required
def create_bill(request):
    items = Item.objects.all()
    
    if request.method == 'POST':
        customer_name = request.POST['customer_name']
        item_ids = request.POST.getlist('items')
        quantities = request.POST.getlist('quantities')
        extra_items = request.POST.get('extra_items', '') 
        extra_amount = request.POST.get('extra_amount', 0)
        print("Extra amount:- ",extra_amount)
        try:
            extra_amount = Decimal(extra_amount)
        except InvalidOperation:
            extra_amount = Decimal('0')  # Default to 0 if conversion fails

        # Step 1: Validate stock quantities before creating the bill
        for item_id, quantity in zip(item_ids, quantities):
            item = Item.objects.get(id=item_id)
            quantity = int(quantity)

            if item.inventory_managed:
                if item.stock_quantity < quantity:
                    # If not enough stock, render the form with an error message
                    return render(request, 'create_bill.html', {
                        'items': items,
                        'error_message': f"Not enough stock for {item.name}. Available stock: {item.stock_quantity}"
                    })

        # Step 2: Create the bill after all items are validated
        total_amount = Decimal('0')
        bill = Bill.objects.create(
            customer_name=customer_name,
            user=request.user,  # The logged-in user
            total_amount=0,  # Placeholder, will be updated after adding items
            date_created=timezone.now(),
            extra_items=extra_items,  # Save extra items description
            extra_amount=extra_amount
        )

        # Step 3: Deduct stock quantities and create BillItems
        for item_id, quantity in zip(item_ids, quantities):
            item = Item.objects.get(id=item_id)
            quantity = int(quantity)

            if item.inventory_managed:
                item.stock_quantity -= quantity  # Deduct the quantity from stock
                item.save()

            BillItem.objects.create(
                bill=bill,
                item=item,
                quantity=quantity
            )
            total_amount += item.price * quantity

         # Step 4: Add extra amount to the total and update the total amount of the bill
        total_amount += extra_amount
        bill.total_amount = total_amount
        bill.save()

        return redirect('create_bill')

    context = {
        'items': items,
    }
    return render(request, 'create_bill.html', context)


from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
@login_required
def previous_bills(request):
    bills = Bill.objects.all().order_by('-date_created')
    search_query = request.GET.get('search')
    search_date_query = request.GET.get('search_date')

    if search_query and search_date_query:
        # If both name and date are provided, filter by both
        date_query = parse_date(search_date_query)
        if date_query:
            bills = bills.filter(
                Q(customer_name__icontains=search_query) &
                Q(date_created__date=date_query)
            )
        else:
            bills = bills.filter(customer_name__icontains=search_query)
    elif search_query:
        # If only the name is provided
        bills = bills.filter(customer_name__icontains=search_query)
    elif search_date_query:
        # If only the date is provided
        date_query = parse_date(search_date_query)
        if date_query:
            bills = bills.filter(date_created__date=date_query)

    # Pagination
    paginator = Paginator(bills, 10)  # Show 10 bills per page
    page = request.GET.get('page')
    
    try:
        bills = paginator.page(page)
    except PageNotAnInteger:
        bills = paginator.page(1)  # If page is not an integer, deliver first page
    except EmptyPage:
        bills = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page

    context = {
        'bills': bills,
    }
    return render(request, 'previous_bills.html', context)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')
