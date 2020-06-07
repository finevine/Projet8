from decimal import Decimal
from django.test import TestCase
from django.db.utils import IntegrityError
from products.models import Product, Category


class TestProductsModels(TestCase):

    @classmethod  # <- setUpTestData must be a class method
    def setUpTestData(cls):
        ''' Create product '''
        cls.prod1 = Product.objects.create(
            name="Coco colo",
            code="123456",
            fat=12.34,
            nutritionGrade="a")
        Product.objects.create(
            name='a'*100,
            code="456")
        Product.objects.create(
            name="Cocu colu",
            code="789")
        cls.cat = Category.objects.create(
            id="Test:Category",
            name="Test Category"
        )
        # Or we can write : self.product1 = Product.object
        
        cls.prod1 = Product.objects.get(code="123456")
        cls.prod2 = Product.objects.get(code="456")

    def setUp(self):
        pass

    def test_product_created(self):
        self.assertEqual(self.prod1.name, "Coco colo")
        self.assertEqual(self.prod1.code, 123456)
        # How admin see product in dashboard
        verbose_name = self.prod1._meta.verbose_name
        self.assertEqual(verbose_name, "Produit")
        # How admin see name in dashboard
        name_verbose_name = self.prod1._meta.get_field('name').verbose_name
        self.assertEqual(name_verbose_name, "Nom")
        # How admin see nutritiongrade in dashboard
        nutrition_verbose_name = self.prod1._meta.get_field('nutritionGrade').verbose_name
        self.assertEqual(nutrition_verbose_name, "Nutriscore")
        # max_length authorized length
        nutrition_max_length = self.prod1._meta.get_field('nutritionGrade').max_length
        self.assertEqual(nutrition_max_length, 1)

    def test_product_slug_create(self):
        self.assertEqual(self.prod1.slug, 'coco-colo-123456')

    def test_integrity_error(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(name="Coco colo bis", code="123456")

    def test_caracteristic_100g_saved_ok(self):
        self.assertEqual(
            self.prod1.fat + self.prod1.satFat + self.prod1.sugar + self.prod1.salt,
            Decimal('12.34'))

    def test_slug_of_product(self):
        self.assertEqual(
            self.prod2.slug,
            'a' * 50 + '-456')

    def test_code_other_that_int(self):
        with self.assertRaises(ValueError):
            Product.objects.create(name="Cycy coly", code="abcd")

    def test_str(self):
        self.assertEqual(str(self.prod1), "Coco colo")
        self.assertEqual(str(self.cat), "Test:Category")
