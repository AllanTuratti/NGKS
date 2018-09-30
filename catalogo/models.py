from django.db import models
from django.urls import reverse

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField('Identificador', max_length=100 )

    criado = models.DateTimeField('Criado em', auto_now_add=True)
    modificado = models.DateTimeField('modificado em', auto_now=True)

    class Meta():
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('catalogo:categoria', kwargs={'slug':self.slug})

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField('Identificador', max_length=100 )
    descricao = models.TextField('Descrição', blank=True)
    preco = models.DecimalField('Preço', decimal_places=2, max_digits=8)
    criado = models.DateTimeField('Criado em', auto_now_add=True)
    modificado = models.DateTimeField('modificado em', auto_now=True)
    categoria = models.ForeignKey(
        'Categoria',
        on_delete=models.DO_NOTHING,
        verbose_name='Categoria'
    )

    class Meta():
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def get_absolute_url(self):
        return reverse('catalogo:produto', kwargs={'slug':self.slug})
