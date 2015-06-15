#!/usr/bin/python3

import queue

from traktor.aobject import AObject
from traktor.container import Done, LoopContainer


class OOO(AObject):

    @amethod
    def tryit(self, x):
        assert x == 1337

    @amethod
    def end(self):
        raise Done



def test_loop_function_call():
    obj = OOO()

    con = LoopContainer()
    obj.start(con)

    #obj.tryit(1337)
    #obj.tryit(1337)
    #obj.tryit(1337)
    #obj.end()
    obj.acall("tryit", 1337)
    obj.acall("tryit", 1337)
    obj.acall("tryit", 1337)
    obj.acall("end")

    wait = queue.Queue()
    con.spawn(wait)

    try:
        container, result = wait.get()
        raise result
    except Done:
        pass
    except:
        raise

    assert True

