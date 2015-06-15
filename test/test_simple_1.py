#!/usr/bin/python3

from traktor.aobject import AObject
from traktor.container import Container


class OOO(AObject):

    @amethod
    def function(self, x):
        assert x == 1337


if __name__ == "__main__":
    obj = OOO()

    con = Container()
    obj.start(con)

    obj.function(1337)
    con.start()

