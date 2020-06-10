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
        self.assertEquals(
            Product.objects.get(code=3274080005003).name,
            "Eau de source")

        self.assertEquals(
            Product.objects.get(code=3274080005003).compared_to_category.id,
            "en:unsweetened-beverages")
        
        # test the manytomanyfield is used well
        mock_categories = Product.objects.get(
            code=3274080005003).category.all()
        water_cat = MOCK_REQUEST['products'][0]["categories_tags"]
        self.assertCountEqual(
            [m.id for m in mock_categories],
            water_cat)

class TestNutella(TestCase):

    @patch('products.management.commands.init_db.requests.get')
    def test_init_nutella(self, mock_request):
        # replace json by a small mock openff request with only 3 product
        mock_request.return_value.json.return_value = NUTELLA
        call_command('init_db')
        nutella = Product.objects.get(code=3017620422003)
        self.assertEquals(nutella.name, "Nutella")


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


