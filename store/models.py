from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Наименование категории')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Изображения')
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Категория',
                               related_name='subcategories')

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Категория: pk={self.pk}, title={self.title}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name='Наименование продукта')
    price = models.FloatField(verbose_name='Цена ($)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    quantity = models.IntegerField(default=0, verbose_name='Количество товара')
    description = models.TextField(default='Здесь скоро будет описание', verbose_name='Описание товара')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', related_name='products')
    slug = models.SlugField(unique=True, null=True)
    size = models.TextField(max_length=100, verbose_name='Информация')
    color = models.CharField(max_length=50, default='Вводите цвет товара', verbose_name='Цвет')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Товар: pk={self.pk}, title={self.title}, price={self.price}'

    def get_first_photo(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return 'https://cdn4.iconfinder.com/data/icons/prohibited/100/16-1024.png'
        else:
            return 'https://cdn4.iconfinder.com/data/icons/prohibited/100/16-1024.png'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Изображения')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения товаров'


class Review(models.Model):
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} {self.text} {self.product.title}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

class FavouriteProducts(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='Ползователь')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,verbose_name='Продукт')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранный товары'


class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.SET_NULL,blank=True,null=True,verbose_name='Покупатель')
    first_name = models.CharField(max_length=250,verbose_name='Имя покупателья',default='')
    last_name = models.CharField(verbose_name='Фамилия покупателья',max_length=255,default='')

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,blank=True,null=True,verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Дата заказа')
    shipping = models.BooleanField(default=True,verbose_name='Доставка')

    def __str__(self):
        return self(self.pk) + " "

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = 'Заказы'



    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price


    @property
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity
class OrderProduct(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,verbose_name='Продукт')
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,verbose_name='Заказ')
    quantity = models.IntegerField(default=0,null=True,blank=True,verbose_name='Количество')

    def __str__(self):
        return self.product

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'


    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


    class Meta:
        verbose_name = 'Адресс Доставки'
        verbose_name_plural = 'Адресс доставок'