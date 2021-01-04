#!./bin/python.exe
"""
Utils related to VapourSynth
"""
import os
import posixpath

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__)).replace(os.sep, posixpath.sep)
WORK_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../work')).replace(os.sep, posixpath.sep)
BIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../bin')).replace(os.sep, posixpath.sep)
VS_PIPE = os.path.join(BIN_DIR, 'VSPipe.exe').replace(os.sep, posixpath.sep)
FFMPEG = os.path.join(BIN_DIR, 'ffmpeg/bin/ffmpeg.exe').replace(os.sep, posixpath.sep)
TRIMMED_FILENAME = os.path.join(WORK_DIR, 'tmp.mp4').replace(os.sep, posixpath.sep)
RENDER_BAT = os.path.join(WORK_DIR, 'render.bat').replace(os.sep, posixpath.sep)

def checkVSScript(filename):
    """ Verify given script is valid """
    return f'"{VS_PIPE}" --info "{filename}" -'


def trimVideo(filename, start, end, trimFilename=TRIMMED_FILENAME, trimArgs="-vcodec libx264 -preset medium -pix_fmt yuv420p"):
    """ Trim video """
    return f'"{FFMPEG}" -y -ss {start} -t {end} -i "{filename}" {trimArgs} "{trimFilename}"'


def renderVSVideo(script, inFilename, outFilename, extension):
    """ Render VS video """
    exe = f'"{VS_PIPE}" --y4m "{script}" - | "{FFMPEG}"'

    if extension == '.png':
        cmd = f'{exe} -f yuv4mpegpipe -i - -y "{outFilename}"'
    elif extension == '.mov':
        cmd = f'{exe} -f yuv4mpegpipe -colorspace bt709 -i - -vcodec rawvideo -pix_fmt rgb24 ' \
            + f'-sws_flags full_chroma_int+accurate_rnd -y "{outFilename}"'
    elif extension == '.mp4':
        cmd = f'{exe} -f yuv4mpegpipe -colorspace bt709 -i - -vcodec libx264 -qp 0 -y "{outFilename}"'
    else:
        raise ValueError(f"Unrecognized extension {extension}")

    # this is a weird workaround due to this being Windows and QProcess not handling piping; basically
    # write command to render.bat file and have QProcess execute that
    with open(RENDER_BAT, 'w') as fh:
        fh.write(cmd.replace('/', '\\'))

    return f'"{RENDER_BAT}"'
