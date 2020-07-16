import re

from django.contrib.auth.hashers import make_password
# from django_redis import get_redis_connection
from django_redis import get_redis_connection
from rest_framework import serializers

from user.models import UserInfo
from user.utils import get_user_by_account


class UserModelSerializer(serializers.ModelSerializer):
    # 自定义token字段
    token = serializers.CharField(max_length=1024, read_only=True, help_text="用户token")
    # 自定义验证码字段
    sms_code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text="短信验证码")

    class Meta:
        model = UserInfo
        fields = ("id", "username", "password", "phone", "token", "sms_code")

        extra_kwargs = {
            "id": {
                'read_only': True,
            },
            "username": {
                "read_only": True,
            },
            "password": {
                "write_only": True,
            },
            "phone": {
                "write_only": True
            }
        }

    def validate(self, attrs):
        # 读取前端发送的手机号等信息
        phone = attrs.get("phone")
        sms_code = attrs.get("sms_code")  # 用户提交的验证码

        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            raise serializers.ValidationError("手机号格式错误")

        # 验证手机号是否被注册
        try:
            user = get_user_by_account(phone)
        except:
            user = None
        if user:
            raise serializers.ValidationError("当前手机号已经被注册")

        # 验证手机号短信验证码是否正确
        redis_connection = get_redis_connection("npf")
        phone_code = redis_connection.get("mobile_%s" % phone)

        # 输出前端发送过来的验证码和短信验证码
        print(phone_code.decode(), sms_code)

        # redis取出的是二进制字符串，维持编码一致性需要解码
        if phone_code.decode() != sms_code:
            # 为了防止暴力破解 可以再次设置一个手机号只能验证10次
            redis_connection.setnx("%s" % phone, '1')
            num = int(redis_connection.get("%s" % phone).decode())
            print(num)  # 输出验证错误次数
            if num < 11:
                redis_connection.incr("%s" % phone)
            else:
                # 伪删除验证码
                redis_connection.append("mobile_%s" % phone, 'knms')
                raise serializers.ValidationError("超出验证次数,验证码失效")

            raise serializers.ValidationError("验证码不一致")
        # 成功后需要将验证码删除：这里是伪删除，追加了一个字符串
        redis_connection.append("mobile_%s" % phone, 'knms')

        return attrs

    def create(self, validated_data):
        # 采集用户信息
        # 获取密码  进行加密
        pwd = validated_data.get("password")
        hash_password = make_password(pwd)

        # 处理用户名  设置为手机号
        username = validated_data.get("phone")

        # 添加数据
        user = UserInfo.objects.create(
            phone=username,
            username=username,
            password=hash_password,
        )

        # 为注册成功的用户生成token
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)

        return user
