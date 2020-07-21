from django.urls import path
from payments import views

urlpatterns = [
    path('ali_pay/', views.AliPayAPIView.as_view()),
    path('results/', views.AliPayResultAPIView.as_view()),
]
