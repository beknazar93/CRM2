import csv
from django.core.management.base import BaseCommand
from crm.models import Client

class Command(BaseCommand):
    help = 'Import clients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the CSV file.')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                clients = []
                for row in reader:
                    clients.append(Client(
                        name=row['name'],
                        email=row['email'],
                        phone=row['phone'],
                        stage=row['stage'],
                        payment=row['payment'],
                        price=row['price'],
                        sport_category=row['sport_category'],
                        trainer=row['trainer'],
                        year=row['year'],
                        month=row['month'],
                        day=row['day'],
                        comment=row['comment'],
                    ))
                Client.objects.bulk_create(clients)
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(clients)} clients.'))
        except Exception as e:
            self.stderr.write(f'Error: {e}')
