import requests
import os
import django.core.exceptions as exceptions
from django.db import IntegrityError
from json import load
from django.core.management.base import BaseCommand
from products.models import Product, Category

API_URL = 'https://fr-en.openfoodfacts.org/cgi/search.pl'
SEARCH_HEADER = {
    "user-agent": "Purbeurre - https://github.com/finevine/Projet8"
    }


class Command(BaseCommand):
    help = 'Create DB and populate it'

    def get_products(self, page):
        SEARCH_PARAM = {
            "action": "process",
            "tagtype_0": "countries",
            "tag_contains_0": "contains",
            "tag_0": "france",
            "sort_by": "unique_scans_n",
            "page_size": 500,
            "page": page,
            "json": 1,
        }
        req = requests.get(
            API_URL,
            params=SEARCH_PARAM,
            headers=SEARCH_HEADER)
        # Output of request as a json file
        req_output = req.json()
        # Get results
        return req_output["products"]

    def create_categories_in_DB(self, categories, category_names):
        ''' from a list of categories id, return list of created object categories
        categories (list of strings)
        category_names (dict)'''
        categories_res = []
        for category in categories:
            if category and category_names.get(category, ''):
                try:
                    category_DB, created = Category.objects.get_or_create(
                        id=category,
                        defaults={
                            "id": category,
                            "name": category_names.get(category)
                        })
                    categories_res.append(category_DB)
                except IntegrityError:
                    pass

        return categories_res

    def create_product_in_DB(self, product):
        '''return product in DB created if nutriscore_grade else None'''
        sugar = product["nutriments"].get("sugars_100g", 0)
        satFat = product["nutriments"].get("saturated-fat_100g", 0)
        salt = product["nutriments"].get("salt_100g", 0)
        fat = product["nutriments"].get("fat_100g", 0)

        # If product has nutritiongrade
        if product.get("nutriscore_grade"):
            code_to_store = int(product["code"])
            product_DB, created = Product.objects.get_or_create(
                code=code_to_store,
                defaults={
                    "code": code_to_store,
                    "name": product.get(
                        "product_name", product.get("product_name_fr")),
                    "nutritionGrade": product.get("nutriscore_grade"),
                    "image": product.get(
                        "selected_images", {}).get(
                            "front", {}).get(
                                "display", {}).get(
                                    "fr"),
                    "sugar": sugar,
                    "satFat": satFat,
                    "salt": salt,
                    "fat": fat,
                },
            )
            return product_DB
        else:
            return None

    def handle(self, *args, **options):
        count = 0
        # Open json of all categories to associate id & names
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "categories_cleaned.json"), 'r') as json_file:
            category_names = load(json_file)

        # pages of openFoodFacts request
        broken = False
        for page in range(1, 18):
            if broken:
                break
            print(f'page {page} ({count} save in DB)')
            products = self.get_products(page)
            for product in products:
                # limit to products (Heroku_db < 10000 rows)
                if count >= 9000:
                    broken = True
                    break
                    print(f'page {page} ({count} save in DB)')

                product_DB = self.create_product_in_DB(product)
                count += 1

                # assign product 'compared_to_category' attribute
                if product_DB:
                    # if False:
                    # categories of the product
                    categories = product.get('categories_tags', [])[:3]
                    # categories createdin DB
                    if categories:
                        categories_DB = self.create_categories_in_DB(
                            categories, category_names)
                        # add to product :
                        product_DB.categories.set(categories_DB)
                        count += len(categories_DB)

                    try:
                        category_to_compare = self.create_categories_in_DB(
                            [product.get("compared_to_category")],
                            category_names)
                        count += 1
                        product_DB.compared_to_category = category_to_compare[0]
                        product_DB.save()
                    except (exceptions.ObjectDoesNotExist, IndexError):
                        product_DB.compared_to_category = None
                        product_DB.save()
