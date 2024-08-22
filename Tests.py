from pyftdi.ftdi import Ftdi
import pyftdi.serialext
import pluggy
import inspect


class tester:

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    @hookimpl
    def imma_hook(self):
        print("Hookin'")

    def get_a_load(self):
        print("griftin'")

    def of_this_guy(self):
        print("griftin' people")


if __name__ == "__main__":
    t = tester()

    methods_list = [
        method[0] for method in inspect.getmembers(t, predicate=inspect.ismethod)
    ]

    print(methods_list)
