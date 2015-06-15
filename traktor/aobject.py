import functools


class AMeta(type):

    @staticmethod
    def amethod_decorator(amethods):
        def decorator(func):
            amethods.append(func)
            return func
        return decorator

    # Register 'handler_for' decorator and make it put all recognized handlers
    # to class attribute "process_handlers". Handlers will then be registered in
    # __init__ of each class when even overriden methods are known.
    def __prepare__(name, bases):
        amethods = []

        for base in bases:
            if hasattr(base, "_registered_amethods"):
                for name, func in base._registered_amethods:
                    amethods.append(func)

        amethod = AMeta.amethod_decorator(amethods)

        return {"_registered_amethods": amethods,
                "amethod": amethod,
                "cls_name": name,
                "_ids": 0}


class Enablable:

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
    """ AObject stands for asynchronous object. It is a normal object, but has
    a decorator @amethod which can turn its method into asynchronous method.
    """

    def __init__(self):
        super().__init__()

        self._amethods = {}
        self.__container = None

        for func in self._registered_amethods:
            # Preferably get overriden method by name from instance
            method_name = func.__name__
            method = getattr(self, method_name, None)

            # Method is private, turn function into method
            if not method:
                method = func.__get__(self, type(self))

            # Python closures are lexically scoped. Create a scope around
            # 'method_name' so that it does not confuses method_name within the
            # for loop scope
            def make_wrapper(method_name):
                @functools.wraps(method)
                def amethod_wrap(*a, **k):
                    self.acall(method_name, *a, **k)
                return amethod_wrap

            self._amethods[method_name] = make_wrapper(method_name)

    def acall(self, method_name, *a, **k):
        """ acall is an asynchronous invocation of method with name
        'method_name'.
        """
        method = super().__getattribute__(method_name)
        item = (method, a, k)
        self._enqueue(item)

    def _process(self, item):
        method, a, k = item
        self.__container.invoke(method, *a, **k)

    def start(self, container):
        self.__container = container
        self.activate()

    def stop(self):
        self.deactivate()
        self.__container = None

    def __getattribute__(self, attr):
        """ Override default attribute getter so that getting methods
        registered with decorator @amethod will return wrapper which calls the
        method asynchronously - ie. enqueues the function to container's queue.
        """
        try:
            amethods = super().__getattribute__("_amethods")
        except AttributeError:
            return super().__getattribute__(attr)

        if attr in amethods:
            return amethods[attr]
        else:
            return super().__getattribute__(attr)


