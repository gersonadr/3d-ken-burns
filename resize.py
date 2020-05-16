import cv2
import sys

npyImage = cv2.imread(filename=sys.argv[1], flags=cv2.IMREAD_COLOR)

intWidth = npyImage.shape[1]
intHeight = npyImage.shape[0]

fltRatio = float(intWidth) / float(intHeight)

intWidth = min(int(1024 * fltRatio), 1024)
intHeight = min(int(1024 / fltRatio), 1024)

npyImage = cv2.resize(src=npyImage, dsize=(intWidth, intHeight), fx=0.0, fy=0.0, interpolation=cv2.INTER_AREA)

cv2.imwrite(sys.argv[1], npyImage)