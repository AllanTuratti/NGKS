from django.test import TestCase
from django.urls import reverse

from model_mommy import mommy 

from catalogo.models import Categoria, Produto

class CategoriaTestCase(TestCase):

    def setUp(self):
        self.categoria = mommy.make('catalogo.Categoria')

    def test_get_absolute_url(self):
        self.assertEquals(
            self.categoria.get_absolute_url(),
            reverse('catalogo:categoria', kwargs={'slug': self.categoria.slug})
            )
    
class ProdutoTestCase(TestCase):

    def setUp(self):
        self.produto = mommy.make(Produto, slug='produto')

    def test_get_absolute_url(self):
        self.assertEquals(
            self.produto.get_absolute_url(),
            reverse('catalogo:produto', kwargs={'slug': 'produto'})
        )
