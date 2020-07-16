from django.urls import path

from course import views

urlpatterns = [
    path('category/', views.CourseCategoryListAPIView.as_view()),
    path("list/", views.CourseListAPIView.as_view()),
    path("list_filter/", views.CourseFilterListAPIView.as_view()),
    path('detail/<str:pk>/', views.CourseDetailView.as_view()),
    path('chapter/', views.CourseLessonListAPIView.as_view()),
]
