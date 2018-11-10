from core import views
from django.contrib import admin
from django.conf.urls import url, include
from catalogo import views as views_catalogo
from checkout import views as views_checkout
from django.contrib.auth.views import login, logout

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^contato/$', views.contato,name='contato'),
    url(r'^login/$', login,{'template_name':'login.html'},name='login'),
    url(r'^logout/$', logout,{'next_page':'index'},name='logout'),
    url(r'^loja/', include(('catalogo.urls','lista_produto'), namespace='catalogo')),
    url(r'^compras/', include(('checkout.urls', 'checkout'), namespace='checkout')),
    url(r'^admin/', admin.site.urls),
    url(r'^paypal/', include(('paypal.standard.ipn.urls', 'paypal'), namespace='paypal')),
]
