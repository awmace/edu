from django.urls import path

from cart import views

urlpatterns = [
    path('option/', views.CartViewSet.as_view(
        {'post': 'add_cart',
         'get': 'list_cart',
         'patch': 'chang_selected',
         "put": "change_expire",
         "delete": "delete_course",
         })),
    path('order/', views.CartViewSet.as_view(
        {
            'get': 'get_select_course',
        })),
    path('rmcart/<str:id>/', views.DeleteCartAPIView.as_view()),
]
