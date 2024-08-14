from django import forms

from .models import Product, Order


# ProductForm 클래스
class ProductForm(forms.ModelForm):
    # 메타 정보
    class Meta:
        # 사용 하는 모델 Product
        model = Product
        # 폼에서 사용할 필드 정의
        fields = ["name", "category", "image", "price", "quantity", "description"]
        # 폼필드의 HTML 표현 정의
        widgets = {
            # 텍스트 입력 위젯 부트스트랩의 CSS클래스 설정
            "name": forms.TextInput(attrs={"class": "form-control"}),
            # 드롭다운 위젯 설정
            "category": forms.Select(attrs={"class": "form-control"}),
            # 파일 업로드 위젯 설정
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            # 숫자 입력 위젯 설정
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            # 숫자 입력 위젯
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            # 다중행 텍스트 영역 위젯
            "description": forms.Textarea(attrs={"class": "form-control"}),
        }


# 주문할 때 필요한 폼을 제작
class OrderForm(forms.ModelForm):
    # 메타 정보 수정
    class Meta:
        # 사용하는 모델은 Order
        model = Order
        # Order 모델 중 사용하는 필드
        fields = ["name", "amount", "quantity"]
        widgets = {
            # 필드에 있는 값을 모두 읽을 수만 있도록 위젯을 설정
            "name": forms.TextInput(attrs={"readonly": "readonly"}),
            "amount": forms.TextInput(attrs={"readonly": "readonly"}),
            "quantity": forms.TextInput(attrs={"readonly": "readonly"}),
        }
