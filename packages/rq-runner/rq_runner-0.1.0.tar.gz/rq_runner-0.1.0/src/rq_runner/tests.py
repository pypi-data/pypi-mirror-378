from django.conf import settings
from django.test import TestCase
from redis import Redis
from rq import Queue

from .executor import AnsibleExecutor
from .job import AnsibleJob


class JobTestCase(TestCase):
    @staticmethod
    def adhoc():
        inventory = {
            'all': {
                'children': {
                    'test': {
                        'hosts': {
                            f'test_{i}': {
                                'plat': "test",
                                'sid': i,
                                'ansible_host': 'localhost',
                                'ansible_connection': 'local',
                            }
                            for i in range(3)
                        }
                    }
                },
                'vars': {}
            }
        }
        e = AnsibleExecutor()
        r = e(
            host_pattern='all',
            inventory=inventory,
            module='shell',
            module_args='ls -l /tmp',
            verbosity=2,
        )
        return r

    def test_job(self):
        conn = Redis.from_url(settings.REDIS_URL)
        q = Queue(
            'test',
            connection=conn,
            is_async=False,
            job_class=AnsibleJob,
        )
        job = q.enqueue(self.adhoc)
        print('job:', job)
        print('result:', job._result)
        print('exc_info:', job._exc_info)
