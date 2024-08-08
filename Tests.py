

class Tester:

    def __init__(self):
        self.secret_Var = "Secret"

    def function1(self, arg1):
        return arg1 + "from function1"

    def function2(self, arg1):
        return arg1 + "from function2" + self.secret_Var

    def give_out_function1(self):
        return self.function1

    def give_out_function2(self):
        return self.function2


if __name__ == "__main__":
    test = Tester()
    func1 = test.give_out_function1()
    func2 = test.give_out_function2()
    print(func1("Hello "))
    print(func2("Hello "))
    
