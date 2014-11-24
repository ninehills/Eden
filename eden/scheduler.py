import logging
import time
import threading
import sys
import Queue
import uuid
from eden.data import Backend
try:
    from thread import get_ident
except ImportError:
    from _thread import get_ident

LOGGER = logging.getLogger(__name__)

_SHUTDOWNTASK = object()



class Scheduler(object):

    # the total for worker thread to cleanly exit
    SHOTDOWN_TIMEOUT = 5

    def __init__(self, app, task_size=10, minthreads=10, maxthreads=50):
        minthreads = minthreads or 1
        minthreads = 1 if minthreads <=0 else minthreads
        maxthreds = maxthreds or 500
        maxthreds = 500 if maxthreds > 500 else maxthreds
        if maxthreds <= minthreads:
            raise TypeError('maxthreds:%d must greater than minthreads:%d', maxthreds, minthreads)

        self.app = app
        self.ready = False 
        self.task_size = task_size or ((maxthreds - minthreads) / 2)
        self._idel_tasks = Queue.Queue()
        self.threadpool = ThreadPool(self, minthreads, maxthreds)
        self.heartbeat = HeartBeat(self, self._periodic_action, 5)

    def _periodic_action(self):
        idel_queue_size = self._idel_tasks.size()
        for _ in range(idel_queue_size):
            task = self.get()
            self.execute(task, True)

    get = lambda self: self._idel_tasks.get()

    put = lambda self, task: self._idel_tasks.put(task)

    def run(self):
        LOGGER.debug('Starting schedule ....')
        LOGGER.debug('master thread : %d', get_ident())
        self.ready = True
        self.threadpool.start()
        self.heartbeat.start()
        
        while self.ready:
            try:
                tasks = self.claim()
                if not tasks:
                    time.sleep(5)
                    continue

                for task in tasks:
                    LOGGER.debug('current_task: %s', task)
                    self.execute(task)
           
            except Exception as e:
                LOGGER.error('Internal Error: %s', e)

        LOGGER.debug('Stop schedule...')
        self.stop()

    def stop(self):
        self.heartbeat.stop()
        self.threadpool.stop(self.SHOTDOWN_TIMEOUT)

    def execute(self, task, retry=False):
        try:
            done = False
            thread = self.threadpool.pop()
            if thread:
                LOGGER.debug('execute in thread: %s', self.thread)
                thread.current_task = task
                self.thread.resume()
                done = True
            elif not retry:
                self.put(task)
        except (KeyboardInterrupt, SystemExit):
                self.ready = False
                if not done and thread:
                    thread.current_task = _SHUTDOWNTASK
                    thread.resume()
        except Exception as e:
            LOGGER.error('Error : %s', e)
            raise

    def claim(self):
        return [{'action': 'user.add', 'args': ('xx', ), 'kw': dict()}] * 5

    def gen_task_id(self):
        return str(uuid.uuid4())

    @classmethod
    def add_task(cls, name, event, action, *args, **kw):
        data = {'args': args, 'kw': kw}
        task = Task(None, None, name, event, action, data)
        return Backend('task').save(job)

    @classmethod
    def stop_task(cls, name):
        task = Backend('task').find(name)
        if job and job.status != Task.RUNNING:
            task.status = Task.STOP
            Backend('task').save(task)
            return True
        return False

    def delete_task(cls, name):
        task = Backend('task').find(name)
        if job and job.status != Task.RUNNING:
            Backend('task').delete(task)
            return True
        return False

class HeartBeat(threading.Thread)

    def __init__(self, interval=5, callback):
        self.callback = callback
        self.interval = interval
        self.ready = False
        threading.Thread.__init__(self)

    def run(self):
        self.ready = True
        while self.ready:
            time.sleep(self.interval)
            self.callback()

    def stop(self):
        self.ready = False
        if self.isAlive():
            self.join()
            
class ThreadPool(object):

    def __init__(self, schedule, min, max):
        self.schedule = schedule
        self.min = min
        self.max = max
        self._created = 0
        self._lock = threading.Lock()
        self._in_use_threads = {}
        self._idle_threads = []

    def start(self):
        for i in range(self.min):
            with self._lock:
                self._created += 1
                thread = self._new_thread()
                self._idle_threads.append(thread)

    def push(self, thread):
        with self._lock:
            if thread in self._in_use_threads:
                del self._in_use_threads[thread]
            self._idle_threads.append(thread)

    def pop(self):
        """Non-block pop an idle thread, if not get returns None"""
        thread = None
        self._lock.acquire()
        if self._idle_threads:
            thread = self._idle_threads.pop(0)
            self._in_use_threads[thread] = True
        else:
            if self._created < self.max:
                self._created += 1
                thread = self._new_thread()
                self._in_use_threads[thread] = True
        self._lock.release()
        return thread

    def _new_thread(self):
        return WorkerThread(self.schedule, self)

    def stop(self, timeout=5):
        # Must shut down threads here so the code that calls
        # this method can know when all threads are stopped.

        #time.sleep(1)
        endtime = int(time.time() + timeout)
        while True:
            time.sleep(1)
            with self._lock:
                if self._in_use_threads or self._idle_threads:
                    LOGGER.info('_idle_threads')
                    while self._idle_threads:
                        worker = self._idle_threads.pop(0)
                        worker.current_task = _SHUTDOWNtask
                        worker.resume()
                        #worker.event.clear()
                else: 
                    break


class WorkerThread(threading.Thread):

    def __init__(self, schedule, pool):
        self.ready = False
        self.event = threading.Event()
        self.schedule = schedule
        self.current_task = None
        self.pool = pool
        threading.Thread.__init__(self)
        self.start()

    def suspend(self):
        self.event.clear()
        self.event.wait()

    def resume(self):
        self.event.set()

    def run(self):
        self.ready = True
        LOGGER.debug('Starting thread %d', get_ident())
        while self.ready:
            self.suspend()
            if self.current_task == _SHUTDOWNTASK:
                # shutdown the worker thread
                self.ready = False
                break
            try:
                if self.current_task:
                    self.schedule.app(**self.current_task)
            finally:
                self.current_task = None
                self.pool.push(self)
        self.event.clear()


def app(action, args, kw):
    LOGGER.info('app ....')
    LOGGER.debug('action is : %s', action)


def setdebug(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')


setdebug(True)

scheduler= Scheduler(app, 1, 10)
scheduler.run()