import requests
import os
from json import load
from django.core.management.base import BaseCommand
from products.models import Product, Category

API_URL = 'https://fr-en.openfoodfacts.org/cgi/search.pl'
SEARCH_HEADER = {
    "user-agent": "Purbeurre - https://github.com/finevine/Projet8"
    }


class Command(BaseCommand):
    help = 'Create DB and populate it'

    def handle(self, *args, **options):
        count = 0
        while count <= 9000:
            for page in range(1,6):            
                SEARCH_PARAM = {
                    "action": "process",
                    "tagtype_0": "countries",
                    "tag_contains_0": "contains",
                    "tag_0": "france",
                    "sort_by": "unique_scans_n",
                    "page_size": 1000,
                    "page": page,
                    "action": "process",
                    "json": 1,
                }
                req = requests.get(
                    API_URL,
                    params=SEARCH_PARAM,
                    headers=SEARCH_HEADER)
                # Output of request as a json file
                req_output = req.json()
                # Get results
                products = req_output["products"]

                for item in products:
                    # Create all categories associated to each product
                    categories = item.get('categories_tags', [])
                    categories_DB = []
                    for category in categories:
                        category_DB, created = Category.objects.update_or_create(
                            id=category,
                            defaults={
                                "id": category
                            }
                        )
                        categories_DB.append(category_DB)
                        count += 1

                    if item.get("nutriscore_grade"):
                        # Assign attributes to product
                        sugar = item["nutriments"].get("sugars_100g", 0)
                        satFat = item["nutriments"].get("saturated-fat_100g", 0)
                        salt = item["nutriments"].get("salt_100g", 0)
                        fat = item["nutriments"].get("fat_100g", 0)

                        product_DB, created = Product.objects.update_or_create(
                            code=item["code"],
                            defaults={
                                "code": item["code"],
                                "name": item.get(
                                    "product_name",
                                    item.get("product_name_fr")),
                                "nutritionGrade": item.get("nutriscore_grade"),
                                "image": item.get(
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
                        product_DB.category.set(categories_DB)
                        count += 1