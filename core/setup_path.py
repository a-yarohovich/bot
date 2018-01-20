import os
import sys


def correct_python_path():
    pth_lst = os.path.dirname(os.path.realpath(__file__)).split('/')
    del pth_lst[-1]
    pth = '/'.join(pth_lst)
    sys.path.insert(0, pth)


def print_sys_path():
    print(sys.path)


correct_python_path()
