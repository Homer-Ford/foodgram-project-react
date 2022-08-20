import csv
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredients


class Command(BaseCommand):
    """Экспорт из csv файлов в нашу базу данных."""

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'data',
                               'ingredients.csv'), 'r', encoding='UTF-8') as f:
            csv_reader = csv.reader(f, delimiter=',')
            for row in csv_reader:
                Ingredients.objects.create(name=row[0],
                                           measurement_unit=row[1])
