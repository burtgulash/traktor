import functools


class AMeta(type):

    @staticmethod
    def amethod_decorator(amethods):
        def decorator(func):
            amethods[func.__name__] = func
            return func
        return decorator

    # Register 'handler_for' decorator and make it put all recognized handlers
    # to class attribute "process_handlers". Handlers will then be registered in
    # __init__ of each class when even overriden methods are known.
    def __prepare__(name, bases):
        amethods = {}

        # Reverse the bases so that the most overriden methods will be chosen
        # as an amethod
        for base in bases[::-1]:
            if hasattr(base, "_registered_amethods"):
                for name, func in base._registered_amethods.items():
                    amethods[name] = func

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

        self.name = "{} #{}".format(self.cls_name, self.__class__._ids)
        self.__class__._ids += 1

        self._methods = {}
        self._amethods = {}
        self.__container = None

        for method_name, func in self._registered_amethods.items():
            # Preferably get overriden method by name from instance
            method = getattr(self, method_name, None)

            # Method is private, turn function into method
            if not method:
                method = func.__get__(self, type(self))

            method = self._wrap(method)
            
            # Store 'old' synchronous method here
            self._methods[method_name] = method

            # Replace the synchronous method with wrapped asynchronous call
            self._amethods[method_name] = self.__make_async_wrapper(method)

    def _wrap(self, method):
        return method

    def __make_async_wrapper(self, method):
        @functools.wraps(method)
        def acall_wrap(*a, **k):
            self.__async_call(method, a, k)
        return acall_wrap

    def __async_call(self, method, a, k):
        item = (method, a, k)
        self._enqueue(item)

    def _process(self, item):
        method, a, k = item
        self.__container.invoke(method, *a, **k)

    def acall(self, method_name, *a, **k):
        """ acall is an asynchronous invocation of method with name
        'method_name'.
        """
        method = self.__get_method(method_name)
        self.__async_call(method, a, k)

    def __get_method(self, method_name):
        try:
            return self._methods[method_name]
        except KeyError:
            raise AttributeError("AObject '{}' doesn't have amethod '{}'!".
                    format(self.__class__.__name__, method_name))


    def start(self, container):
        self.__container = container
        self.activate()

    def stop(self):
        self.deactivate()
        self.__container = None

    def get_container(self):
        return self.__container

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

    def __repr__(self):
        return "{" + self.name + "}"


