import logging

from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from course.models import Course

# 获取日志信息
from edu_api.settings import constants

log = logging.getLogger('django')


class CartViewSet(ViewSet):
    # 用户认证:登录且认证通过的才能访问
    permission_classes = [IsAuthenticated]

    # 添加购物车的相关逻辑
    def add_cart(self, request):
        # 添加用户提交的信息到购物车
        # 用户id 课程id  勾选状态 有效期
        course_id = request.data.get('course_id')
        user_id = request.user.id
        # 是否勾选
        select = True
        # 有效期
        expire = 0

        # 校验前端提交的参数
        try:
            Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'message': '参数有误,课程不存在'}, status=status.HTTP_400_BAD_REQUEST)

        # 课程存在且用户存在，保存信息
        try:
            # 获取redis连接对象
            redis_connection = get_redis_connection('cart')
            # 将数据保存到redis
            pipeline = redis_connection.pipeline()
            # 管道开启
            pipeline.multi()
            # 商品的信息以及对应的有效期 cart_1  1  0
            pipeline.hset('cart_%s' % user_id, course_id, expire)
            # 被勾选的商品
            pipeline.sadd('select_%s' % user_id, course_id)
            # 开始执行
            pipeline.execute()
            # 先执行后获取商品id的个数
            course_len = redis_connection.hlen('cart_%s' % user_id)  # 返回商品id的个数

        except:
            log.error('购物车数据存储失败')
            return Response({'message': '参数有误,购物车添加失败'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        print('成功')
        return Response({'message': '购物车商品添加成功', 'course_length': course_len})

    # 查询购物车信息相关逻辑
    def list_cart(self, request):
        user_id = request.user.id
        redis_connection = get_redis_connection('cart')
        cart_list = redis_connection.hgetall('cart_%s' % user_id)
        select_list = redis_connection.smembers('select_%s' % user_id)
        # print('cart_list:', cart_list)  # 二进制类型数据

        # 循环从mysql中找出商品(课程)的信息
        data = []
        # 课程id和有效期
        for course_id_b, expire_id_b in cart_list.items():
            course_id = int(course_id_b)  # 转整形
            expire_id = int(expire_id_b)
            try:
                # 获取到所有商品的课程信息
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except Course.DoesNotExist:
                continue

            # 将购物车所需要的信息返回
            data.append({
                'selected': True if course_id_b in select_list else False,
                'course_img': constants.IMAGE_SRC + course.course_img.url,
                'name': course.name,
                'id': course.id,
                'expire_id': expire_id,
                'price': course.price
            })
        return Response(data)

    # 切换购物车选中/不选中的状态
    def chang_selected(self, request):
        user_id = request.user.id
        selected = request.data.get('selected')
        course_id = request.data.get('course_id')
        print(user_id, selected, course_id)
        # 判断商品是否在购物车中
        try:
            course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({'message': '当前商品不存在'}, status=status.HTTP_400_BAD_REQUEST)

        redis_connection = get_redis_connection('cart')
        print('123')
        if selected:
            # 将商品添加到set中，代表选中
            redis_connection.sadd('select_%s' % user_id, course_id)
        else:
            redis_connection.srem('select_%s' % user_id, course_id)
        return Response({'message': '状态切换成功'}, status=status.HTTP_200_OK)
