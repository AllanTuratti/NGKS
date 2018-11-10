from django.db import models
from django.conf import settings
from catalogo.models import Produto
from pagseguro import PagSeguro

# Create your models here.

class CartItemManager(models.Manager):

    def add_item(self, cart_key, produto):
        if self.filter(cart_key=cart_key, produto=produto).exists():
            created = False
            cart_item = self.get(cart_key=cart_key, produto=produto)
            cart_item.quantidade = cart_item.quantidade + 1
            cart_item.save()
        else:
            created = True
            cart_item = CartItem.objects.create(cart_key=cart_key, produto=produto, preco=produto.preco)
                  
        return cart_item, created

class CartItem(models.Model):

    cart_key = models.CharField('Chave do Carrinho', max_length=40, db_index=True)
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    preco = models.DecimalField('Preço', decimal_places=2, max_digits=8)
    produto = models.ForeignKey(
        'catalogo.produto',
        on_delete=models.DO_NOTHING,
        verbose_name='catalogo.produto'
    )

    objects = CartItemManager()

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens dos Carrinhos'
        unique_together = (('cart_key', 'produto'),)


    def __str__(self):
        return '{} [{}]'.format(self.produto, self.quantidade)

    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens dos pedidos'

    def __str__(self):
        return '[{}] {}'.format(self.order, self.produto)

class PedidoManager(models.Manager):
    def criar_pedido(self, user, cart_items):
        pedido = self.create(user=user)
        for cart_item in cart_items:
            pedido_item = PedidoItem.objects.create(
                pedido = pedido, quantidade=cart_item.quantidade, produto= cart_item.produto,
                preco = cart_item.preco
            )
        return pedido

class Pedido(models.Model):
    
    STATUS_CHOICES = (  
        (0, 'Aguardando Pagamento'),
        (1, 'Concluida'),
        (2,'Cancelada'),
    )

    PAYMENT_OPTION_CHOICES = (  
        ('pagseguro', 'Pagseguro'),
        ('paypal', 'Paypal'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Usuário', on_delete=models.DO_NOTHING
    )
    status = models.IntegerField(
        'Situação', choices=STATUS_CHOICES, default=0, blank=True
    )
    opcao_pagamento = models.CharField(
        'Opação de Pagamento', choices= PAYMENT_OPTION_CHOICES, max_length=20,
    )

    criado = models.DateTimeField('Criado em', auto_now_add=True)
    modificado = models.DateTimeField('Modificado em', auto_now=True)

    objects = PedidoManager()

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return 'Pedido #{}'.format(self.pk)
    
    def produtos(self):
        produtos_ids = self.items.values_list('produto')
        return Produto.objects.filter(pk__in=produtos_ids)

    def total(self):
        aggregate_queryset = self.items.aggregate(
            total=models.Sum(
                models.F('preco') * models.F('quantidade'),
                output_field=models.DecimalField()
            )
        )
        return aggregate_queryset['total']
        
    def pagseguro_update_status(self, status):
        if status == '3':
            self.status = 1
        elif status == '7':
            self.status = 2
        self.save()
    
    def complete(self):
        self.status = 1
        self.save()

    def pagseguro(self):
        self.opcao_pagamento = 'pagseguro'
        self.save()
        pg = PagSeguro(
            email=settings.PAGSEGURO_EMAIL, token=settings.PAGSEGURO_TOKEN, 
            config={'sandbox': settings.PAGSEGURO_SANDBOX}
        )
        pg.sender= {
            'email':self.user.email
        }
        pg.reference_prefix = None
        pg.shipping = None
        pg.reference = self.pk
        for item in self.items.all():
            pg.items.append(
                {
                    'id': item.produto.pk,
                    'description': item.produto.nome,
                    'Quantity': item.quantidade,
                    'amount': '%.2f' % item.preco,
                }
            )
        return pg

    def paypal(self):
        self.opcao_pagamento = 'paypal'
        self.save()
        paypal_dict = {
            'upload': '1',
            'business': settings.PAYPAL_EMAIL,
            'invoice': self.pk,
            'cmd': '_cart',
            'currency_code': 'BRL',
            'charset': 'utf-8',
        }
        index = 1
        for item in self.items.all():
            paypal_dict['amount_{}'.format(index)] = '%.2f' % item.preco
            paypal_dict['item_name_{}'.format(index)] = item.produto.nome
            paypal_dict['quantity_{}'.format(index)] = item.quantidade
            index = index + 1
        return paypal_dict

class PedidoItem(models.Model):

    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    preco = models.DecimalField('Preço', decimal_places=2, max_digits=8)
    produto = models.ForeignKey(
        'catalogo.produto', on_delete=models.DO_NOTHING, verbose_name='catalogo.produto'
    )
    pedido = models.ForeignKey(
        Pedido, verbose_name='Pedido', related_name='items', on_delete=models.DO_NOTHING
    )

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens dos Pedidos'

    def __str__(self):
        return '[{}] {}'.format(self.order, self.produto)


def post_save_cart_item(instance, **kwargs):
    if instance.quantidade < 1:
        instance.delete()

models.signals.post_save.connect(
    post_save_cart_item, sender=CartItem, dispatch_uid='post_save_cart_item')
