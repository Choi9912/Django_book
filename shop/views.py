from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from shop.forms import OrderForm
from shop.models import Cart, Category, Product


# Section 2 심화 학습
# # 로그인한 유저 정보와 HTTP로 요청한 유저 정보가 같은지 확인하는 함수
def user_verification(func):
    def wrap(request, *args, **kwargs):
        session_user = User.objects.get(pk=kwargs["pk"])
        request_user = request.user

        if session_user != request_user:
            return HttpResponseForbidden()

        return func(request, *args, **kwargs)

    return wrap


# 주소창 함수
def index(request):
    # models.py의 Product 객쳉 [(-)pub_date] 내림차순으로 큰순서로 product에 넣는다.
    products = Product.objects.order_by("-pub_date")
    # models.py 쿼리셋 Category 객체를 all() 전부 categories에 넣는다.
    categories = Category.objects.all()
    # 위 product를 조회수 큰순서로 4번째 까지 ranked_products에 넣는다.
    ranked_products = products.order_by("-hit")[:4]

    context = {
        "products": products,
        "categories": categories,
        "ranked_products": ranked_products,
    }

    return render(request, "shop/index.html", context)


# Section3 # 카테로리를 눌렀을 때 나오는 때 나오는 함수
def show_category(request, category_id):
    categories = Category.objects.all()
    # 카테고리 쿼리셋에서 category_id에 해당하는 쿼리만을 가져옴
    category = categories.get(id=category_id)
    # Product모델에서 변수로 지정한 category에 해당하는 것만 필터링해서 쿼리셋으로 가져옴
    products = Product.objects.filter(category=category)
    sorted_products = products.order_by("pub_date")
    ranked_products = products.order_by("-hit")[:4]

    # 페이지네이션 예외 처리하는 부분
    try:
        # GET방식으로 가져온 데이터에서 "page" 키가 있는 경우 "page" 키에 해당하는 값으로 page를 설정
        # "page"가 없으면 page <- 1
        page = int(request.GET.get("page", 1))
    # "page"에 숫자가 아닌 값이 들어가 있을 경우 page <- 1
    except ValueError:
        page = 1

    paginator = Paginator(sorted_products, 8)
    products = paginator.get_page(page)

    context = {
        "categories": categories,
        "category": category,
        "products": products,
        "ranked_products": ranked_products,
    }

    return render(request, "shop/category.html", context)


# Section3 # 상품의 상세 화면을 보여주는 함수
def product_detail(request, product_id):
    # 쿼리셋 Category 객체를 all() 전부 categories에 넣는다.
    categories = Category.objects.all()
    # 쿼리셋 Product 객체에서 id를 사용하여 제품을 비교한다 없으면 404 오류를 발생
    product = get_object_or_404(Product, id=product_id)

    # 조회수 1씩 늘려줌
    product.hit += 1
    # 데이터 베이스에 저장
    product.save()
    # 수량리스트 제품의 수량에 따라 1 부터 제품 수까지의 리스트를 생성 (재고의 개념)
    quantity_list = list(range(1, product.quantity + 1))

    context = {
        "quantity_list": quantity_list,
        "product": product,
        "category": product.category,
        "categories": categories,
    }
    # 컨텍스트를 html 템플리에 랜더링
    return render(request, "shop/product_detail.html", context)


# 로그인이 되어있지 않으면 아래 함수가 실행되지 않음
# 로그인 없이 실행하면 "accounts/login/"으로 리다이렉트 시킴
@login_required
# 장바구니를 보여주는 함수
# pk => user_id
def view_cart(request, pk):
    categories = Category.objects.all()
    # user_id에 해당하는 쿼리를 가져옴
    user = User.objects.get(pk=pk)
    # Cart 데이터 중 변수user에 해당하는 쿼리셋을 가져옴
    cart_list = Cart.objects.filter(user=user)
    # 상품들 가격의 총합을 구하는 함수
    item_price_sum = sum(
        map(lambda item: item.quantity * item.products.price, cart_list)
    )
    # 페이지네이션 예외 처리하는 부분
    try:
        # GET방식으로 가져온 데이터에서 "page" 키가 있는 경우 "page" 키에 해당하는 값으로 page를 설정
        # "page"가 없으면 page <- 1
        page = int(request.GET.get("page", 1))
        # "page"에 숫자가 아닌 값이 들어가 있을 경우 page
    except ValueError:
        page = 1

    paginator = Paginator(cart_list, 10)
    cart = paginator.get_page(page)

    context = {
        "user": user,
        "cart": cart,
        "categories": categories,
        "item_price_sum": item_price_sum,
    }

    return render(request, "shop/cart.html", context)


