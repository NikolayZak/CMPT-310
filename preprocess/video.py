from subprocess import Popen, PIPE
from subprocess import run as subprocess_run
import cv2 as cv
import numpy as np

class WriteVideo:
    def hasFFmpeg():
        try:
            subprocess_run(['ffmpeg'])
        except:
            return False
        return True
    def __init__(self, path, resolution, fps):
        resolution = (int(resolution[0]), int(resolution[1]))
        cmd = ['ffmpeg', '-y', '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', f'{resolution[0]}x{resolution[1]}', '-framerate', f'{fps}', '-i', '-', '-vcodec', "libx264", "-pix_fmt", "yuv420p", "-profile:v", "baseline", "-movflags" ,"faststart", "-an" ,  path]
        print (f"Running {cmd}")
        self.proc = Popen(cmd, stdin=PIPE)
        self.stdin = self.proc.stdin
    def write(self, img):
        self.stdin.write(cv.cvtColor(img, cv.COLOR_BGR2RGB).tobytes())
    def close(self):
        self.stdin.close()
        self.proc.wait()

class WriteVideoLegacy:
    def __init__(self, path, resolution, fps):
        resolution = (int(resolution[0]), int(resolution[1]))
        self.fourcc = cv.VideoWriter_fourcc(*"mp4v")
        self.video = cv.VideoWriter(path, self.fourcc, fps, resolution)
    def write(self, img):
        self.video.write(img)
    def close(self):
        self.video.release()

def getTime(time):
    if type(time) == str:
        if ":" in time:
            time_int = 0
            for i in time.split(":"):
                time_int *= 60
                time_int += int(i)
            return time_int*1000
        return int(time)*1000
    return round(time*1000)

def readVideo(path, func, start=None, end=None, info=None):
    video = cv.VideoCapture(path)
    if not info is None:
        resolution = (video.get(cv.CAP_PROP_FRAME_WIDTH),video.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv.CAP_PROP_FPS)
        info(resolution, fps)
    end_time = None
    if not end is None:
        end_time = getTime(end)
    if not start is None:
        start_time = getTime(start)
        video.set(cv.CAP_PROP_POS_MSEC, start_time)
    while video.isOpened():
        ret, frame = video.read()
        if not end_time is None:
            if video.get(cv.CAP_PROP_POS_MSEC) > end_time:
                print("past time")
                break
        if not ret:
            print("done")
            break
        func(frame)
    video.release()
