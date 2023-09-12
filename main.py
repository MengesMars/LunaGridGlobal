from tkinter import *
import tkinter as tk
import numpy as np
import cv2 as cv
import math

im = cv.imread('Moon_LRO_LROC-WAC_Mosaic_global_1024.jpg')
height, width = im.shape[0:2]

newminlon = 0
newmaxlon = 360
newlonrange = newmaxlon-newminlon
newminlat = -90
newmaxlat = 90
newlatrange = newmaxlat-newminlat

while True:
    try:
        RECT_WIDTH_KM = input("Grid Cell Width (km): ")  # Site rectangle width in km.
        RECT_WIDTH_KM = float(RECT_WIDTH_KM)
        break
    except ValueError:
        print("Error: Enter valid float value: ")
while True:
    try:
        RECT_HT_KM = input("Grid Cell Height (km): ")  # Site rectangle height in km.
        RECT_HT_KM = float(RECT_HT_KM)
        break
    except ValueError:
        print("Error: Enter valid float value: ")

a = 1738.1 #eq radius km
b = 1736.0 #pol radius km
IMG_WIDTH_EXTENT=2*a*math.pi*(newlonrange/360)
IMG_HEIGHT_EXTENT=2*b*math.pi*(newlatrange/360)
LAT_0 = round((newmaxlat)*(height/newlatrange))
midlat = (newminlat+newmaxlat)/2
LAT_MID = round((newmaxlat-midlat)*(height/newlatrange))
NUM_CANDIDATES = 50

RECT_HT=height/(IMG_HEIGHT_EXTENT/RECT_HT_KM)
rect_ht_deg = RECT_HT_KM/(IMG_HEIGHT_EXTENT/newlatrange)
rect_pix = round((height/newlatrange)*rect_ht_deg)
rect_ht_deg2 = (rect_pix/(height/newlatrange))
MAX_LAT = newlatrange
LAT = newminlat
pixlat = height
while LAT<MAX_LAT:
    LAT+=rect_ht_deg2
    pixlat-=rect_pix
MAX_LAT=LAT-rect_ht_deg2
pixlat = int(pixlat+rect_pix)


ul_y = pixlat
lat_conv_top = newmaxlat-pixlat*(newlatrange/height)
lat_conv_bottom = newmaxlat-((ul_y+rect_pix)*(newlatrange/height))
lat_rad_top = np.deg2rad(lat_conv_top)
lat_rad_bottom = np.deg2rad(lat_conv_bottom)
#Knowing the geodetic latitude, ϕ, we can calculate the reduced latitude, μ, using: tan(μ)=(b/a)tan(ϕ)
mu_top = math.atan((b/a)*math.tan(lat_rad_top))
mu_bottom = math.atan((b/a)*math.tan(lat_rad_bottom))
#The radius of the small circle, x, at the latitude ϕ can then be calculated using: x=a*cos(μ)
x_top = a*math.cos(mu_top)
x_bottom = a*math.cos(mu_bottom)
#The circumference, C, of the small circle at the latitude ϕ is given by: C=2πx
C_top = 2*x_top*math.pi/(360/newlonrange)
C_bottom = 2*x_bottom*math.pi/(360/newlonrange)
numblocks = round(C_bottom/RECT_WIDTH_KM)
STEP_X = round(width/numblocks)

# Create tkinter screen and drawing canvas
screen = tk.Tk()
canvas = tk.Canvas(screen, width=1022, height=512 + 130)


