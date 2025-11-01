from background import Background
from video import createVideoWriter

class BackgroundExtractor:
    def __init__(self):
        self.background = None
    def setInfo(self, resolution, fps):
        self.background = Background(resolution)
    def handleFrame(self, frame):
        if not self.background.hasImg():
            self.background.setImg(frame)
        frame = self.filterBackground(frame)
        return frame
    def filterBackground(self, frame):
        return self.background.rmBackground(frame)

class VideoAnnotate(BackgroundExtractor):
    def __init__(self, output, annotate=None):
        self.output = output
        self.video = None
        self.annotate = annotate
    def close(self):
        self.video.close()
    def setInfo(self, resolution, fps):
        print(f"video resolution {resolution}, fps: {fps}")
        self.video = createVideoWriter(self.output, resolution, fps)
        super().setInfo(resolution, fps)
        self.fid = 0
    def handleFrame(self, frame):
        img = frame
        frame = super().handleFrame(frame)
        if not self.annotate is None:
            frame = self.annotate(self.fid, img, frame)
        self.video.write(frame)
        self.fid += 1
