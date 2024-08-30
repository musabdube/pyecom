from django.shortcuts import get_object_or_404, render
from .models import Product
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Category
from .models import Cart, Order, OrderItem
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum

def product_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(name__icontains=query)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    categories = Category.objects.all()
    
    return render(request, 'shop/product_list.html', {'products': products, 'categories': categories})
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = SignUpForm()
    return render(request, 'shop/signup.html', {'form': form})

def profile(request):
    return render(request, 'shop/profile.html')

def logout_confirm(request):
    return render(request, 'shop/logout_confirm.html')

def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)

    if product.stock > 0:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += 1
        
        product.stock -= 1  # Decrease the stock
        product.save()  # Save the product with the updated stock
        
        cart_item.save()

        # Update session with the new cart item count
        request.session['cart_item_count'] = cart.items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        messages.success(request, 'Product added to cart successfully!')
    else:
        messages.error(request, 'Sorry, this product is out of stock.')

    return redirect('cart_detail')


def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_items = sum(item.quantity for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': total_items,
    }
    
    return render(request, 'shop/cart_detail.html', context)
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart_detail')

def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product = cart_item.product
    new_quantity = int(request.POST.get('quantity'))

    if new_quantity > cart_item.quantity:  # Increasing quantity
        difference = new_quantity - cart_item.quantity
        if product.stock >= difference:
            product.stock -= difference
            cart_item.quantity = new_quantity
            product.save()
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        else:
            messages.error(request, 'Sorry, there is not enough stock available.')
    elif new_quantity < cart_item.quantity:  # Decreasing quantity
        difference = cart_item.quantity - new_quantity
        product.stock += difference
        cart_item.quantity = new_quantity
        product.save()
        cart_item.save()
        messages.success(request, 'Cart updated successfully!')
    else:
        messages.info(request, 'No changes were made to the cart.')

    return redirect('cart_detail')
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    if request.method == 'POST':
        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=cart.get_total_cost(),
            payment_status='pending'  # Mark the order as pending until admin approval
        )
        
        for item in cart.cartitem_set.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear the cart
        cart.cartitem_set.all().delete()

        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'checkout.html', {'cart': cart})

@user_passes_test(lambda u: u.is_superuser)
def approve_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
        return redirect('admin_order_list')
    return render(request, 'shop/admin_approve_order.html', {'order': order})

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_confirmation.html', {'order': order})

def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_list.html', {'orders': orders})

def place_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    order = Order(user=request.user)
    order.total_price = cart.get_total_cost()  # Calculate the total price
    order.save()

    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
    cart.items.all().delete()
    request.session['cart_item_count'] = 0  
    return redirect('order_confirmation', order_id=order.id)

@user_passes_test(lambda u: u.is_staff)
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'shop/order_list.html', {'orders': orders})

@user_passes_test(lambda u: u.is_staff)
def reject_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = 'REJECTED'
        order.save()
        return redirect('order_list')
    return render(request, 'shop/reject_order.html', {'order': order})

def admin_order_list(request):
    orders = Order.objects.all()
    return render(request, 'shop/admin_order_list.html', {'orders': orders})

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(featured=True)  
    products = Product.objects.all()[:8]  

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'products': products,
    }
    return render(request, 'shop/home.html', context)

def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'shop/product_list.html', context)

def cart_add(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity'))
    if product.stock >= quantity:
        product.stock -= quantity
        product.save()
        if str(product.id) in cart:
            cart[str(product.id)] += quantity
        else:
            cart[str(product.id)] = quantity
        request.session['cart'] = cart
    return redirect('cart_detail')