from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from shop.forms import OrderForm
from shop.models import Cart, Category,  Product


def user_verification(func):
    def wrap(request, *args, **kwargs):
        session_user = User.objects.get(pk=kwargs['pk'])
        request_user = request.user

        if session_user != request_user:
            return HttpResponseForbidden()

        return func(request, *args, **kwargs)
    return wrap

from shop.models import Cart, Category, Product
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def index(request):
    categories = Category.objects.all()
    products = Product.objects.order_by('-pub_date')

    context = {
        "categories": categories,
        "products": products,
    }
    products = Product.objects.order_by("-pub_date")
    categories = Category.objects.all()
    context = {"products": products, "categories": categories}

    return render(request, "shop/index.html", context)


def show_category(request, category_id):
    categories = Category.objects.all()
    category = Category.objects.get(id=category_id)

    products = Product.objects.filter(category=category)
    sorted_products = products.order_by('pub_date')
    ranked_products = products.order_by('-hit')[:4]

    page = int(request.GET.get('page', 1))
    paginator = Paginator(sorted_products, 5)
    products = paginator.page(page)

    # TODO: 랭킹 할 때는 rank입니다. html 부분 수정 필요.
    context = {
        "categories": categories,
        "category": category,
        "products": products,
        "lank_products": ranked_products,
    }

    return render(request, "shop/category.html", context)


def product_detail(request, product_id):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)

    product.hit += 1
    product.save()
    quantity_list = list(range(1, product.quantity + 1))

    context = {
        "quantity_list": quantity_list,
        "product": product,
        "category": product.category,
        "categories": categories
    }

    return render(request, 'shop/product_detail.html', context)
  
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
def view_cart(request, pk):
    categories = Category.objects.all()
    user = User.objects.get(pk=pk)
    cart_list = Cart.objects.filter(user=user)

    page = int(request.GET.get('page', 1))
    paginator = Paginator(cart_list, 10)
    cart = paginator.page(page)

    context = {
        "user": user,
        "cart": cart,
        "categories": categories
    }

    return render(request, 'shop/cart.html', context)

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

@login_required
def delete_cart(request, pk):
    if request.method == "POST":
        user = request.user
        product_id = request.POST.get("product")

        if product_id:
            product = Product.objects.get(id=int(product_id))
            Cart.objects.get(user=user, products=product).delete()

        return redirect("shop:cart", user.pk)


@login_required
def add_to_cart(request, pk):
    if request.method == "POST":
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
        product = Product.objects.get(pk=pk)
        quantity = int(request.POST.get("quantity"))
        cart_item = Cart.objects.filter(user=user, products=product).first()

        if cart_item:
            cart_item.quantity = min(cart_item.quantity + quantity, product.quantity)
            cart_item.save()
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


        initial = {
            "name": product.name,
            "amount": product.price,
            "quantity": quantity
        }

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


        context = {
            'form': form,
            'quantity': quantity,
            'iamport_shop_id': 'iamport',
            'user': user,
            'product': product,
            'categories': categories,
        }

        return render(request, 'shop/order_pay.html', context)

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

