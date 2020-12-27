#!./bin/python.exe
"""
Utils related to VapourSynth
"""
import os
import subprocess
import vapoursynth as vs

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
BIN_DIR = os.path.join(SCRIPT_DIR, '../../bin')

def checkScript(filename):
    """ Verify given script is valid """
    cmd = f"{os.path.join(BIN_DIR, 'VSPipe.exe')} --info {filename} -"
    returnCode, out, err = runSubprocess(cmd)

    if returnCode != 0:
        results = '\n'.join(err.decode('utf-8').splitlines())
        return False, f"Script reported errors:\n\n{results}"

    results = '\n'.join(out.decode('utf-8').splitlines())
    return True, f"Script validated! Here's the video output information:\n\n{results}"


def runSubprocess(cmd, errorMsg=None, withShell=False):
    """ Run external process """
    if not withShell and not isinstance(cmd, list):
        cmd = cmd.split(' ')

    if not errorMsg:
        errorMsg = f"Command failed: {' '.join(cmd)}"

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=withShell)
    out, err = p.communicate()

    return p.returncode, out, err
