import logging

from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from course.models import Course, CourseExpire

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
                # 'price': course.real_price(),
                # 获取课程的有效期
                "expire_list": course.expire_list,
                # 获取真实价格
                "real_price": course.real_expire_price(expire_id),
            })
        return Response(data)

    # 切换购物车选中/不选中的状态
    def chang_selected(self, request):
        user_id = request.user.id
        selected = request.data.get('selected')
        course_id = request.data.get('course_id')
        # 判断商品是否在购物车中
        try:
            course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({'message': '当前商品不存在'}, status=status.HTTP_400_BAD_REQUEST)

        redis_connection = get_redis_connection('cart')
        if selected:
            # 将商品添加到set中，代表选中
            redis_connection.sadd('select_%s' % user_id, course_id)
        else:
            redis_connection.srem('select_%s' % user_id, course_id)
        return Response({'message': '状态切换成功'}, status=status.HTTP_200_OK)

    def change_expire(self, request):
        """改变redis中课程的有效期"""
        user_id = request.user.id
        expire_id = request.data.get("expire_id")
        course_id = request.data.get("course_id")

        try:
            course = Course.objects.get(is_show=True, is_delete=False, id=course_id)
            # 如果前端传递来的有效期选项  如果不是0  则修改课程对应的有效期
            if expire_id > 0:
                expire_iem = CourseExpire.objects.filter(is_show=True, is_delete=False, id=expire_id)
                if not expire_iem:
                    raise Course.DoesNotExist()
        except Course.DoesNotExist:
            return Response({"message": "课程信息不存在"}, status=status.HTTP_400_BAD_REQUEST)

        connection = get_redis_connection("cart")
        connection.hset("cart_%s" % user_id, course_id, expire_id)

        # 重新计算切换有效期后的价钱
        real_price = course.real_expire_price(expire_id)

        return Response({"message": "切换有效期成功", "real_price": real_price})

    def get_select_course(self, request):
        # 获取购物车已选中的商品 返回前端所需要的数据

        user_id = request.user.id
        redis_connection = get_redis_connection("cart")

        # 获取当前登录用户的购车中所有的商品
        cart_list = redis_connection.hgetall("cart_%s" % user_id)
        select_list = redis_connection.smembers("select_%s" % user_id)

        total_price = 0  # 商品总价
        data = []

        for course_id_byte, expire_id_byte in cart_list.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)
            print(course_id, expire_id)

            # 判断商品id是否在已勾选的的列表中
            if course_id_byte in select_list:
                try:
                    # 获取到的所有的课程信息
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    continue
                # 如果有效期的id大于0  则需要计算商品的价格  id不大于0则代表永久有效 需要默认值
                original_price = course.price
                expire_text = "永久有效"

                try:
                    if expire_id > 0:
                        course_expire = CourseExpire.objects.get(id=expire_id)
                        # 对应有效期的价格
                        original_price = course_expire.price
                        expire_text = course_expire.expire_text
                except CourseExpire.DoesNotExist:
                    pass

                # 根据已勾选的商品的对应有效期的价格去计算勾选商品的最终价格
                real_expire_price = course.real_expire_price(expire_id)

                # 将购物车所需的信息返回
                data.append({
                    "course_img": constants.IMAGE_SRC + course.course_img.url,
                    "name": course.name,
                    "id": course.id,
                    "expire_text": expire_text,
                    # 活动、有效期计算完成后的  真实价格
                    "real_price": "%.2f" % float(real_expire_price),
                    # 原价
                    "price": original_price,
                    "discount_name": course.discount_name,
                })

                # 商品叠加后的总价
                total_price += float(real_expire_price)

        return Response({"course_list": data,
                         "total_price": total_price,
                         "message": '获取成功',
                         'user_id': user_id, })

    # 删除购物车的课程
    def delete_course(self, request, *args, **kwargs):

        user_id = request.user.id
        course_id = request.data.get('course_id')
        # course_id = kwargs.get('id')
        print(kwargs, args)

        try:
            course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({'message': '当前商品不存在,删除失败'}, status=status.HTTP_400_BAD_REQUEST)

        redis_connection = get_redis_connection('cart')
        redis_connection.srem("cart_%s" % user_id, course_id)
        return Response({'message': '商品删除成功'}, status=status.HTTP_200_OK)


class DeleteCartAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        course_id = kwargs.get("id")
        print(course_id)
        try:
            course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({"message": "当前商品不存在，删除失败！"}, status=status.HTTP_400_BAD_REQUEST)
        redis_connection = get_redis_connection("cart")
        if course:
            redis_connection.hdel("cart_%s" % user_id, course_id)
        else:
            return Response({"message": "当前商品不存在"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "删除成功！"})
