import cv2
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import patches

import pyHook, pythoncom

import pyautogui

import sys

from PyQt5 import QtGui, QtCore, uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication

from threading import Timer

########################################################################################################################

class MainWindow(QMainWindow):
    def __init__(self, x, y):
        QMainWindow.__init__(self)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setGeometry(x + 60,y + 60,50,50)

    def mousePressEvent(self, event):
        QtWidgets.qApp.quit()

app = QApplication(sys.argv)

windows = [None] * 4

for i in range(4):
    windows[i] = MainWindow(0,0)

def clearWindows():
    for i in range(4):
        windows[i].close()

########################################################################################################################

class Finerprint:
    def __init__(self):
        self.fingerImg = []
        self.fingerSol = [None] * 4

#Initialize the four fingerprints
fingerprints = [None] * 4
for i in range(4):
    fingerprints[i] = Finerprint()
    fingerprints[i].fingersol = []

for i in range(4):
    #make them binary so that it doesn't matter if it's selected
    fingerprints[i].fingerImg = cv2.resize(cv2.imread(f"C:\\Users\\hazem\\Desktop\\GTA\\Finger{i+1}\\F{i+1}.jpg",cv2.IMREAD_GRAYSCALE),(320,550))
    for j in range(4):
        fingerprints[i].fingerSol[j] = cv2.resize(cv2.imread(f"C:\\Users\\hazem\\Desktop\\GTA\\Finger{i+1}\\F{i+1}S{j+1}.jpg",cv2.IMREAD_GRAYSCALE),(127,127))

def takeScreenshot():
    screenshot = cv2.resize(cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_BGR2GRAY),(1920,1080))
    FPtoSolve =  screenshot[150:680 , 980:1300]
    return FPtoSolve, screenshot

def solveScreenshot(FPtoSolve, screenshot, fingerprints):
    bestMatch = [None] * 4

    for i in range(4):
        surf = cv2.xfeatures2d.SURF_create()
        kp1, des1 = surf.detectAndCompute(FPtoSolve, None)
        kp2, des2 = surf.detectAndCompute(fingerprints[i].fingerImg, None)

        bf = cv2.BFMatcher(cv2.NORM_L2,crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        bestMatch[i] = len(matches)

    if max(bestMatch) < 400:
        return

    correctFingerIndex = bestMatch.index(max(bestMatch))

    for i in range(4):
        method = cv2.TM_SQDIFF_NORMED
        result = cv2.matchTemplate(fingerprints[correctFingerIndex].fingerSol[i], screenshot, method)

        mn,_,mnLoc,_ = cv2.minMaxLoc(result)
        MPx,MPy = mnLoc

        windows[i] = MainWindow(MPx, MPy)
        windows[i].show()

    t = Timer(2, clearWindows)
    t.start()

def OnKeyboardEvent(event):
    if event.KeyID == 191:
        clearWindows()
        solveScreenshot(takeScreenshot()[0],takeScreenshot()[1], fingerprints)

    return True

########################################################################################################################

hm = pyHook.HookManager()
hm.KeyDown = OnKeyboardEvent
hm.HookKeyboard()
pythoncom.PumpMessages()