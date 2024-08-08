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
    imgPath = "plugins/CoordConverter/testImages/NC1.png"
    maskPath = "plugins/CoordConverter/masks/NCM.png"

    aff = Affine()
    vis = Visualize(aff)
    img = cv.imread(imgPath, cv.IMREAD_GRAYSCALE)
    mask = cv.imread(maskPath, cv.IMREAD_GRAYSCALE)
    if aff.try_match(imgPath, maskPath):
        vis.queue_affine()
        vis.show()
    else: 
