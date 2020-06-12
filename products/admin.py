from django.contrib import admin
from . models import Product, Favourite


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'nutritionGrade',)
    list_filter = ('nutritionGrade',)
    ordering = ('categories', 'nutritionGrade', )
    search_fields = ('name', 'categories',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Favourite)
