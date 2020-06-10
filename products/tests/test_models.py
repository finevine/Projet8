from decimal import Decimal
from django.test import TestCase
from django.db.utils import IntegrityError
from products.models import Product, Category


class TestProductsModels(TestCase):

    @classmethod  # <- setUpTestData must be a class method
    def setUpTestData(cls):
        ''' Create product and categories '''
        # Categories
        cls.cat1 = Category.objects.create(
            id="cat1",
            name="Test Category 1",
        )
        cls.cat2 = Category.objects.create(
            id="cat2",
            name="Test Category 2",
        )
        # Products
        cls.goodprod = Product.objects.create(
            name="Good Coca",
            code=999999,
            fat=12.34,
            nutritionGrade="a",
            compared_to_category=cls.cat1)
        cls.longprod = Product.objects.create(
            name='a'*100,
            code=456,
            compared_to_category=cls.cat1)
        cls.badprod = Product.objects.create(
            name="Bad Coca",
            code=000000,
            nutritionGrade="e",
            compared_to_category=cls.cat1)

    def setUp(self):
        pass

    def test_product_created(self):
        '''test products creation'''
        self.assertEqual(self.goodprod.name, "Good Coca")
        self.assertEqual(self.goodprod.code, 999999)
        # How admin see product in dashboard
        verbose_name = self.goodprod._meta.verbose_name
        self.assertEqual(verbose_name, "Produit")
        # How admin see name in dashboard
        name_verbose_name = self.goodprod._meta.get_field('name').verbose_name
        self.assertEqual(name_verbose_name, "Nom")
        # How admin see nutritiongrade in dashboard
        nutrition_verbose_name = self.goodprod._meta.get_field('nutritionGrade').verbose_name
        self.assertEqual(nutrition_verbose_name, "Nutriscore")
        # max_length authorized length
        nutrition_max_length = self.goodprod._meta.get_field('nutritionGrade').max_length
        self.assertEqual(nutrition_max_length, 1)

    def test_product_slug_create(self):
        self.assertEqual(self.goodprod.slug, 'good-coca-999999')

    def test_integrity_error(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(name="Good coca bis", code=999999)

    def test_caracteristic_100g_saved_ok(self):
        self.assertEqual(
            self.goodprod.fat + self.goodprod.satFat + self.goodprod.sugar + self.goodprod.salt,
            12.34)

    def test_slug_of_product(self):
        self.assertEqual(
            self.longprod.slug,
            'a' * 50 + '-456')

    def test_code_other_that_int(self):
        with self.assertRaises(ValueError):
            Product.objects.create(name="Inappropriate coca", code="abcd")

    def test_str(self):
        self.assertEqual(str(self.goodprod), "Good Coca")
        self.assertEqual(str(self.cat1), "cat1")

    def test_product_category_assignment(self):
        self.goodprod.category.add(self.cat1)
        self.goodprod.category.add(self.cat2)
        self.assertQuerysetEqual(
            self.goodprod.category.all(),
            [repr(self.cat1), repr(self.cat2)], ordered=False)

    def test_similar_method(self):
        self.goodprod.category.add(self.cat1)
        self.longprod.category.add(self.cat2)
        # 2 categories were created using "name Test Category"
        cat = Product.objects.filter(category__name__contains='Test Category')
        self.assertEquals(cat.count(), 2)

    def test_better_method(self):
        self.goodprod.category.add(self.cat1)
        self.badprod.category.add(self.cat1)
        # select all products that are better than badprod
        result = Product.objects.better(self.badprod)
        self.assertTrue(999999 in [prod.code for prod in result])