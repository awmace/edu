from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from course.models import CourseCategory, Course, CourseChapter

# 课程分类信息查询
from course.pagination import CoursePageNumber
from course.serializer import CourseCategorySerializer, CourseModelSerializer, CourseDetailModerSerializer, \
    CourseChapterModelSerializer


class CourseCategoryListAPIView(ListAPIView):
    # 查询所有课程分类信息
    queryset = CourseCategory.objects.filter(is_show=True, is_delete=False).order_by('orders')
    # 指定序列化器
    serializer_class = CourseCategorySerializer


class CourseListAPIView(ListAPIView):
    # 课程列表查询
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseModelSerializer


class CourseFilterListAPIView(ListAPIView):
    """根据条件查询课程"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseModelSerializer

    # 根据不同的分类id查询不同的课程
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ("course_category",)
    # 排序
    ordering_fields = ("id", "students", "price")
    # 分页   只能有一个
    pagination_class = CoursePageNumber


# 继承RetrieveAPIView
class CourseDetailView(RetrieveAPIView):
    # 查询单个课程的信息
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseDetailModerSerializer


class CourseLessonListAPIView(ListAPIView):
    # 章节以及对应课时信息
    queryset = CourseChapter.objects.filter(is_show=True, is_delete=False).order_by('orders')
    serializer_class = CourseChapterModelSerializer
    # 根据课程id过滤章节信息
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['course']
