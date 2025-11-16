from subprocess import Popen, PIPE, DEVNULL, check_output
from subprocess import run as subprocess_run
import cv2 as cv
import numpy as np
import os

def hasFFmpeg():
    try:
        subprocess_run(['ffmpeg'], stderr=DEVNULL)
        subprocess_run(['ffprobe'], stderr=DEVNULL)
    except:
        return False
    return True

def createVideoWriter(path, resolution, fps, force_opencv=False):
    if (not force_opencv) and hasFFmpeg():
        return WriteVideo(path, resolution, fps)
    return WriteVideoLegacy(path, resolution, fps)

class WriteVideo:
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


def createVideoReader(path, force_opencv=False):
    if force_opencv:
        return VideoReaderLegacy(path)
    if hasFFmpeg():
        return VideoReader(path)
    print("Unable to use ffmpeg, falling back to opencv")
    return VideoReaderLegacy(path)

class VideoReader:
    def __init__(self, path):
        self.path = path
    def getInfo(self):
        stdout = check_output(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate", "-of", "csv=p=0", self.path])
        info = [int(entry) for entry in stdout.decode('utf-8').split("/")[0].split(",")]
        self.codecs = check_output(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name", "-of", "csv=p=0", self.path]).split()
        self.resolution = info[0:2]
        return (self.resolution, info[2])
    def start(self, start, end):
        cmd = ['ffmpeg']
        if not start is None:
            cmd += ["-ss", start]
        if not end is None:
            cmd += ['-to', end]
        if len(os.environ.get("FFMPEG_USE_NVDEC", "")) > 0:
            #cmd += ["-hwaccel","nvdec","-c:v", "av1"]
            cmd += ["-c:v","h264_cuvid"]
        cmd += [ '-i', self.path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f"{self.resolution[0]}x{self.resolution[1]}", '-an', '-']
        print (f"Running {cmd}")
        self.proc = Popen(cmd, stdout=PIPE)
    def process(self, frameHandler, start=None, end=None):
        self.start(start, end)
        imgSize = self.resolution[0]*self.resolution[1]
        bufferShape = (self.resolution[1], self.resolution[0], 3)
        raw = self.proc.stdout.read(imgSize*3)
        while len(raw) == imgSize*3:
            frame = np.ndarray(bufferShape, dtype=np.uint8, buffer=raw)
            frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
            frameHandler(frame)
            raw = self.proc.stdout.read(imgSize*3)

class VideoReaderLegacy:
    def __init__(self, path):
        self.video = cv.VideoCapture(path)
    def getInfo(self):
        resolution = (self.video.get(cv.CAP_PROP_FRAME_WIDTH),self.video.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = self.video.get(cv.CAP_PROP_FPS)
        return (resolution, fps)
    def process(self, frameHandler, start=None, end=None):
        if not end is None:
            end = getTime(end)
        if not start is None:
            start = getTime(start)
            self.video.set(cv.CAP_PROP_POS_MSEC, start)
        while self.video.isOpened():
            ret, frame = self.video.read()
            if not end is None:
                if self.video.get(cv.CAP_PROP_POS_MSEC) > end:
                    break
            if not ret:
                break
            frameHandler(frame)
        self.video.release()

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
