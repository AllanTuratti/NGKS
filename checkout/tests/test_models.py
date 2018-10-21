from django.test import TestCase
from django.conf import settings
from model_mommy import mommy

from checkout.models import CartItem


class CartItemTestCase(TestCase):

    def setUp(self):
        mommy.make(CartItem)

    def test_post_save_cart_item(self):
        cart_item = CartItem.objects.all()[0]
        cart_item.quantidade = 0
        cart_item.save()

class OrderTestCase(TestCase):

    def setUp(self):
        self.cart_item = mommy.make(CartItem)
        self.user = mommy.make(settings.AUTH_USER_MODEL)

  
