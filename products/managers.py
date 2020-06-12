import products.models as m
from django.db import models


class ProductManager(models.Manager):
    def get_similar(self, name):
        # icontains for case-insensitive
        return (
            m.Product.objects.filter(
                models.Q(name__icontains=name)
                | models.Q(categories__name__icontains=name)
            ).order_by('-nutritionGrade', 'code').distinct()
        )

    def get_better(self, product_to_replace):
        # Find products from the same categories ...
        products = m.Product.objects.filter(
            categories__in=product_to_replace.categories.all())
        # ... differents from product_to_replace ...
        products = products.exclude(code=product_to_replace.code)
        # ... have a nutritionGrade > nutritionGradetoreplace :
        return products.filter(
            nutritionGrade__lte=product_to_replace.nutritionGrade
            ).order_by('nutritionGrade', 'code').distinct()
