from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F

from shop.forms import OrderForm
from shop.models import Cart, Category, Product
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    products = Product.objects.order_by("-pub_date")
    categories = Category.objects.all()
    context = {"products": products, "categories": categories}

    return render(request, "shop/index.html", context)


def show_category(request, category_id):
    categories = Category.objects.all()
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category).order_by("pub_date")
    lank_products = Product.objects.filter(category=category).order_by("-hit")[:4]
    paginator = Paginator(products, 5)
    page = request.GET.get("page")
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context = {
        "lank_products": lank_products,
        "products": products,
        "category": category,
        "categories": categories,
    }
    return render(request, "shop/category.html", context)


def product_detail(request, pk):
    categories = Category.objects.all()
    product = get_object_or_404(Product, pk=pk)
    category = get_object_or_404(Category, pk=product.category.pk)
    Product.objects.filter(pk=pk).update(hit=F("hit") + 1)
    quantity_list = list(range(1, product.quantity))
    context = {
        "quantity_list": quantity_list,
        "product": product,
        "category": category,
        "categories": categories,
    }
    return render(request, "shop/product_detail.html", context)


@login_required
def cart(request, pk):
    categories = Category.objects.all()
    user = get_object_or_404(User, pk=pk)
    cart_items = Cart.objects.filter(user=user)
    paginator = Paginator(cart_items, 10)
    page = request.GET.get("page")
    try:
        cart_items = paginator.page(page)
    except PageNotAnInteger:
        cart_items = paginator.page(1)
    except EmptyPage:
        cart_items = paginator.page(paginator.num_pages)
    context = {"user": user, "cart": cart_items, "categories": categories}
    return render(request, "shop/cart.html", context)


@login_required
def delete_cart(request, pk):  # cart 내에서 상품을 지우는 함수
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    quantity = 0

    if request.method == "POST":
        check_none = request.POST.get("product")
        if not check_none:
            return redirect("shop:cart", user.pk)

        pk = int(request.POST.get("product"))
        product = get_object_or_404(Product, pk=pk)
        for item in cart_items:
            if item.products == product:
                quantity = item.quantity

        if quantity > 0:
            Cart.objects.filter(user=user, products=product).delete()
            return redirect("shop:cart", user.pk)


@login_required
def add_to_cart(request, product_id):  # 장바구니에 상품 추가
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        product = get_object_or_404(Product, pk=product_id)
        user = request.user

        cart_item = Cart.objects.filter(user=user, products=product)
        if cart_item.exists():
            cart_item.update(quantity=min(F("quantity") + quantity, product.quantity))
        else:
            Cart.objects.create(user=user, products=product, quantity=quantity)

        messages.success(request, "Added to cart successfully.")
        return redirect("shop:cart", user.pk)


@login_required
def pay(request, pk):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        product = get_object_or_404(Product, pk=pk)
        user = request.user
        categories = Category.objects.all()
        initial = {"name": product.name, "amount": product.price, "quantity": quantity}

        form = OrderForm(request.POST, initial=initial)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.quantity = quantity
            order.products = product
            order.save()
            return redirect("shop:order_list", user.pk)
        else:
            form = OrderForm(initial=initial)

        return render(
            request,
            "shop/order_pay.html",
            {
                "form": form,
                "quantity": quantity,
                "iamport_shop_id": "iamport",
                "user": user,
                "product": product,
                "categories": categories,
            },
        )
