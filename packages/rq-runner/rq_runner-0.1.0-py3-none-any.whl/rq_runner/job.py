import logging
from typing import Any, TYPE_CHECKING, Optional

from rq.job import Job
from rq.timeouts import BaseDeathPenalty
from rq.utils import import_attribute

if TYPE_CHECKING:
    from ansible_runner import Runner
    from redis.client import Pipeline
    from rq_result.backends import DatabaseBackend

from .plugins.callbacks.awx_display import MARK_EVENTS

logger = logging.getLogger(__name__)


class AnsibleJob(Job):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backend = None
        self._backend_class = 'rq_result.backends.DatabaseBackend'
        self._runner: Optional['Runner'] = None

    @property
    def backend(self) -> 'DatabaseBackend':
        if self._backend is None:
            self._backend = import_attribute(self._backend_class)()
        return self._backend

    @property
    def runner(self) -> Optional['Runner']:
        return self._runner

    @runner.setter
    def runner(self, runner: Optional['Runner']):
        self._runner = runner

    def event_handler(self, event_data: dict[str, Any]) -> bool:
        try:
            if (
                    (ev := event_data.get('event')) in MARK_EVENTS and
                    (evd := event_data.get('event_data')) and
                    (custom_data := evd.get('custom_task_data'))
            ):
                self.meta['tasks'] = custom_data
                if ev == 'playbook_on_stats':
                    self.meta['stats'] = {'failures': evd.get('failures', {})}
                self.backend.store_result(self.id, meta=self.meta)
        except Exception as e:
            logger.error(f'Event handler error: {e}')

        return True

    def status_handler(self, status_data: dict[str, Any]):
        self.backend.store_result(self.id, **status_data)

    def _execute(self) -> Any:
        data = {
            'name': self.func_name,
            'meta': self.meta,
            'kwargs': self.kwargs,
            'description': self.description,
            'status': 'started',
            'queue': self.origin,
            'worker_name': self.worker_name or '',
            'group_id': self.group_id or '',
            'started_at': self.started_at,
            'enqueued_at': self.enqueued_at,
        }
        self.status_handler(data)
        return super()._execute()

    def _handle_success(self, result_ttl, pipeline: 'Pipeline', worker_name: str = ''):
        super()._handle_success(result_ttl, pipeline, worker_name)
        data = {
            'meta': self.meta,
            'status': 'finished',
            'ended_at': self.ended_at,
        }
        if not self._result is None:
            data['result'] = str(self._result)
        if not self._exc_info is None:
            data['exc_info'] = str(self._exc_info)
        if self.runner:
            data['rc'] = self.runner.rc
            data['status'] = self.runner.status
        self.status_handler(data)

    def _handle_failure(
            self,
            exc_string: str,
            pipeline: 'Pipeline',
            worker_name: str = ''
    ):
        super()._handle_failure(exc_string, pipeline, worker_name)
        data = {
            'meta': self.meta,
            'status': 'failed',
            'exc_info': exc_string,
            'ended_at': self.ended_at,
        }
        if not self._result is None:
            data['result'] = str(self._result)
        if self.runner:
            data['rc'] = self.runner.rc
        self.status_handler(data)

    def execute_stopped_callback(self, death_penalty_class: type[BaseDeathPenalty]):
        super().execute_stopped_callback(death_penalty_class)
        self.status_handler({
            'meta': self.meta,
            'status': 'stopped'
        })
