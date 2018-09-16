from django.shortcuts import render

from .models import Produto, Categoria

def lista_produto(request):
    context = {
        'lista_produto': Produto.objects.all()
    }
    return render(request, 'lista_produto.html', context)

def categoria(request, slug):
    categoria = Categoria.objects.get(slug=slug)
    context = {
        'categoria_atual': categoria,
        'lista_produto': Produto.objects.filter(categoria=categoria)
    }
    return render(request, 'categoria.html', context)