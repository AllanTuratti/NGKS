from .models import Categoria

def categorias(resquest):
    return{
        'categorias': Categoria.objects.all()
    }