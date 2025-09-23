from django.urls import path
from .api_views import CaptchaGenerateAPIView, CaptchaVerifyAPIView, CaptchaRefreshAPIView

app_name = 'hertz_captcha'

urlpatterns = [
    # API endpoints for documentation
    path('generate/', CaptchaGenerateAPIView.as_view(), name='api_generate'),
    path('verify/', CaptchaVerifyAPIView.as_view(), name='api_verify'),
    path('refresh/', CaptchaRefreshAPIView.as_view(), name='api_refresh'),
]