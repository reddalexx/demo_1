from django.contrib.auth.models import  User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Create superuser --username USER --password PWD --email it@email.com"

    def add_arguments(self, parser):
        parser.add_argument('--username',
                            help='Username')
        parser.add_argument('--password',
                            help='Password')
        parser.add_argument('--email',
                            help='Email')

    def handle(self, *args, **options):
        user, created = User.objects.update_or_create(
            username=options['username'],
            is_superuser=True,
            is_staff=True,
            defaults=dict(
                email=options['email'],
                is_active=True))

        if created:
            user.set_password(options['password'])
            user.save()

        print('Superuser "{}" is {}'.format(
            options['username'], 'created' if created else 'updated')
        )
