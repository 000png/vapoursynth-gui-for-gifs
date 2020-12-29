#!./bin/python.exe
"""
Utils related to VapourSynth
"""
import os
import subprocess
import vapoursynth as vs

SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
WORK_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..\\..\\..\\work'))
BIN_DIR = os.path.join(SCRIPT_DIR, '..\\..\\bin')
VS_PIPE = os.path.abspath(os.path.join(BIN_DIR, 'VSPipe.exe'))
FFMPEG = os.path.abspath(os.path.join(BIN_DIR, 'ffmpeg/bin/ffmpeg.exe'))

TRIMMED_FILENAME = os.path.abspath(os.path.join(WORK_DIR, 'tmp.mp4'))

def checkVSScript(filename):
    """ Verify given script is valid """
    cmd = f"{VS_PIPE} --info {filename} -"
    returnCode, out, err = runSubprocess(cmd)

    if returnCode != 0:
        return False, '\n'.join(err.decode('utf-8').splitlines())

    results = '\n'.join(out.decode('utf-8').splitlines())
    return True, f"Script validated! Here's the video output information:\n\n{results}"


def trimVideo(filename, start, end, trimFilename=TRIMMED_FILENAME):
    """ Trim video """
    cmd = f'"{FFMPEG}" -y -ss {start} -t {end} -i "{filename}" -vcodec libx264 -preset ultrafast -pix_fmt yuv420p "{trimFilename}"'

    returnCode, out, err = runSubprocess(cmd, withShell=True)
    if returnCode != 0:
        return False, cmd, '\n'.join(err.decode('utf-8').splitlines())

    return True, cmd, None

def renderVSVideo(script, inFilename, outFilename, extension, start, end):
    """ Render VS video """
    result, trimCmd, err = trimVideo(inFilename, start, end)
    if not result:
        return False, trimCmd, f'TRIM FAILED: Here is the execution output:\n\n{err}'

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

    returnCode, out, err = runSubprocess(cmd, withShell=True)

    print(f"CMD:\n{cmd}\nCODE:\n{returnCode}\nSTDOUT:\n{out.decode('utf-8')}\nSTDERR\n{err.decode('utf-8')}")
    if returnCode != 0 or 'Error:' in err.decode('utf-8'):
        return False, cmd, 'RENDER FAILED: Here is execution output:\n\n' + '\n'.join(err.decode('utf-8').splitlines())

    return True, cmd, f'Successfully wrote to {outFilename}'


def runSubprocess(cmd, errorMsg=None, withShell=False):
    """ Run external process """
    if not withShell and not isinstance(cmd, list):
        cmd = cmd.split(' ')

    if not errorMsg:
        errorMsg = f"Command failed: {' '.join(cmd)}"

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=withShell)
    out, err = p.communicate()

    return p.returncode, out, err
