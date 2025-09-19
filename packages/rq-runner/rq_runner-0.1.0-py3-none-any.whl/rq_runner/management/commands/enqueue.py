from django.conf import settings
from django.core.management import BaseCommand

from rq.cli.cli import enqueue


class Command(BaseCommand):
    help = 'Enqueues a job from the command line.'

    def run_from_argv(self, argv):
        self.handle(
            f'--url={settings.REDIS_URL}',
            f'--job-class=rq_runner.job.AnsibleJob',
            *argv[2:]
        )

    def handle(self, *args, **options):
        enqueue(args)
