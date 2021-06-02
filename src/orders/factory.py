from app.test.factory import register


@register
def order(self, is_paid: bool = False, item=None, **kwargs):
    order = self.mixer.blend('orders.Order', **kwargs)
    if is_paid:
        order.set_paid()

    if item is not None:
        order.set_item(item)
        order.save()

    return order
