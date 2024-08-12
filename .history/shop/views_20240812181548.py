from django.contrib import messages
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required

from shop.forms import OrderForm
from shop.models import Cart, Category, Product
from django.contrib.auth.models import User


PRODUCTS_PER_PAGE = 5
CART_ITEMS_PER_PAGE = 10


def index(request):
    products = Product.objects.order_by('-pub_date')
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'shop/index.html', context)


def show_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category).order_by('pub_date')
    lank_products = Product.objects.filter(category=category).order_by('-hit')[:4]
    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page = request.GET.get('page')
    
    products = paginate_queryset(paginator, page)
    
    context = {
        'lank_products': lank_products,
        'products': products,
        'category': category,
        'categories': Category.objects.all()
    }
    return render(request, 'shop/category.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    category = get_object_or_404(Category, pk=product.category.pk)
    Product.objects.filter(pk=pk).update(hit=F('hit') + 1)
    quantity_list = list(range(1, product.quantity))
    context = {
        'quantity_list': quantity_list,
        'product': product,
        'category': category,
        'categories': Category.objects.all()
    }
    return render(request, 'shop/product_detail.html', context)


@login_required
def cart(request, pk):
    user = get_object_or_404(User, pk=pk)
    cart_items = Cart.objects.filter(user=user)
    paginator = Paginator(cart_items, CART_ITEMS_PER_PAGE)
    page = request.GET.get('page')
    
    cart_items = paginate_queryset(paginator, page)
    
    context = {
        'user': user,
        'cart': cart_items,
        'categories': Category.objects.all()
    }
    return render(request, 'shop/cart.html', context)


@login_required
def delete_cart(request, pk):
    user = request.user
    if request.method == "POST":
        product_id = request.POST.get("product")
        if not product_id:
            return redirect("shop:cart", user.pk)

        product = get_object_or_404(Product, pk=int(product_id))
        Cart.objects.filter(user=user, products=product).delete()
        return redirect("shop:cart", user.pk)


@login_required
def add_to_cart(request, pk):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        product = get_object_or_404(Product, pk=pk)
        user = request.user

        cart_item, created = Cart.objects.get_or_create(user=user, products=product)
        if not created:
            cart_item.quantity = F("quantity") + quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        messages.success(request, "Added to cart successfully.")
        return redirect("shop:cart", user.pk)


@login_required
def pay(request, pk):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        product = get_object_or_404(Product, pk=pk)
        user = request.user
        initial = {
            'name': product.name,
            'amount': product.price,
            'quantity': quantity
        }

        form = OrderForm(request.POST, initial=initial)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.quantity = quantity
            order.products = product
            order.save()
            return redirect('shop:order_list', user.pk)
        
        return render(request, 'shop/order_pay.html', {
            'form': form,
            'quantity': quantity,
            'iamport_shop_id': 'iamport',
            'user': user,
            'product': product,
            'categories': Category.objects.all()
        })


def paginate_queryset(paginator, page):
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
