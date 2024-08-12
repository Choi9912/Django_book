from django.conf import settings
from django.db import models
from sorl.thumbnail import ImageField

class Category(models.Model):
    menu = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.menu)
    

class Product(models.Model):
    menu = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = ImageField(upload_to='photos/',blank=True, null=True)
    price = models.IntegerField()
    stock = models.IntegerField(default=0)
    detail = models.TextField()
    pub_date = models.DateTimeField(auto_now_add = True)
    hit = models.IntegerField(default=0)

    def __str__(self):
        return '{} {}'.format(self.menu, self.pub_date)
    

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, )
    products = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wish_product', blank=True)
    stock = models.IntegerField(default=1)

    def __str__(self):
        return '{} // {}'.format(self.user, self.products.name)


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, )
    name = models.CharField(max_length=100, verbose_name='상품명')
    amount = models.PositiveIntegerField(verbose_name='결제금액')
    stock = models.IntegerField(default=1)
    products = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_product')
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return '{} by {}'.format(self.products.menu, self.user)