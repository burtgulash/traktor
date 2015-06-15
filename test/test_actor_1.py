#!/usr/bin/python3

import queue

from traktor.aktor import Supervisor, Supervised
from traktor.aobject import AObject
from traktor.container import Done, LoopContainer, TimerContainer


class A(Supervisor):

    @amethod
    def on_error(self, error):
        assert isinstance(error, Exception)
        raise Done

class B(Supervised):

    @amethod
    def fail(self):
        raise Exception("Zasrata Blbost")



def test_loop_function_call():
    a = A()
    b = B()
    con = LoopContainer()

    a.spawn(b)
    a.start(con)

    b.fail()

    wait = queue.Queue()
    con.spawn(wait)

    try:
        container, result = wait.get()
        raise result
    except Done:
        pass

    assert True
