from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from crm.models import Client


class Command(BaseCommand):
    help = 'Удаляет клиентов, данные которых старше 4 месяцев'

    def handle(self, *args, **kwargs):
        # Рассчитываем дату 4 месяца назад
        cutoff_date = datetime.now() - timedelta(days=4 * 30)

        # Удаляем клиентов, созданных более 4 месяцев назад
        old_clients = Client.objects.filter(created_at__lt=cutoff_date)
        count = old_clients.count()
        old_clients.delete()

        # Вывод информации в консоль
        self.stdout.write(self.style.SUCCESS(f'{count} старых клиентов удалено'))
