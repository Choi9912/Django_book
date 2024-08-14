from django.conf import settings
from django.db import models
from sorl.thumbnail import ImageField


# section 3 상품목록에 상품 카테고리의 클래스 정의
# index, show_category, product_detail, view_cart, pay 함수에서 사용됨
class Category(models.Model):
    # 카테고리 이름
    name = models.CharField(max_length=255)

    # 쿼리를 불러올 때, 이름을 지정
    def __str__(self):
        return "{}".format(self.name)


# Section 3 상품의 모델 작성
class Product(models.Model):
    name = models.CharField(max_length=255)
    # 상품의 카테고리 # 해당하는 Category 삭제시 해당하는 모델들 전부 삭제
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # media/photos/에 저장 # blank =해당 필드를 비워두어도 유효성 검사 통과 # null=database에 빈 값으로 저장 가능
    image = ImageField(upload_to="photos/", blank=True, null=True)
    price = models.IntegerField()
    # 남아있는 재고 수량
    quantity = models.IntegerField(default=0)
    description = models.TextField()
    # 출시한 날짜(상품 등록 날짜) # 자동으로 추가 됨
    pub_date = models.DateTimeField(auto_now_add=True)
    hit = models.IntegerField(default=0)  # 조회수

    def __str__(self):  # 쿼리를 불러올 때, 이름을 지정
        return "{} {}".format(self.name, self.pub_date)


# Section 4 장바구니의 클래스 정의
# 장바구니 (Cart) 클래스 정의
class Cart(models.Model):
    # user 인스턴스 필드선언 ForeignKey는 class Category
    user = models.ForeignKey(
        # 사용자 정의 모델
        settings.AUTH_USER_MODEL,
        # 해당하는 Category 삭제시  이 Cart 인스턴스 모델들 전부삭제
        on_delete=models.CASCADE,
    )
    # Product 모델과 연결, 해당상품삭제시 Cart 인스턴스도 함께 삭제/ related_name="wish_product" 은 Product 모델에서 Cart 모델을 참조할 때 사용할 이름을 정의
    products = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wish_product", blank=True
    )
    # quantity 인스턴스 필드 정의 , 장바구니에 해당 상품의 수량을 저장
    quantity = models.IntegerField(default=1)

    # 문자열로 표현될떄 정의
    # 사용자 이름과 상품의 이름 표시
    def __str__(self):
        return "{} // {}".format(self.user, self.products.name)


# Section 5 주문하기, forms.py에서'class OrderForm'에서 사용됨
class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100, verbose_name="상품명")
    amount = models.PositiveIntegerField(verbose_name="결제금액")
    # 선택한 수량 / 따로 작성한 값이 없다면 1로 고정
    quantity = models.IntegerField(default=1)
    products = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_product"
    )
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # id를 내림차순으로 정렬
        ordering = ("-id",)

    def __str__(self):
        return "{} by {}".format(self.products.name, self.user)
