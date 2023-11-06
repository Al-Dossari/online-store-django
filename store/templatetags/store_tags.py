from django import template
from store.models import Category, Product, FavouriteProducts

register = template.Library()


@register.simple_tag()
def get_categories():
   return Category.objects.filter()



@register.simple_tag()
def get_products():
    return Product.objects.all()


@register.simple_tag()
def get_categories_nav():
    return Category.objects.filter(parent=None)


@register.simple_tag()
def get_subcategories(category):
    return Category.objects.filter(parent=category)


@register.simple_tag()
def get_sorted():
    sorters = [
        {
            'title': 'По цене',
            'sorters': [
                ('price', 'По возрастанию'),
                ('-price', 'По убыванию'),
            ]
        },

        {
            'title': 'По цвету',
            'sorters': [
                ('color', 'По цвету'),
            ]
        },

        {
            'title': 'По размеру',
            'sorters': [
                ('size', 'По возрастанию'),
                ('-size', 'По убыванию'),
            ]
        }
    ]
    return sorters


@register.simple_tag()
def get_favourite_products(user):
    fav = FavouriteProducts.objects.filter(user=user)
    products = [i.product for i in fav]
    print(f'Liked {user} {products}')
    return products