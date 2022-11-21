# standard
import sys
import os
import random
import re
import shutil
from pathlib import Path
from multiprocessing import Process

# Qt
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QPushButton, QVBoxLayout, QTabWidget, QGridLayout
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QCheckBox, QHBoxLayout, QListWidget, QTableWidget, QFileDialog
from PyQt5.QtCore import Qt

import pandas as pd
import numpy as np
from PIL import Image
from natsort import natsorted
from skimage.transform import rescale,resize, downscale_local_mean
from skimage.util import img_as_uint
from sklearn.datasets import make_blobs
from sklearn import decomposition
import scipy.stats
import seaborn as sns

#matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')