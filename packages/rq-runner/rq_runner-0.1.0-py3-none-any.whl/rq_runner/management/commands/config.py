from django.conf import settings
from django.core.management import BaseCommand
from dynaconf.utils.inspect import inspect_settings


class Command(BaseCommand):
    help = 'Debug settings.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        inspect_settings(settings, dumper='yaml', print_report=True)
