from pagseguro import PagSeguro

from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.models import  ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

from django.views.generic import RedirectView, TemplateView, ListView, DetailView
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.contrib import messages
from django.urls import reverse, reverse_lazy
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
            cart_items.delete()
        else:
            messages.info(request, 'Não há itens no carrinho de compras')
            return redirect('checkout:cart_item')
        response = super(CheckoutView, self).get(request, *args, **kwargs)
        response.context_data['pedido'] = pedido
        return response

class ListaPedidoView(LoginRequiredMixin, ListView):

    template_name = 'lista_pedido.html'
    paginate_by = 5

    def get_queryset(self):
        return Pedido.objects.filter(user=self.request.user)

class DetalhePedidoView(LoginRequiredMixin, DetailView):
    template_name = 'detalhe_pedido.html'

    def get_queryset(self):
        return Pedido.objects.filter(user=self.request.user)

class PagSeguroView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        pedido_pk = self.kwargs.get('pk')
        pedido = get_object_or_404(
            Pedido.objects.filter(user=self.request.user), pk=pedido_pk
        )
        pg = pedido.pagseguro()
        pg.redirect_url = self.request.build_absolute_uri(
            reverse('checkout:detalhe_pedido', args=[pedido.pk])
        )
        pg.notification_url = self.request.build_absolute_uri(
            reverse('checkout:pagseguro_notification')
        )
        response = pg.checkout()
        return response.payment_url        

class PaypalView(LoginRequiredMixin, TemplateView):

    template_name = 'paypal.html'

    def get_context_data(self, **kwargs):
        context = super(PaypalView, self).get_context_data(**kwargs)
        pedido_pk = self.kwargs.get('pk')
        pedido = get_object_or_404(
            Pedido.objects.filter(user=self.request.user), pk=pedido_pk
        )
        paypal_dict = pedido.paypal()
        paypal_dict['return_url'] = self.request.build_absolute_uri(
            reverse('checkout:lista_pedido')
        )
        paypal_dict['cancel_return'] = self.request.build_absolute_uri(
            reverse('checkout:lista_pedido')
        )
        paypal_dict['notify_url'] = self.request.build_absolute_uri(
            reverse('paypal:paypal-ipn')
        )
        context['form'] = PayPalPaymentsForm(initial=paypal_dict)
        return context


@csrf_exempt
def pagseguro_notification(request):
    notification_code = request.POST.get('notificationCode', None)
    if notification_code:
        pg = PagSeguro(
            email=settings.PAGSEGURO_EMAIL, token=settings.PAGSEGURO_TOKEN,
            config={'sandbox': settings.PAGSEGURO_SANDBOX}
        )
        notification_data = pg.check_notification(notification_code)
        status = notification_data.status
        reference = notification_data.reference
        try:
            pedido = Pedido.objects.get(pk=reference)
        except Pedido.DoesNotExist:
            pass
        else:
            pedido.pagseguro_update_status(status)
    return HttpResponse('OK')




def paypal_notification(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED and \
        ipn_obj.receiver_email == settings.PAYPAL_EMAIL:
        try:
            pedido = Pedido.objects.get(pk=ipn_obj.invoice)
            pedido.complete()
        except Pedido.DoesNotExist:
            pass


valid_ipn_received.connect(paypal_notification)

pagseguro_view = PagSeguroView.as_view()
paypal_view = PaypalView.as_view()
create_cartitem = CreateCartItemView.as_view()
cart_item = CartItemView.as_view()
checkout = CheckoutView.as_view()
lista_pedido = ListaPedidoView.as_view()
detalhe_pedido = DetalhePedidoView.as_view()









