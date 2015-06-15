import collections
import heapq
import queue
import threading
import time


class SkipQueue(queue.Queue):
    """ Implementation of blocking queue which can queue urgent items to the
    beginning of the queue instead of at the end.
    """

    def __init__(self):
        super().__init__()
        self.queue = collections.deque()

    def enqueue(self, x, skip=False):
        item = x, skip
        self.put(item)

    def dequeue(self, block=True, timeout=None):
        return self.get(block, timeout)

    def _put(self, item):
        x, skip = item
        if skip:
            self.queue.appendleft(x)
        else:
            self.queue.append(x)


class TimedQueue(SkipQueue):

    def __init__(self):
        super().__init__()
        self.delayed = []
        self._WAIT = .1

    def enqueue(self, x, delay=0):
        deadline = time.time() + delay
        super().enqueue((deadline, delay, x), skip=delay > 0)

    def dequeue(self, block=True, timeout=None):
        while True:
            now = time.time()
            timeout = self._WAIT

            if self.delayed:
                nearest = self.delayed[0]
                timeout = max(0, nearest[0] - now)

            try:
                deadline, delay, x = super().dequeue(block=block, timeout=timeout)
            except queue.Empty:
                if not block:
                    raise
            else:
                if delay > 0:
                    heapq.heappush(self.delayed, (deadline, x))
                else:
                    return x

            delayed = []
            while self.delayed and self.delayed[0][0] <= now:
                delay, x = heapq.heappop(self.delayed)
                delayed.append(x)
            while delayed:
                x = delayed.pop()
                super().enqueue((0, 0, x))


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
        event = self._make_event(function, *a, **k)
        self._queue.enqueue(event)

    def _make_event(self, function, *a, **k):
        return function, a, k

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


class TimerContainer(LoopContainer):

    def _make_queue(self):
        return TimedQueue()

    def invoke(self, function, *a, _delay=0, **k):
        if "_delay" in k:
            del k["_delay"]

        if _delay >= 0:
            event = self._make_event(function, *a, **k)
            self._queue.enqueue(event, delay=_delay)
        else:
            raise ValueError("'delay' must be a non-negative number!")