# 로그인이 되어있지 않으면 아래 함수가 실행되지 않음
# 로그인 없이 실행하면 "accounts/login/"으로 리다이렉트 시킴
@login_required
# 카트 삭제 함수
# pk => user_id
def delete_cart(request, pk):
    # 요청 방식이 POST인지 확인
    if request.method == "POST":
        # 현재 사용자 요청 확인
        user = request.user
        # POST 요청에서 product 로 전달된 제품 id를 가져옴
        product_id = request.POST.get("product")

        # 제품 id 확인
        if product_id:
            # 해당 id를 가진 제품객체를 데이터베이스에서 가져옴
            product = Product.objects.get(id=int(product_id))
            # 현재 사용자와 해당 제품을 가진 장바구니 를 삭제합니다.
            Cart.objects.get(user=user, products=product).delete()
        # 사용자 id(pk)를 URL에 전달
        return redirect("shop:cart", user.pk)


# 로그인이 되어있지 않으면 아래 함수가 실행되지 않음
# 로그인 없이 실행하면 "accounts/login/"으로 리다이렉트 시킴
@login_required
# 카트 추가 함수
# pk => user_id
def add_to_cart(request, pk):
    # 요청 방식이 POST인지 확인
    if request.method == "POST":
        # 현재 사용자 요청 확인
        user = request.user
        # product에 데이터베이스에 저장된 Product 항목을 넣어줌
        product = Product.objects.get(pk=pk)
        # quantity에 POST 요청에서 "quantity"라고 전달된 것을 가져와 정수로 변환하여 넣어줌
        quantity = int(request.POST.get("quantity"))
        # cart_item에 현재 사용자와 해당제품을 가진 장바구니 항목을 데이터베이스에 검색하여 있다면 넣어줌
        cart_item = Cart.objects.filter(user=user, products=product).first()

        # 장바구니에 해당 제품이 있을시
        if cart_item:
            # 기존 수량에 추가 수량을 더하지만 최대 수량은 초과 하지않게함
            cart_item.quantity = min(cart_item.quantity + quantity, product.quantity)
            # 변경 수량 데이터베이스에 저장
            cart_item.save()
        # 장바구니에 해당 제품 없을시
        else:
            # 새로운 장바구니 항목을 데이터베이스에 만듦
            Cart.objects.create(user=user, products=product, quantity=quantity)

        # 사용자가 장바구니에 성공적으로 제품이 추가되었다는 메세지 설정
        messages.success(request, "Added to cart successfully.")
        return redirect("shop:cart", user.pk)


# 로그인이 되어있지 않으면 아래 함수가 실행되지 않음
# 로그인 없이 실행하면 "accounts/login/"으로 리다이렉트 시킴
@login_required
# 결제 화면으로 넘어가는 함수
# html의 구성은 "이미지|상품명|수량|가격"으로 되어있고 pg결제창이 바로 뜸
# pk => product_id
def pay(request, pk):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        product = get_object_or_404(Product, pk=pk)
        user = request.user
        categories = Category.objects.all()

        initial = {"name": product.name, "amount": product.price, "quantity": quantity}

        form = OrderForm(request.POST, initial=initial)

        context = {
            "form": form,
            "quantity": quantity,
            # pg를 사용하기 위해 필요함
            "iamport_shop_id": "iamport",
            "user": user,  # 사용 안함
            "product": product,
            "categories": categories,  #  사용 안함
        }

        return render(request, "shop/order_pay.html", context)
