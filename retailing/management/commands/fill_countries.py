import json

from django.core.management import BaseCommand
from django.db import connection

from retailing.models import Country


class Command(BaseCommand):

    @staticmethod
    def json_read_countries():
        with open("countries.json", "r", encoding="utf-8") as file:
            return json.load(file)

    def handle(self, *args, **options):

        countries_for_create = []
        country_sequence = 1
        sequence = 1

        self.clean_database()
        self.reset_sequences_country(country_sequence)

        for country in Command.json_read_countries():
            countries_for_create.append(
                Country(
                    sequence,
                    country["iso_code2"],
                    country["name_ru"],
                )
            )
            sequence += 1
        Country.objects.bulk_create(countries_for_create)
        self.reset_sequences_country(len(countries_for_create))

    @staticmethod
    def reset_sequences_country(country_sequence):
        """Сихронизируем автоинкрементные значения таблицы страны"""
        with connection.cursor() as cursor:
            cursor.execute(
                f"ALTER SEQUENCE retailing_country_id_seq RESTART WITH {country_sequence};"
            )

    @staticmethod
    def clean_database():
        """Очищаем таблицу страны."""
        Country.objects.all().delete()
