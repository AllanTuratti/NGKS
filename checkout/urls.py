from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^carrinho/adicionar/(?P<slug>[\w_-]+)/$', views.create_cartitem,
        name='create_cartitem'
    ),
    url(r'^carrinho/$', views.cart_item, name='cart_item'),
    url(r'^finalizando/$', views.checkout, name='checkout'),
    url(r'^meus-pedidos/$', views.lista_pedido, name='lista_pedido'),
    url(r'^meus-pedidos/(?P<pk>\d+)/$', views.detalhe_pedido, name='detalhe_pedido')
]
