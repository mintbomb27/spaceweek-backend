from django import views
from django.urls import include, path
from .entrycheck import *
from .views import *

urlpatterns = [
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('forgot-password/', ForgotPasswordRequest.as_view()),
    path('verify-forgot-password-otp/', VerifyForgotPasswordOTP.as_view()),
    path('update-password/', ForgotPasswordView.as_view()),
    path('entry/',EntryCheckView.as_view()),
    path('sadhya/',HadFood.as_view()),
    path('vtop-regns/', UploadRegistrations.as_view())
]