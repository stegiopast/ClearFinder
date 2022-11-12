from decimal import ROUND_FLOOR
from fileinput import filename
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget, QLineEdit, QDialog
from PyQt5.QtWidgets import QGridLayout, QTabWidget, QComboBox, QCheckBox, QHBoxLayout, QListWidget, QTableWidget, QFileDialog
from PyQt5.QtCore import Qt

import os
import pathlib
import re
import string
import sys
import random

from pyparsing import empty

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats

from ClearMap.Environment import *
import numpy.lib.recfunctions as rfn
import napari

from dask_image.imread import imread
from multiprocessing import Process

from sklearn.datasets import make_blobs
from sklearn import decomposition

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
matplotlib.use('Qt5Agg')

print(sys.version)
