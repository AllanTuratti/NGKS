from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from catalogo.models import Produto
from .models import CartItem, Pedido

# Create your views here.


class CreateCartItemView( RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        produto = get_object_or_404(Produto, slug=self.kwargs['slug'])
        if self.request.session.session_key is None:
            self.request.session.save()
        cart_item, created = CartItem.objects.add_item(
            self.request.session.session_key, produto
        )
        if created:
            messages.success(self.request, 'Produto adicionado com Sucesso')
        else:
            messages.success(self.request, 'Produto atualizado com Sucesso')
        return reverse('checkout:cart_item')


class CartItemView(LoginRequiredMixin, TemplateView):

    template_name = 'carrinho.html'

    def get_formset(self, clear=False):
        CartItemFormSet = modelformset_factory(
            CartItem, fields=('quantidade',), can_delete=True, extra=0
        )
        session_key = self.request.session.session_key
        if session_key:
            if clear:
                formset = CartItemFormSet(
                    queryset=CartItem.objects.filter(cart_key=session_key)
                )
            else:
                formset = CartItemFormSet(
                    queryset=CartItem.objects.filter(cart_key=session_key),
                    data=self.request.POST or None
                )
        else:
            formset = CartItemFormSet(queryset=CartItem.objects.none())
        return formset

        
    def get_context_data(self, **kwargs):
        context = super(CartItemView, self).get_context_data(**kwargs)
        context['formset'] = self.get_formset()
        return context


    def post(self, request, *args, **kwargs):
        formset = self.get_formset()
        context = self.get_context_data(**kwargs)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Carrinho atualizado com sucesso')
            context['formset'] = self.get_formset(clear=True)
        return self.render_to_response(context)


class CheckoutView(LoginRequiredMixin, TemplateView):

    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        session_key = request.session.session_key
        if session_key and CartItem.objects.filter(cart_key=session_key).exists():
            cart_items = CartItem.objects.filter(cart_key=session_key)
            pedido = Pedido.objects.criar_pedido(
                user=request.user, cart_items=cart_items
            )
        else:
            messages.info(request, 'Não há itens no carrinho de compras')
            return redirect('checkout:cart_item')
        response = super(CheckoutView, self).get(request, *args, **kwargs)
        response.context_data['pedido'] = pedido
        return response

class ListaPedidoView(LoginRequiredMixin, ListView):

    template_name = 'lista_pedido.html'
    paginate_by = 10

    def get_queryset(self):
        return Pedido.objects.filter(user=self.request.user)

class DetalhePedidoView(LoginRequiredMixin, DetailView):
    template_name = 'detalhe_pedido.html'

    def get_queryset(self):
        return Pedido.objects.filter(user=self.request.user)

create_cartitem = CreateCartItemView.as_view()
cart_item = CartItemView.as_view()
checkout = CheckoutView.as_view()
lista_pedido = ListaPedidoView.as_view()
detalhe_pedido = DetalhePedidoView.as_view()
