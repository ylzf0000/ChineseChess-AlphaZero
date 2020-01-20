# coding=utf-8
import os
import sys
import agent
from PyQt5.QtWidgets import QApplication, QMainWindow
from mainwindow import *

sys.setrecursionlimit(1000000)
os.environ["CUDA_VISIBLE_DEVICES"] = "2,3"
if __name__ == '__main__':
    agent.train()
    # app = QApplication(sys.argv)
    # mainWindow = MainWindow()
    # mainWindow.show()
    # sys.exit(app.exec_())
