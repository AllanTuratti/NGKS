from django.contrib import admin

from .models import Pedido

class Statuspagamento(admin.ModelAdmin):
    list_display = ['user', 'status', 'opcao_pagamento']

admin.site.register(Pedido, Statuspagamento)
