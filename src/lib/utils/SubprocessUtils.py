#!./bin/python.exe
"""
Utils related to VapourSynth
"""
import os
import posixpath

from lib.SubWindows.FfmpegSettingsWindow import FfmpegSettingsWindow
from .GlobalConstants import WORK_DIR, BIN_DIR

VS_PIPE = os.path.join(BIN_DIR, 'VSPipe.exe').replace(os.sep, posixpath.sep)
FFMPEG = os.path.join(BIN_DIR, 'ffmpeg/bin/ffmpeg.exe').replace(os.sep, posixpath.sep)

TRIMMED_FILENAME = os.path.join(WORK_DIR, 'tmp.mp4').replace(os.sep, posixpath.sep)
RENDER_BAT = os.path.join(WORK_DIR, 'render.bat').replace(os.sep, posixpath.sep)
DURATION_BAT = os.path.join(WORK_DIR, 'duration.bat').replace(os.sep, posixpath.sep)


def checkVSScript(filename):
    """ Verify given script is valid """
    return f'"{VS_PIPE}" --info "{filename}" -'


def trimVideo(filename, start, end, trimFilename=TRIMMED_FILENAME, settings=None):
    """ Trim video """
    if not settings:
        settings = FfmpegSettingsWindow()

    return f'"{FFMPEG}" -y -ss {start} -t {end} -i "{filename}" {settings.getFlags("trim")} "{trimFilename}"'


def renderVSVideo(script, inFilename, outFilename, extension, settings=None):
    """ Render VS video """
    exe = f'"{VS_PIPE}" --y4m "{script}" - | "{FFMPEG}"'

    if not settings:
        settings = FfmpegSettingsWindow()
    flags = settings.getFlags(extension)

    if extension == '.png':
        cmd = f'{exe} -f yuv4mpegpipe -i - {flags} -y "{outFilename}"'
    elif extension == '.mov':
        cmd = f'{exe} -f yuv4mpegpipe -colorspace bt709 -i - {flags} -y "{outFilename}"'
    elif extension == '.mp4':
        cmd = f'{exe} -f yuv4mpegpipe -colorspace bt709 -i - {flags} -y "{outFilename}"'
    else:
        raise ValueError(f"Unrecognized extension {extension}")

    # this is a weird workaround due to this being Windows and QProcess not handling piping; basically
    # write command to render.bat file and have QProcess execute that
    with open(RENDER_BAT, 'w') as fh:
        fh.write(cmd.replace('/', '\\'))

    return f'"{RENDER_BAT}"'


def getVideoDuration(filename):
    """ Get video duration """
    cmd = f'"{FFMPEG}" -i {filename} 2>&1' + "| grep Duration | awk 'print $2}' | tr -d ,"
    with open(DURATION_BAT, 'w') as fh:
        fh.write(cmd.replace('/', '\\'))

    return f'"{DURATION_BAT}"'
