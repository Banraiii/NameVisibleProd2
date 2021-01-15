from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Item, OrderItem, Order, BillingAddress, News, Payment
from .forms import CheckoutForm
import stripe



class Newspage(ListView):
    """Вывелдет последние 5 товаров одежды."""
    model = News
    template_name = "news_list.html"


class NewsDetailView(DetailView):
    """Полное описание новости"""
    slug_field = "url"
    model = News
    template_name = "news_detail.html"


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # same_shipping_address = form.cleaned_data.get(
                #    'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'S':
                    return redirect("core:payment", payment_option="stripe")
                elif payment_option == "P":
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, 'Выбрана не верная оплата')
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "У тебя нет активных заказов")
            return redirect("core: order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order':order
        }
        return render(self.request, "payment.html")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.uesr, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cent
                currency='usd',
                source=token,
                descriptions='Charge for som@som.com'
            )

            # create the payments
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            #  assign the payment to the order

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Ваш заказ удалён!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Ограничение скорости ошибка")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Недопустимый параметр")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Не авторизирован!")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Проблемы с сетью")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Что-то пошло не так. Вам не предъявили обвинения. Пожалуйста, попробуйте еще раз.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "Произошла серьезная ошибка. Нас уведомили об этом.")
            return redirect("/")






class HomeView(ListView):
    model = Item
    paginate_by = 5
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "У тебя нет активных заказов")
            return redirect("/")


class ItemDetaleView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Проверь если приказ продукта есть в приказе в карте
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Количество обьектов в вашей корзине обновленно!")
            return redirect('core:order-summary')
        else:
            messages.info(request, "Товар добавлен в корзину!")
            order.items.add(order_item)
            return redirect('core:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Этот обьект добавлен к корзине!")
    return redirect('core:order-summary')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # Проверь если приказ продукта есть в приказе в карте
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "Обьект удалён из корзины!")
            return redirect('core:order-summary')
        else:
            messages.info(request, "Обьект не находится в вашей корзине!")
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, "У вас нет активных деталей")
        return redirect('core:product', slug=slug)
    return redirect('core:product', slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # Проверь если приказ продукта есть в приказе в карте
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, "Количество в корзине сниженно!")
            return redirect('core:order-summary')
        else:
            messages.info(request, "Обьект не находится в вашей корзине!")
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, "У вас нет активных деталей")
        return redirect('core:product', slug=slug)
    return redirect('core:product', slug=slug)
