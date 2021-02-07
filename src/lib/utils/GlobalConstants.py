#!./bin/python.exe
"""
Global constants used by everything; mainly paths
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
WORK_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../work'))
BIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../bin'))