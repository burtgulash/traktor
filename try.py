#!/usr/bin/python3

from aobject import AObject
from container import Container


class A(AObject):

    def __init__(self, x):
        super().__init__()
        self.x = x

    @amethod
    def print_it(self):
        print(self.x)


if __name__ == "__main__":
    obj = A(1337)

    con = Container()
    obj.start(con)

    obj.print_it()
    con.start()

