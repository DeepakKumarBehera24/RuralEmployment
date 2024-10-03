# management/commands/check_subscriptions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Subscription


class Command(BaseCommand):
    help = 'Check and deactivate expired subscriptions'

    def handle(self, *args, **kwargs):
        expired_subscriptions = Subscription.objects.filter(end_date__lte=timezone.now()).exclude(
            subscription_type='lifetime')

        for subscription in expired_subscriptions:
            subscription.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deactivated subscription for {subscription.user.username}'))
