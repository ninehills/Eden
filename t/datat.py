from eden import db
from eden.model import Task
from eden.data import Backend


import unittest


class TaskMapperTest(unittest.TestCase):

    def setUp(self):
        setattr(db, '__connections', {})
        db.setup('localhost', 'test', 'test', 'eden',
                 pool_opt={'minconn': 3, 'maxconn': 10})
        self.task = Task(
            None, 'task_id', 'job_test', 'job.test', {'args': (), 'kw': {}}, 'every 5')
        Backend('task').delete_by_name('job_test')
        Backend('task').save(self.task)

    def test_find(self):
        task = Backend('task').find('job_test')
        assert task.name == self.task.name
        assert task.status == self.task.status
        assert task.event == self.task.event
        assert task.attempts == self.task.attempts

        task = Backend('task').find_by_task_id('task_id')[0]
        assert task.name == self.task.name
        assert task.status == self.task.status
        assert task.event == self.task.event
        assert task.attempts == self.task.attempts

        task = Backend('task').find_by_cron_id(task.cron_id)
        assert task.name == self.task.name
        assert task.status == self.task.status
        assert task.event == self.task.event
        assert task.attempts == self.task.attempts

    def test_save(self):
        task = Backend('task').find('job_test') 
        task.fresh()
        task.attempts += 1
        task.status = Task.COMPLETED
        Backend('task').save(task)
        task = Backend('task').find('job_test')
        assert task.name == self.task.name
        assert task.event == self.task.event
        assert task.run_times == 1
        assert task.attempts == self.task.attempts + 1
        assert task.status == Task.COMPLETED

    def test_delete(self):
        task = Backend('task').find('job_test')
        ret = Backend('task').delete(task)
        task = Backend('task').find('job_test')
        self.assertEqual(task, None)

    def test_delete_by_name(self):
        task = Backend('task').find('job_test')
        ret = Backend('task').delete_by_name(task.name)
        task = Backend('task').find('job_test')
        self.assertEqual(task, None)

    def test_delete_by_task_id(self):
        task = Backend('task').find('job_test')
        ret = Backend('task').delete_by_task_id(task.task_id)
        task = Backend('task').find('job_test')
        self.assertEqual(task, None)


if __name__ == '__main__':

    unittest.main()
