from django.db import models
from django.conf import settings
from django.utils.text import slugify
from itertools import chain


class ProductManager(models.Manager):
    def similar(self, name):
        return (
            Product.objects.filter(name__contains=name) |
            Product.objects.filter(category__name__contains=name)
            )

    def better(self, product_to_replace):
        # Find products from the same categories ...
        products = Product.objects.filter(
            category__id__in=product_to_replace.category.values_list('id'))
        # ... differents from product_to_replace ...
        products = products.exclude(code=product_to_replace.code)
        # ... have a nutritionGrade >= nutritionGradetoreplace :
        return products.filter(
            nutritionGrade__lte=product_to_replace.nutritionGrade
            ).order_by('nutritionGrade')


class Category(models.Model):
    '''
    name
    '''
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(
        verbose_name="Category name", max_length=400, unique=False)
    slug = models.SlugField(
        max_length=151, unique=True, editable=False, null=True)

    class Meta:
        verbose_name = "Catégorie"

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50] + '-' + str(self.id)
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    '''
    code, name, nutritionGrade, image (url),
    fat, satFat, sugar, salt, compared_to_category
    '''

    objects = ProductManager()
    code = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=True, verbose_name="Nom")
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    nutritionGrade = models.CharField(
        max_length=1, null=True, verbose_name="Nutriscore")
    image = models.URLField(null=True)

    fat = models.DecimalField(
        "Fat in 100g", max_digits=5, decimal_places=2, default=0)
    satFat = models.DecimalField(
        "Saturated fat in 100g", max_digits=5, decimal_places=2, default=0)
    sugar = models.DecimalField(
        "Sugar in 100g", max_digits=5, decimal_places=2, default=0)
    salt = models.DecimalField(
        "Salt in 100g", max_digits=5, decimal_places=2, default=0)

    category = models.ManyToManyField(
        Category,
        related_name="category",
        verbose_name="Catégorie")

    class Meta:
        verbose_name = "Produit"
        ordering = ['category__id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50] + '-' + str(self.code)
        super(Product, self).save(*args, **kwargs)


class Favourite(models.Model):
    ''' codeHealthy, codeUnhealthy '''
    healthy_product = models.ForeignKey(
        'Product', related_name="healthy", on_delete=models.CASCADE)
    unhealthy_product = models.ForeignKey(
        'Product', related_name="unhealthy", on_delete=models.CASCADE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['healthy_product', 'unhealthy_product'],
                name='unique_favourite')
        ]
        ordering = ['healthy_product']

