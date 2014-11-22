from eden import db

from eden.model import Task
from eden.util import json_decode, json_encode


class TaskMapper(object):

    def find_by_cron_id(self, cron_id):
        res = db.query_one('SELECT * FROM cron WHERE cron_id=%s', (cron_id,))
        if res:
            return self._load(res)

    def find(self, name):
        res = db.query_one('SELECT * FROM cron WHERE name=%s', (name,))
        if res:
            return self._load(res)

    def find_by_task_id(self, task_id):
        results = db.query('SELECT * FROM cron WHERE task_id=%s', (task_id,))
        return [self._load(data) for data in results]

    def _load(self, data):
        if data[4] is not None:
            data = list(data)
            data[4] = json_decode(data[4])
        return Task(*data)

    def save(self, task):
        if task.data is not None:
            data = json_encode(task.data)
        else:
            data = None
        if task.cron_id is None:
            return db.execute('INSERT INTO cron(task_id, name, action, data, event, next_run, last_run, run_times, attempts, status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                              (task.task_id, task.name, task.action, data, task.event, task.next_run, task.last_run, task.run_times, task.attempts, task.status))

        return 	db.execute('INSERT INTO cron(task_id, name, action, data, event, next_run, last_run, run_times, attempts, status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
		 		ON DUPLICATE KEY UPDATE cron_id=VALUES(cron_id), task_id=VALUES(task_id), event=VALUES(event), next_run=VALUES(next_run), \
		 		last_run=VALUES(last_run), action=VALUES(action), data=VALUES(data),run_times=VALUES(run_times), attempts=VALUES(attempts), status=VALUES(status)',
                           (task.task_id, task.name, task.action, data, task.event, task.next_run, task.last_run, task.run_times, task.attempts, task.status))

    def delete(self, task):
        return db.execute('DELETE FROM cron WHERE cron_id=%s', (task.cron_id,))

    def delete_by_name(self, name):
        return db.execute('DELETE FROM cron WHERE name=%s', (name,))

    def delete_by_task_id(self, task_id):
        return db.execute('DELETE FROM cron WHERE task_id=%s', (task_id,))

__backends = {}
__backends['task'] = TaskMapper()


def Backend(name):
    return __backends.get(name)


if __name__ == '__main__':
    import logging
    debug = True
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

    db.setup('localhost', 'test', 'test', 'eden',
             pool_opt={'minconn': 3, 'maxconn': 10})
    task = Task(None, 'task_id', 'job_test', 'job.test',
                {'args': (), 'kw': {}}, 'every 5')
    task_mapper = Backend('task')
    task_mapper.delete_by_name('job_test')
    task_mapper.save(task)

    tasks = task_mapper.find_by_task_id('task_id')

    task = task_mapper.find('job_test')
    assert task.name == tasks[0].name

    task_ = task_mapper.find_by_cron_id(task.cron_id)
    assert task_.name == tasks[0].name

    task_find_by_name = task_mapper.find('job_test')
    assert task_find_by_name.name == tasks[0].name
