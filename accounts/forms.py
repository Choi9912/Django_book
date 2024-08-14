# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# django에 내장되어 있는 회원가입 class를 상속받음
# 상속받은 class에 email만 추가한 class
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Required. Enter a valid email address.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
