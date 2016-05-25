from params import subject_ids
from params import main_path, data_path
from ipywidgets import widgets
from IPython.display import display, clear_output, Javascript
import mne
from mne.io import Raw
from mne.preprocessing import read_ica
from mne.preprocessing import create_ecg_epochs, create_eog_epochs
import numpy as np
import getpass
import os
# from nipype.utils.filemanip import split_filename as split_f
# Widget related imports
from traitlets import Unicode
# nbconvert related imports
from nbconvert import get_export_names, export_by_name
from nbconvert.writers import FilesWriter
from nbformat import read, NO_CONVERT
from nbconvert.utils.exceptions import ConversionException
from table_handling import get_ECG_EOG_chnames_by_SubjID
import warnings
warnings.filterwarnings('ignore')
