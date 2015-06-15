#!/usr/bin/python3

import queue

from traktor.aobject import AObject
from traktor.container import Done, LoopContainer, TimerContainer


class OOO(AObject):

    @amethod
    def tryit(self, x):
        assert x == 1337

    @amethod
    def finish(self):
        raise Done



def test_loop_function_call():
    obj = OOO()

    con = LoopContainer()
    obj.start(con)

    obj.tryit(1337)
    obj.acall("tryit", 1337)
    obj.tryit(1337)
    obj.finish()


    wait = queue.Queue()
    con.spawn(wait)

    try:
        container, result = wait.get()
        raise result
    except Done:
        pass

    assert True


def test_timer_function_call():
    obj = OOO()

    con = TimerContainer()
    obj.start(con)

    obj.tryit(1337)
    obj.tryit(1337)
    obj.finish(_delay=.005)

    wait = queue.Queue()
    con.spawn(wait)

    try:
        container, result = wait.get()
        raise result
    except Done:
        pass

    assert True

