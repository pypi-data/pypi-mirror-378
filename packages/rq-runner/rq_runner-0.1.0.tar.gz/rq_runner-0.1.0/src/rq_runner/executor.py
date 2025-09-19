import json
import logging
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from ansible_runner import Runner, RunnerConfig
from ansible_runner.utils import dump_artifact, signal_handler
from rq import get_current_job

if TYPE_CHECKING:
    from rq.job import Job

from .utils import get_ansible_cfg

from .plugins import BASE_DIR

logger = logging.getLogger(__name__)


class AnsibleExecutor:
    def __init__(self):
        self._job = None
        self._event_handler = None
        self._status_handler = None
        self._artifacts_handler = None
        self._finished_callback = None
        self._env_vars = {
            'ANSIBLE_CONFIG': get_ansible_cfg(),
            'ANSIBLE_STDOUT_CALLBACK': 'default',
            'ANSIBLE_CALLBACK_FORMAT_PRETTY': True,
            'ANSIBLE_CALLBACK_RESULT_FORMAT': 'yaml',
            'AWX_LIB_DIRECTORY': str(BASE_DIR / 'callbacks'),
        }

    @property
    def job(self) -> Optional['Job']:
        if self._job is None:
            self._job = get_current_job()
        return self._job

    def event_handler(self, event_data: dict[str, Any]) -> bool:
        if self._job:
            self._job.event_handler(event_data)

        if self._event_handler:
            self._event_handler(event_data)

        return event_data.get('event') == 'playbook_on_stats'

    def status_handler(
            self,
            status_data: dict[str, Any],
            runner_config: 'RunnerConfig'
    ):
        if self._job and (status := status_data.get('status')) == 'running':
            self._job.status_handler({
                'status': status,
                'inventory': str(runner_config.inventory),
            })

        if self._status_handler is not None:
            self._status_handler(status_data, runner_config)

    def artifacts_handler(self, artifact_dir: str):
        if self._artifacts_handler is not None:
            self._artifacts_handler(artifact_dir)

    def finished_callback(self, runner: 'Runner'):
        try:
            if runner.stats and (failures := runner.stats.get('failures')):
                filename = Path(runner.config.artifact_dir) / 'retry_hosts'
                with open(filename, 'w') as f:
                    f.write('\n'.join(failures))
                logger.warning(f'To retry, use: --limit @{filename}\n')
        except Exception as e:
            logger.error('Save retry hosts failed: %s', e)

        if self._finished_callback is not None:
            self._finished_callback(runner)

    def __call__(self, *args, **kwargs):
        if self.job:
            kwargs['ident'] = self.job.id
        kwargs.setdefault('private_data_dir', None)
        kwargs.setdefault('suppress_env_files', True)
        kwargs['envvars'] = self._env_vars | kwargs.pop('envvars', {})
        for name in (
                'event_handler',
                'status_handler',
                'artifacts_handler',
                'finished_callback'
        ):
            setattr(self, f'_{name}', kwargs.pop(name, None))

        rc = RunnerConfig(**kwargs)
        if isinstance(rc.inventory, MutableMapping):
            rc.inventory = dump_artifact(
                obj=json.dumps(rc.inventory, indent=4),
                path=rc.artifact_dir,
                filename='hosts.json'
            )
        rc.prepare()
        r = Runner(
            rc,
            cancel_callback=signal_handler(),
            event_handler=self.event_handler,
            status_handler=self.status_handler,
            finished_callback=self.finished_callback
        )
        if self.job:
            setattr(self.job, 'runner', r)
            logger.info('Running job %s', str(self.job.id))

        return r.run()
