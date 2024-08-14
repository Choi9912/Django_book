# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm


# 회원가입 함수
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        # form이 유효한지 확인
        if form.is_valid():
            # 데이터 베이스에 유저 저장
            user = form.save()
            user.refresh_from_db()
            user.save()

            # if username and password valid, authenticate function returns User Object
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            # login and redirect to root
            login(request, user)

            return redirect("root")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})
