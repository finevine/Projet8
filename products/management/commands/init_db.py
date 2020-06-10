import requests
import os
import django.core.exceptions as exceptions
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
            "page_size": 1000,
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

    def created_category(self, category, category_names):
        '''category (string)
        category_names (dict)'''
        category_DB, created = Category.objects.get_or_create(
            id=category,
            defaults={
                "id": category,
                "name": category_names.get(category, '')
            })
        return category_DB

    def handle(self, *args, **options):
        count = 0
        # Open json of all categories
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "categories_cleaned.json"), 'r') as json_file:
            category_names = load(json_file)

        for page in range(1, 6):
            print('page '+ str(page))
            if count >= 6000:
                break
            products = self.get_products(page)

            for product in products:
                code_to_store=int(product["code"])
                # limit to 5000 products (Heroku_db < 10000 rows)
                if count >= 6000:
                    break

                try:
                    Product.objects.get(code=code_to_store)
                    pass
                except exceptions.ObjectDoesNotExist:
                    # Assign attributes to product
                    sugar = product["nutriments"].get("sugars_100g", 0)
                    satFat = product["nutriments"].get("saturated-fat_100g", 0)
                    salt = product["nutriments"].get("salt_100g", 0)
                    fat = product["nutriments"].get("fat_100g", 0)

                    # If product has nutritiongrade
                    if product.get("nutriscore_grade"):
                        product_DB, created = Product.objects.get_or_create(
                                code=code_to_store,
                                defaults={
                                    "code": code_to_store,
                                    "name": product.get("product_name", product.get("product_name_fr")),
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

                        if created:
                            categories = product.get('categories_tags', [])
                            categories_DB = []
                            for category in categories:
                                # create category in DB :
                                categories_DB.append(
                                    self.created_category(category, category_names)
                                )
                            # add to product :
                            product_DB.category.set(categories_DB)

                            # assign product 'compared_to_category' attribute
                            try:
                                category_to_compare = Category.objects.get(
                                        id=product.get("compared_to_category"))
                                product_DB.compared_to_category=category_to_compare
                                product_DB.save()
                            except exceptions.ObjectDoesNotExist:
                                product_DB.compared_to_category=None
                                product_DB.save()
                            count += 1