class Search():
    """Read image and identify landing rectangles based on input criteria."""

    def __init__(self, name):
        self.name = name
        self.rect_coords = {}

    def run_rect_stats(self):
        """Define rectangular search areas and calculate internal stats."""
        ul_y = pixlat
        STEP_Y = rect_pix

        lat_conv = newmaxlat - ((ul_y + rect_pix) * (newlatrange / height))
        lat_rad = np.deg2rad(lat_conv)
        mu = math.atan((b / a) * math.tan(lat_rad))
        x = a * math.cos(mu)
        C = 2 * x * math.pi / (360 / newlonrange)
        numblocks = math.ceil(C / RECT_WIDTH_KM)
        STEP_X = math.floor(width / numblocks)
        ul_x = int((width - (numblocks * STEP_X)) / 2)

        lr_x, lr_y = ul_x + STEP_X, pixlat + STEP_Y
        rect_num = 1
        #print(ul_x, ul_y, lr_x, lr_y)
        row = 1

        while True:
            #rect_img = im[ul_y: lr_y, ul_x: lr_x]
            self.rect_coords[rect_num] = [ul_x, ul_y, lr_x, lr_y]
            # print('row', row, 'rect', rect_num)
            rect_num += 1

            # Move the rectangle.
            # print('row', row)
            ul_x += STEP_X
            lr_x = ul_x + STEP_X
            if lr_x > width:
                row += 1
                ul_y += STEP_Y
                lr_y += STEP_Y
                if lr_y < LAT_0:
                    lat_conv = newmaxlat - ((ul_y + rect_pix) * (newlatrange / height))
                    lat_rad = np.deg2rad(lat_conv)
                    mu = math.atan((b / a) * math.tan(lat_rad))
                    x = a * math.cos(mu)
                    C = 2 * x * math.pi / (360 / newlonrange)
                    numblocks = math.ceil(C / RECT_WIDTH_KM)
                    # print('numblocks', numblocks)
                    STEP_X = math.floor(width / numblocks)
                    total_rect_width = STEP_X * numblocks
                    ul_x = (width - total_rect_width) // 2
                    while ul_x > STEP_X:
                        numblocks += 1
                        STEP_X = width // numblocks
                        ul_x = (width - (STEP_X * numblocks)) // 2
                    lr_x = ul_x + STEP_X
                else:
                    lat_conv = newmaxlat - ((ul_y) * (newlatrange / height))
                    lat_rad = np.deg2rad(lat_conv)
                    mu = math.atan((b / a) * math.tan(lat_rad))
                    x = a * math.cos(mu)
                    C = 2 * x * math.pi / (360 / newlonrange)
                    numblocks = math.ceil(C / RECT_WIDTH_KM)
                    # print('numblocks', numblocks)
                    STEP_X = math.floor(width / numblocks)
                    total_rect_width = STEP_X * numblocks
                    ul_x = (width - total_rect_width) // 2
                    while ul_x > STEP_X:
                        numblocks += 1
                        STEP_X = width // numblocks
                        ul_x = (width - (STEP_X * numblocks)) // 2
                    lr_x = ul_x + STEP_X

            if lr_y > height - pixlat:
                break

    def draw_qc_rects(self):
        """Draw overlapping search rectangles on image as a check."""
        img_copy = im.copy()
        rects_sorted = sorted(self.rect_coords.items(), key=lambda x: x[0])
        # print("\nRect Number and Corner Coordinates (ul_x, ul_y, lr_x, lr_y):")
        for k, v in rects_sorted:
            # print("rect: {}, coords: {}".format(k, v))
            cv.rectangle(img_copy,
                         (self.rect_coords[k][0], self.rect_coords[k][1]),
                         (self.rect_coords[k][2], self.rect_coords[k][3]),
                         (0, 0, 255), 1)
            '''cv.putText(img_copy, str(k),
                       (self.rect_coords[k][0] + 2, self.rect_coords[k][1] + 12),
                       cv.FONT_HERSHEY_PLAIN, .35, (255, 0, 0), 1)'''
        cv.putText(img_copy, 'EQUATOR', (1, LAT_0 - 5),
                   cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv.line(img_copy, (0, LAT_0), (width, LAT_0),
                (255, 255, 255), 1)
        cv.imshow('QC Rects {}'.format(self.name), img_copy)
        cv.waitKey(0)
        cv.destroyAllWindows()
        #plt.figure(figsize=(12, 8))
        #plt.imshow(img_copy)
        #plt.title('QC Rects {}'.format(self.name))
        #plt.show()

def main():
    app = Search('_')
    app.run_rect_stats()
    app.draw_qc_rects()
    # app.sort_stats()


if __name__ == '__main__':
    main()