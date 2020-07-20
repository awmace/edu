from datetime import datetime

from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers

from course.models import Course, CourseExpire
from order.models import Order, OrderDetail


class OrderModelSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'pay_type')

        extra_kwargs = {
            'id': {'read_only': True},
            'order_number': {'read_only': True},
            'pay_type': {'write_only': True}
        }

    def validate(self, attrs):
        # 对数据进行验证
        pay_type = attrs.get('pay_type')
        try:
            Order.pay_choices[pay_type]
        except Order.DoesNotExist:
            raise serializers.ValidationError('您当前选择的支付方式不正确')
        return attrs

    def create(self, validated_data):
        # 生成订单与订单详情
        # 通过context获取到request对象然后获取user.id
        user_id = self.context['request'].user.id

        redis_connection = get_redis_connection('cart')
        incr = redis_connection.incr('order')

        # 生成唯一的订单号   时间戳 用户id 随机字符串等
        order_number = datetime.now().strftime('%Y%m%d%H%M%S') + '%06d' % user_id + '%06d' % incr

        # 开启事物
        with transaction.atomic():

            # 记录下事务回滚的点
            rollback_id = transaction.savepoint()

            # 生成订单
            try:
                order = Order.objects.create(
                    order_title='百知教育在线课程订单',
                    total_price=0,
                    real_price=0,
                    order_number=order_number,
                    order_status=0,
                    pay_type=validated_data.get('pay_type'),
                    credit=0,
                    coupon=0,
                    order_desc='机会不容错过',
                    user_id=user_id,
                )
            except:
                transaction.savepoint_rollback(rollback_id)
                raise serializers.ValidationError('订单生成失败')
            # 生成订单详情
            # 从购物车获取订单详情
            cart_list = redis_connection.hgetall("cart_%s" % user_id)
            select_list = redis_connection.smembers("select_%s" % user_id)

            total_price = 0  # 商品总价
            data = []

            for course_id_byte, expire_id_byte in cart_list.items():
                course_id = int(course_id_byte)
                expire_id = int(expire_id_byte)

                # 判断商品id是否在已勾选的的列表中
                if course_id_byte in select_list:
                    try:
                        # 获取到的所有的课程信息
                        course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                    except Course.DoesNotExist:
                        # 课程不存在不再进行订单的生成，已生成好的订单也不再保存
                        transaction.savepoint_rollback(rollback_id)
                        return serializers.ValidationError('对不起，当前商品不存在')

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

                    try:
                        # 生成订单详情
                        OrderDetail.objects.create(
                            order=order,
                            course=course,
                            expire=expire_id,
                            price=original_price,
                            real_price=real_expire_price,
                            discount_name=course.discount_name
                        )
                        redis_connection.hdel("cart_%s" % user_id, course_id)
                    except:
                        # 回滚事物
                        transaction.savepoint_rollback(rollback_id)
                        raise serializers.ValidationError('订单详情生成失败')

                    # 成功则计算订单的总价
                    order.total_price += float(original_price)
                    order.real_price += float(real_expire_price)
                order.save()
            return order
