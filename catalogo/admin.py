from django.contrib import admin

from .models import Produto, Categoria

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'criado', 'modificado']
    search_fields = ['nome','slug']
    list_filter = ['criado', 'modificado']

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'categoria', 'criado', 'modificado']
    search_fields = ['nome','slug', 'categoria__nome']
    list_filter = ['criado', 'modificado']


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Produto, ProdutoAdmin)