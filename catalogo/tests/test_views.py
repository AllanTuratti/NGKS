from django.test import TestCase, Client
from django.urls import reverse

from model_mommy import mommy

from catalogo.models import Produto, Categoria

class ProdutosListTestCase(TestCase):

    def setUp(self):
        self.url = reverse('catalogo:lista_produto')
        self.client = Client()
        self.Produto = mommy.make('catalogo.Produto')

    def tearDown(self):
        Produto.objects.all().delete()

    def test_view_ok(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo_produto.html')

    def test_context(self):
        response = self.client.get(self.url)
        self.assertTrue('lista_produto' in response.context)
        lista_produto = response.context['lista_produto']
        paginator = response.context['paginator']

    def test_page_not_found(self):
        response = self.client.get('{}?page=5'.format(self.url))
        self.assertEquals(response.status_code, 404)

       


