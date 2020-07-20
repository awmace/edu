from rest_framework.generics import CreateAPIView
from order.models import Order
from order.serialisers import OrderModelSerilizer


class OrderAPIView(CreateAPIView):
    # 生成订单的视图
    queryset = Order.objects.filter(is_delete=False,is_show=True)
    serializer_class = OrderModelSerilizer
