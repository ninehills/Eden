import logging
import time
import threading
import sys

try:
    from thread import get_ident
except ImportError:
    from _thread import get_ident

LOGGER = logging.getLogger(__name__)

_SHUTDOWNJOB = object()


class Schedule(object):

    # the total for worker thread to cleanly exit
    SHOTDOWN_TIMEOUT = 5

    def __init__(self, app, min, max):
        self.app = app
        self.ready = False
        self.threadpool = ThreadPool(self, min, max)
        self.done = None
        self.thread = None

    def run(self):
        LOGGER.debug('Starting schedule ....')
        LOGGER.debug('master thread : %d', get_ident())
        self.ready = True
        # self.threadpool.start()
        
        while self.ready:
            try:
                jobs = self.claim()
                if not jobs:
                    time.sleep(5)

                for job in jobs:
                    LOGGER.debug('current_job: %s', job)
                    self.execute(job)
                #time.sleep(5)
           
            except Exception as e:
                LOGGER.error('Internal Error: %s', e)

        LOGGER.debug('Stop schedule...')
        self.stop()

    def stop(self):
        self.threadpool.stop(self.SHOTDOWN_TIMEOUT)

    def execute(self, job):
        try:
            self.done = False
            self.thread = self.threadpool.pop()
            if self.thread:
                LOGGER.debug('execute in thread: %s', self.thread)
                self.thread.current_job = job
                self.thread.resume()
                self.done = True
                self.thread = None
        except (KeyboardInterrupt, SystemExit):
                self.ready = False
                if not self.done and self.thread:
                    self.thread.current_job = _SHUTDOWNJOB
                    self.thread.resume()
        except Exception as e:
            LOGGER.error('Error : %s', e)
            raise

    def claim(self):
        return [{'action': 'user.add', 'args': ('xx', ), 'kw': dict()}] * 5


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
        thread = None
        first_tried = time.time()
        while True:
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

            if not thread and 3 <= (time.time() - first_tried):
                raise ThreadPoolError("tried 3 sethreadds, can't load thread, maybe too many jobs")

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
                        worker.current_job = _SHUTDOWNJOB
                        worker.resume()
                        #worker.event.clear()
                else: 
                    break

class ThreadPoolError(Exception):
    pass


class WorkerThread(threading.Thread):

    def __init__(self, schedule, pool):
        self.ready = False
        self.event = threading.Event()
        self.schedule = schedule
        self.current_job = None
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
            if self.current_job == _SHUTDOWNJOB:
                # shutdown the worker thread
                self.ready = False
                break
            self.suspend()
            try:
                if self.current_job:
                    self.schedule.app(**self.current_job)
            finally:
                self.current_job = None
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

schedule = Schedule(app, 1, 10)
schedule.run()