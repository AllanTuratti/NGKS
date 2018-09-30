from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Produto, Categoria

class ProdutosListView(generic.ListView):
    model = Produto
    template_name = 'lista_produto.html'
    context_object_name = 'lista_produto'
    paginate_by = 3

lista_produto = ProdutosListView.as_view()

class CategoriaListView(generic.ListView):
    template_name = 'categoria.html'
    context_object_name = 'lista_produto'
    paginate_by = 3

    def get_queryset(self):
        return Produto.objects.filter(categoria__slug=self.kwargs['slug'])

    def get_context_data(self,**kwargs):
        context = super(CategoriaListView, self).get_context_data(**kwargs)
        context['categoria_atual'] = get_object_or_404(Categoria, slug=self.kwargs['slug'])
        return context

categoria = CategoriaListView.as_view()

def produto(request, slug):
    produto = Produto.objects.get(slug=slug) 
    context = {
        'produto': produto,
    }
    return render(request, 'produto.html', context)