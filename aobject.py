import functools


class AMeta(type):

    @staticmethod
    def amethod_decorator(amethods):
        def bake_in(amethod_name):
            def decorator(func):
                amethods.append((amethod_name, func))
                return amethod
            return decorator
        return bake_in

    # Register 'handler_for' decorator and make it put all recognized handlers
    # to class attribute "process_handlers". Handlers will then be registered in
    # __init__ of each class when even overriden methods are known.
    def __prepare__(name, bases):
        amethods = []

        for base in bases:
            if hasattr(base, "_registered_amethods"):
                for name, func in base._registered_amethods:
                    amethods.append((name, func))

        decorator = AMeta.amethod_decorator(amethods)

        return {"_registered_amethods": amethods,
                "amethod": decorator,
                "cls_name": name,
                "_ids": 0}


class Enablable(object):

    def __init__(self):
        self.__active = False
        self.__waiting = []

    def __process_waiting(self):
        for message in self.__waiting:
            self._process(message)
        self.__waiting = []

    def _process(self, message):
        pass

    def _enqueue(self, message):
        self.__waiting.append(message)
        if self.__active:
            self.__process_waiting()

    def is_active(self):
        return self.__active

    def activate(self):
        self.__active = True
        self.__process_waiting()

    def _flush(self):
        self.__waiting = []

    def deactivate(self):
        self.__active = False



class AObject(Enablable, metaclass=AMeta):

    def __init__(self):
        super().__init__()
        self.__amethods = {}
        self.__container = None

        for amethod_name, func in self._registered_amethods:
            # Preferably get overriden method by name from instance
            method = getattr(self, method.__name__, None)

            # Method is private, turn function into method
            if not method:
                method = func.__get__(self, type(self))

            @functools.wraps(method)
            def amethod(self, *a, **k):
                self.acall(method, *k, **k)

            self.__amethods[method.__name__] = amethod

    def acall(self, method, *a, **k):
        item = (method, a, k)
        self._queue(item)

    def _process(self, item):
        method, a, k = item
        self.__container.invoke(method, *a, **k)

    def __getattribute__(self, attr):
        if attr in self.__amethods:
            return self.__amethods[attr]
        else:
            return super().__getattribute__(attr)

    def start(self, container):
        self.__container = container
        self.activate()

    def stop(self):
        self.deactivate()
        self.__container = None


