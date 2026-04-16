"""
示例电商模块 - 用于演示 AI 测试平台功能
"""


class ShoppingCart:
    """购物车类"""

    def __init__(self):
        self.items = []
        self.max_quantity = 99

    def add_item(self, product_id, name, price, quantity=1):
        """
        添加商品到购物车

        Args:
            product_id: 商品 ID
            name: 商品名称
            price: 单价
            quantity: 数量

        Returns:
            dict: 操作结果
        """
        if quantity <= 0:
            return {'success': False, 'message': '数量必须大于 0'}

        if quantity > self.max_quantity:
            return {'success': False, 'message': f'单次购买数量不能超过 {self.max_quantity}'}

        if price < 0:
            return {'success': False, 'message': '价格不能为负数'}

        # 检查商品是否已在购物车中
        for item in self.items:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                return {'success': True, 'message': '商品数量已更新', 'item': item}

        # 添加新商品
        new_item = {
            'product_id': product_id,
            'name': name,
            'price': price,
            'quantity': quantity
        }
        self.items.append(new_item)
        return {'success': True, 'message': '商品已添加到购物车', 'item': new_item}

    def remove_item(self, product_id):
        """移除商品"""
        for i, item in enumerate(self.items):
            if item['product_id'] == product_id:
                removed_item = self.items.pop(i)
                return {'success': True, 'message': '商品已移除', 'item': removed_item}
        return {'success': False, 'message': '商品不存在'}

    def update_quantity(self, product_id, quantity):
        """更新商品数量"""
        if quantity <= 0:
            return self.remove_item(product_id)

        if quantity > self.max_quantity:
            return {'success': False, 'message': f'数量不能超过 {self.max_quantity}'}

        for item in self.items:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                return {'success': True, 'message': '数量已更新', 'item': item}
        return {'success': False, 'message': '商品不存在'}

    def get_total(self):
        """计算总价"""
        return sum(item['price'] * item['quantity'] for item in self.items)

    def clear(self):
        """清空购物车"""
        self.items = []
        return {'success': True, 'message': '购物车已清空'}

    def get_item_count(self):
        """获取商品总数"""
        return sum(item['quantity'] for item in self.items)


class OrderProcessor:
    """订单处理器"""

    def __init__(self):
        self.orders = []
        self.order_counter = 1000

    def create_order(self, cart, user_id, shipping_address):
        """
        创建订单

        Args:
            cart: 购物车对象
            user_id: 用户 ID
            shipping_address: 收货地址

        Returns:
            dict: 订单结果
        """
        if not cart.items:
            return {'success': False, 'message': '购物车为空'}

        if not user_id:
            return {'success': False, 'message': '用户未登录'}

        if not shipping_address or len(shipping_address) < 10:
            return {'success': False, 'message': '请输入完整的收货地址'}

        # 创建订单
        self.order_counter += 1
        order = {
            'order_id': f'ORD{self.order_counter}',
            'user_id': user_id,
            'items': cart.items.copy(),
            'total': cart.get_total(),
            'shipping_address': shipping_address,
            'status': 'pending'
        }
        self.orders.append(order)

        # 清空购物车
        cart.clear()

        return {'success': True, 'message': '订单创建成功', 'order': order}

    def cancel_order(self, order_id):
        """取消订单"""
        for order in self.orders:
            if order['order_id'] == order_id:
                if order['status'] == 'pending':
                    order['status'] = 'cancelled'
                    return {'success': True, 'message': '订单已取消'}
                return {'success': False, 'message': '该订单无法取消'}
        return {'success': False, 'message': '订单不存在'}

    def get_order_status(self, order_id):
        """查询订单状态"""
        for order in self.orders:
            if order['order_id'] == order_id:
                return {'success': True, 'order': order}
        return {'success': False, 'message': '订单不存在'}
