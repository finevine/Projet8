import os
from json import load
from unittest.mock import patch, mock_open
from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product, Category, Favourite
from django.core.management import call_command
from .mock_off_small import MOCK_REQUEST
from .mock_off_nutella import NUTELLA


class TestInitDB(TestCase):

    @patch('products.management.commands.init_db.requests.get')
    def test_init_db(self, mock_request):
        # replace json by a small mock openff request with only 3 product
        mock_request.return_value.json.return_value = MOCK_REQUEST
        # import pdb
        # pdb.set_trace()
        call_command('init_db')
        # check only 2 products are saved :
        self.assertEquals(Product.objects.all().count(), 3)
        # water was in the set :
        eau_de_source = Product.objects.get(code=3274080005003)
        self.assertEquals(
            eau_de_source.name,
            "Eau de source")

        self.assertEquals(
            eau_de_source.compared_to_category.id,
            "en:unsweetened-beverages")
        
        # test the manytomanyfield is used well
        mock_categories = Product.objects.get(
            code=3274080005003).category.all()
        water_cat = MOCK_REQUEST['products'][1]["categories_tags"]
        # Compare categories of product 1 in json and product 3274080005003
        self.assertListEqual([cat.id for cat in eau_de_source.category.all()],
            ["en:beverages", "en:waters"]
        )
        # Check that product without nutritionscore is not saved 
        self.assertFalse(Product.objects.filter(code=123456781).exists())


class TestInitDuplicates(TestCase):

    @patch('products.management.commands.init_db.requests.get')
    def test_init_nutella(self, mock_request):
        # replace json by a small mock openff request with only 3 product
        mock_request.return_value.json.return_value = NUTELLA
        call_command('init_db')
        nutella = Product.objects.get(code=3017620422003)
        self.assertEquals(nutella.name, "Nutella")
        self.assertFalse(Product.objects.filter(name="Nutella doublon").exists())
        self.assertEquals(len(list(
            Product.objects.filter(code=3017620422003).order_by('code')
            )), 1)


class TestRealOFFPage(TestCase):

    @patch('products.management.commands.init_db.requests.get')
    def test_init_nutella(self, mock_request):
        # Open json of all categories to associate id & names
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "mock_off_real.json"), 'r') as json_file:
            REAL_JSON = load(json_file)
        # replace json by a big mock openff request
        mock_request.return_value.json.return_value = REAL_JSON
        call_command('init_db')
        nutella = Product.objects.get(code=3017620422003)
        self.assertEquals(nutella.name, "Nutella")
        self.assertFalse(Product.objects.filter(name="Nutella doublon").exists())
        self.assertEquals(len(list(
            Product.objects.filter(code=3017620422003).order_by('code')
            )), 1)

class TestCleanDB(TestCase):

    def test_clean_db(self):
        user1 = User.objects.create_user(
            'user1name',
            'user1@email.com',
            'user1password')
        products = [Product.objects.create(code=str(i)) for i in range(2)]
        Category.objects.create(id="fr:fruits")
        Favourite.objects.create(
            healthy_product=products[0],
            unhealthy_product=products[1],
            owner=user1)

        # Test clean only Products
        call_command('clean_db')
        count_prod = Product.objects.all().count()
        count_cat = Category.objects.all().count()
        count_fav = Favourite.objects.all().count()
        self.assertEquals(count_prod, 0)
        self.assertEquals(count_cat, 1)
        self.assertEquals(count_fav, 0)

        # Test clean also Categories
        call_command('clean_db', '-all')
        count_prod = Product.objects.all().count()
        count_cat = Category.objects.all().count()
        count_fav = Favourite.objects.all().count()
        self.assertEquals(count_prod, 0)
        self.assertEquals(count_cat, 0)
        self.assertEquals(count_fav, 0)


