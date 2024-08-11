from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import F

from shop.forms import OrderForm
from shop.models import Cart, Category,  Product
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    products = Product.objects.order_by('-pub_date')
    categories = Category.objects.all()
    context = {'products': products, 'categories': categories}

    return render(request, 'shop/index.html', context)


def show_category(request, category_id):
    categories = Category.objects.all()
    category = Category.objects.get(pk=category_id)
    products = Product.objects.filter(category=category).order_by('pub_date')
    lank_products = Product.objects.filter(category=category).order_by('-hit')[:4]
    paginator = Paginator(products, 5)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context = {'lank_products': lank_products, 'products': products, 'category': category, 'categories': categories}
    return render(request, 'shop/category.html', context)

def product_detail(request, pk):
    categories = Category.objects.all()
    product = Product.objects.get(pk=pk)
    category = Category.objects.get(pk=product.category.pk)
    Product.objects.filter(pk=pk).update(hit=product.hit+1)
    quantity_list = []
    for i in range(1, product.quantity) :
        quantity_list.append(i)
    context = {"quantity_list": quantity_list, "product": product, "category": category, "categories": categories}
    return render(request, 'shop/product_detail.html', context)

@login_required
def cart(request, pk):
    categories = Category.objects.all()
    user = User.objects.get(pk=pk)
    cart = Cart.objects.filter(user=user)
    paginator = Paginator(cart, 10)
    page = request.GET.get('page')
    try:
        cart = paginator.page(page)
    except PageNotAnInteger:
        cart = paginator.page(1)
    except EmptyPage:
        cart = paginator.page(paginator.num_pages)
    context = {'user': user, 'cart': cart, 'categories': categories}
    return render(request, 'shop/cart.html', context)

@login_required
def delete_cart(request, pk):  # cart 내에서 상품을 지우는 함수
    # section 4
    user = request.user
    cart = Cart.objects.filter(user=user)
    quantity = 0

    if request.method == "POST":
        check_none = request.POST.get("product")
        if not check_none:
            return redirect("shop:cart", user.pk)

        pk = int(request.POST.get("product"))
        product = Product.objects.get(pk=pk)
        for i in cart:
            if i.products == product:
                quantity = i.quantity

        if quantity > 0:
            product = Product.objects.filter(pk=pk)
            cart = Cart.objects.filter(user=user, products__in=product)
            cart.delete()
            return redirect("shop:cart", user.pk)
        
@login_required  # 장바구니에 상품 추가
def add_to_cart(request, pk): # section 4
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        product = Product.objects.get(pk=pk)
        user = request.user

        cart_item = Cart.objects.filter(user=user, products=product)
        if cart_item:
            cart_item.update(quantity=F("quantity") + quantity)
        else:
            Cart.objects.create(user=user, products=product, quantity=quantity)

        messages.success(request, "Added to cart successfully.")
        return redirect("shop:cart", user.pk)
    
@login_required
def pay(request, pk):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(pk=pk)
        user = request.user
        categories = Category.objects.all()
        initial = {'name': product.name, 'amount': product.price, 'quantity': quantity}

        form = OrderForm(request.POST, initial=initial)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.quantity = quantity
            order.products = product
            order.save()
            return redirect('shop:order_list', user.pk)
        else:
            form = OrderForm(initial=initial)

        return render(request, 'shop/order_pay.html', {
            'form': form,
            'quantity': quantity,
            'iamport_shop_id': 'iamport', 
            'user': user,
            'product': product,
            'categories': categories,
        })