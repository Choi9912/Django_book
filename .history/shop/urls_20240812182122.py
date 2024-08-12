from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:category_id>/', views.show_category, name='show_category'),
    path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/<int:pk>/', views.cart, name='cart'),
    path('cart/delete/<int:pk>/', views.delete_cart, name='delete_cart'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('pay/<int:pk>/', views.pay, name='pay'),
]