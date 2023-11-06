from random import randint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, logout
from .models import *
from .forms import *
from .utils import *
import stripe
from config import settings

# Create your views here.
class ProductList(ListView):
    model = Product
    context_object_name = 'categories'
    extra_context = {
        'title': 'TOTEMBO: главная страница'
    }
    template_name = 'store/product_list.html'

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)

        return categories


class CategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_page.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        main_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = main_category
        context['title'] = f'Категория: {main_category.title}'
        return context

    def get_queryset(self):
        sort_field = self.request.GET.get('sort')
        type_field = self.request.GET.get('type')  # podkategoriyano olish

        if type_field:
            products = Product.objects.filter(category__slug=type_field)
            return products
        main_category = Category.objects.get(slug=self.kwargs['slug'])
        subcategories = main_category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)

        if sort_field:
            products = products.order_by(sort_field)
        return products


class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'{product.title}'

        products = Product.objects.all()
        data = []
        for i in range(4):
            random_index = randint(0, len(products) - 1)
            p = products[random_index]
            if p not in data:
                data.append(p)
        context['products'] = data
        context['reviews'] = Review.objects.filter(product=product)

        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForms()

        return context


class AddReview(View):

    def post(self,request,pk):
        form = ReviewForms(request.POST)
        print(request.POST)
        product =  Product.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.product = product
            form.save()
        return redirect(product.get_absolute_url())

class ReviewList(ListView):
    model = Review
    context_object_name = 'comments'
    template_name = 'store/components/_reviews.html'




def login_registration(request):
    context = {
        'title': 'Войти или зарегистрироваться',
        'login_form': LoginForm(),
        'register_form': RegistrationForm()
    }

    return render(request, 'store/login_register.html', context)


def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)

        return redirect('product_list')
    else:

        return redirect('login_registration')


def user_logout(request):
    logout(request)

    return redirect('login')


def register(request):
    form = RegistrationForm(data=request.POST)
    if form.is_valid():
        user = form.save()
        return redirect('product_list')

    return redirect('login_registration')


def save_favourite_product(request, product_slug):
    user = request.user if request.user.is_authenticated else None
    product = Product.objects.get(slug=product_slug)
    favourite_products = FavouriteProducts.objects.filter(user=user)
    if user:
        if product in [i.product for i in favourite_products]:
            fav_product = FavouriteProducts.objects.get(user=user, product=product)
            fav_product.delete()
        else:
            FavouriteProducts.objects.create(user=user, product=product)
    next_page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(next_page)


class FavouriteProductView(ListView, LoginRequiredMixin):
    model = FavouriteProducts
    context_object_name = 'products'
    template_name = 'store/favourite_products.html'
    login_url = 'login_registration'

    def get_queryset(self):
        user = self.request.user
        favs = FavouriteProducts.objects.filter(user=user)
        products = [i.product for i in favs]
        return products


def cart(request):
    cart_info = get_cart_data(request)

    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'products': cart_info['products'],
        'title' : 'Корзина'
    }

    return render(request, 'store/cart.html', context)


def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, product_id, action)
        return redirect('cart')
    else:

        return redirect('login_registration')


class SearchResults(ListView):
    def get_queryset(self):
        word = self.request.GET.get('q').capitalize()
        product = Product.objects.filter(title__icontains=word)
        return product



def checkout(request):

    cart_info = get_cart_data(request)
    context = {
        'cart_total_quantity' : cart_info['cart_total_quantity'],
        'order' : cart_info['order'],
        'products' : cart_info['products'],
        'title' : 'Оформления заказа',
        'customer_form' :  CustomerForm(),
        'shipping_form' : ShippingForm()
    }
    return render(request,'store/checkout.html',context)


def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        total_price = cart_info['cart_total_price']
        session = stripe.checkout.Session.create(
            line_items = [{
                'price_data': {
                    'currency' : 'usd',
                    'product_data' : {
                        'name' : 'Товар сайта Ustora'
                    },
                    'unit_amount' : int(total_price*100)
                },
                'quantity' : 1
            }],
            mode='payment',
            success_url = request.build_absolute_uri(reverse('product_list')),
            cancel_url = request.build_absolute_uri(reverse('checkout'))

        )
        return redirect(session.url,303)


def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
        quantity = order_product.quantity
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.save()
    return redirect('cart')