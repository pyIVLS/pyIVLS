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


from plugins.CoordConverter.affine import Affine, Visualize
import cv2 as cv

if __name__ == "__main__":
    move_speeds = {
        15: 1300,
        14: 1218.75,
        13: 1137.5,
        12: 1056.25,
        11: 975,
        10: 893.75,
        9: 812.5,
        8: 731.25,
        7: 650,
        6: 568.75,
        5: 487.5,
        4: 406.25,
        3: 325,
        2: 243.75,
        1: 162.5,
        0: 81.25,
    }

    def _calculate_wait_time(speed, x, y, z):
        curr_pos = (0, 0, 0)
        x_diff = abs(curr_pos[0] - x)
        y_diff = abs(curr_pos[1] - y)
        z_diff = abs(curr_pos[2] - z)

        total_diff = x_diff + y_diff + z_diff
        time = total_diff / move_speeds[speed]
        return time

    print(_calculate_wait_time(1, 2500, 2500, 2500))
