from django.conf import settings
from django.core.management import BaseCommand

from rq.cli import worker


class Command(BaseCommand):
    help = 'Starts an RQ worker.'

    def run_from_argv(self, argv):
        self.handle(
            f'--url={settings.REDIS_URL}',
            f'--job-class=rq_runner.job.AnsibleJob',
            *argv[2:]
        )

    def handle(self, *args, **options):
        worker(args)
