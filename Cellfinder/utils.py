 #from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

import sys
#print(sys.version)
import os
import pathlib
from pathlib import Path
import re
import shutil
import pandas as pd
import numpy as np
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt
from PIL import Image
from natsort import natsorted
from skimage.transform import rescale,resize, downscale_local_mean
from skimage.util import img_as_uint

from multiprocessing import Process

from sklearn.datasets import make_blobs
from sklearn import decomposition
import scipy.stats
import matplotlib.pyplot as plt
import seaborn as sns

from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import matplotlib
matplotlib.use('Qt5Agg')
#from plotnine import ggplot, aes, geom_bar, coord_flip