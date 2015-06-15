import functools
from traktor.aobject import AObject


class Supervised(AObject):

    def __init__(self):
        super().__init__()
        self.__supervisor = None

    def set_supervisor(self, supervisor):
        self.__supervisor = supervisor

    def get_supervisor(self):
        return self.__supervisor

    def _wrap(self, method):
        @functools.wraps(method)
        def catched_wrap(*a, **k):
            try:
                method(*a, **k)
            except Exception as err:
                self.get_supervisor().acall("on_error", err)
        return super()._wrap(catched_wrap)


class Supervisor(AObject):

    def __init__(self):
        super().__init__()
        self.__supervised = set()

    def get_kids(self):
        return iter(self.__supervised)

    def spawn(self, actor):
        self.__supervised.add(actor)
        actor.set_supervisor(self)
        actor.start(self.get_container())

    def start(self, container):
        super().start(container)
        for kid in self.get_kids():
            kid.start(container)

    @amethod
    def on_error(self, error):
        raise error



class Aktor(Supervised, Supervisor, AObject):

    pass
