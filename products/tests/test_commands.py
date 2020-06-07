from unittest.mock import patch, mock_open
from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product, Category, Favourite
from django.core.management import call_command
from .mock import MOCK_CATEGORIES, MOCK_OPENFF_REQUEST


class MockOFF():
    '''class to mock Google Map search'''
    def __init__(self, url, params=None, headers=None, **kwargs):
        pass

    @staticmethod
    def json():
        return MOCK_OPENFF_REQUEST

class TestInitDB(TestCase):

    @patch('products.management.commands.init_db.requests.get', MockOFF)
    # replace open by mock_categories
    @patch('builtins.open', mock_open(read_data=MOCK_CATEGORIES))
    def test_init_db(self, mock_request):
        # replace json by mock openff request with only 1 product
        mock_request.return_value.json.return_value = MOCK_OPENFF_REQUEST
        call_command('init_db')
        count = Product.objects.all().count()
        self.assertEquals(count, 1)
        self.assertEquals(
            Product.objects.get(code=3034470003107).name,
            "Benco original")


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


