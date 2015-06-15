import collections
import queue
import threading


class SkipQueue(queue.Queue):
    """ Implementation of blocking queue which can queue urgent items to the
    beginning of the queue instead of at the end.
    """

    def __init__(self):
        super().__init__()
        self.queue = collections.deque()

    def enqueue(self, x, urgent=False):
        item = x, urgent
        self.put(item)

    def dequeue(self, block=True, timeout=None):
        return self.get(block, timeout)

    def _put(self, item):
        x, urgent = item
        if urgent:
            self.queue.appendleft(x)
        else:
            self.queue.append(x)


class Done(Exception): pass

class Container:

    def __init__(self):
        self._queue = self._make_queue()
        self.__thread = None

    def _make_queue(self):
        return SkipQueue()

    def start(self):
        self._react()

    def stop(self):
        # Can't stop this!
        pass

    def spawn(self, wait):
        self.__thread = threading.Thread(target=self._synchronized_start, args=[wait])
        self.__thread.start()

    def join(self):
        self.__thread.join()

    def _synchronized_start(self, wait):
        result = None

        try:
            self.start()
        except Exception as err:
            result = err
        else:
            result = Done

        wait.put((self, result))

    def invoke(self, function, *a, **k):
        event = function, a, k
        self._queue.enqueue(event)

    def _react(self):
        event = self._queue.dequeue()
        function, a, k = event
        function(*a, **k)


class LoopContainer(Container):

    def __init__(self):
        super().__init__()
        self.__running = False

    def stop(self):
        self.__running = False

        # Flush the queue with empty event
        self.invoke(lambda: None)

    def _react(self):
        self.__running = True
        while self.__running:
            super()._react()

