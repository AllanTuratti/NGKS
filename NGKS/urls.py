from django.contrib import admin
from django.conf.urls import url, include
from core import views
from catalogo import views as views_catalogo

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^contato/$', views.contato,name='contato'),
    url(r'^produto/$', views.produto, name='produto'),
    url(r'^produtos/', include(('catalogo.urls','catalogo'), namespace='catalogo')),
    url(r'^admin/', admin.site.urls),
    url(r'^sobrenos', views.sobrenos, name='sobrenos')
]
