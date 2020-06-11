from django.core.management.base import BaseCommand, CommandError
from products.models import Product, Category

class Command(BaseCommand):
    help = 'clean DB'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--all', type=bool, default=False, help='If drop all table')

    def handle(self, *args, **kwargs):
        # not used here
        all = kwargs['all']
        if all:
            Product.objects.all().delete()
            Category.objects.all().delete()
        else:
            Product.objects.all().delete()
