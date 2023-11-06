from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe

# Register your models here.

class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title','parent','get_products_count')
    prepopulated_fields = {'slug': ('title',)}


    def get_products_count(self,obj):
        if obj.products:
            return str(len(obj.products.all()))

        else:
            return '0'

    get_products_count.short_description = 'Количества товаров'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk','title','category','quantity','price','created_at','size','color','get_photo')
    list_editable = ('price','quantity','size','color')
    list_display_links = ('title',)
    list_filter = ('title','price','category')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryInline]

    def get_photo(self,obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75px">')
            except:
                return '-'
        else:
            return '-'

    get_photo.short_description = 'Рисунки'

admin.site.register(Gallery)
admin.site.register(Review)