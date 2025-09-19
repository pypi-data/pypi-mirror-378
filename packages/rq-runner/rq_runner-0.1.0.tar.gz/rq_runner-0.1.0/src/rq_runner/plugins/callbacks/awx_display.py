from __future__ import (absolute_import, division, print_function)

import contextlib
from collections import defaultdict
from datetime import datetime

from ansible.utils.color import colorize
from ansible_runner.display_callback.callback import awx_display

DOCUMENTATION = awx_display.DOCUMENTATION

MARK_EVENTS = [
    'playbook_on_task_start',
    'playbook_on_handler_task_start',
    'playbook_on_stats'
]


class CallbackModule(awx_display.CallbackModule):
    def __init__(self):
        super().__init__()
        self._host_total = 0
        self._prev_task = None
        self._task_data = defaultdict(dict)

    def _get_result_timing_data(self, result):
        try:
            self._task_data[result._task._uuid]['host_counter'] += 1
            result._result['progress'] = (
                f"{self._task_data[result._task._uuid]['host_counter']}/"
                f"{self._task_data[result._task._uuid]['host_total']}"
            )
        except Exception as e:
            self._display.error('Failed to set host progress: %s' % e)

        return super()._get_result_timing_data(result)

    def set_task(self, task, local=False):
        if not local:
            try:
                self._task_data[task._uuid]['name'] = task.get_name().strip()
                self._task_data[task._uuid]['host_counter'] = 0
                self._task_data[task._uuid]['host_total'] = self._host_total
                self._task_data[task._uuid]['started_at'] = datetime.now()
                self.set_task_duration()
                self._prev_task = task._uuid
            except Exception as e:
                self._display.error('Failed to set task: %s' % e)

        super().set_task(task, local)

    def set_task_duration(self):
        if not self._prev_task:
            return

        try:
            task = self._task_data[self._prev_task]
            task['ended_at'] = datetime.now()
            if not task['started_at']:
                return
            task['duration'] = (task['ended_at'] - task['started_at']).total_seconds()
        except Exception as e:
            self._display.error('Failed to set task duration: %s' % e)

    def set_options(self, task_keys=None, var_options=None, direct=None):
        setattr(self, '_load_name', awx_display.DefaultCallbackModule.CALLBACK_NAME)
        super().set_options(task_keys, var_options, direct)

    def v2_playbook_on_play_start(self, play):
        variable_manager = play.get_variable_manager()
        variable = variable_manager.get_vars(play=play)['vars']
        self._host_total = len(variable['ansible_play_hosts_all'])
        super().v2_playbook_on_play_start(play)

    def v2_playbook_on_stats(self, stats):
        self.set_task_duration()
        super().v2_playbook_on_stats(stats)

        if self._task_data:
            self._display.banner('TASK DATA')
            for v in self._task_data.values():
                if not v:
                    continue
                self._display.display(
                    u"%-46s : %-37s %s %s %s" % (
                        colorize(u'name', v['name'], awx_display.C.COLOR_OK),
                        colorize(
                            u'progress',
                            f"{v['host_counter']}/{v['host_total']}",
                            awx_display.C.COLOR_OK
                        ),
                        colorize(
                            u'started_at',
                            v.get('started_at'),
                            awx_display.C.COLOR_OK),
                        colorize(
                            u'ended_at',
                            v.get('ended_at', 'ended_at'),
                            awx_display.C.COLOR_OK
                        ),
                        colorize(
                            u'duration',
                            v.get('duration', 'NaN'),
                            awx_display.C.COLOR_OK
                        ),
                    ),
                    screen_only=True
                )

    @contextlib.contextmanager
    def capture_event_data(self, event, **event_data):
        if event in MARK_EVENTS:
            event_data['custom_task_data'] = [
                {k: str(v) for k, v in i.items()}
                for i in self._task_data.values()
            ]

        with super().capture_event_data(event, **event_data):
            yield
