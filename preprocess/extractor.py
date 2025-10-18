from background import Background
from video import createVideoWriter

class BaseExtractor:
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

class VideoAnnotate(BaseExtractor):
    def __init__(self, output, user=None, user1=None):
        self.output = output
        self.video = None
        self.user = user
        self.user1 = user1
    def close(self):
        self.video.close()
    def setInfo(self, resolution, fps):
        print(f"video resolution {resolution}, fps: {fps}")
        self.video = createVideoWriter(self.output, resolution, fps)
        super().setInfo(resolution, fps)
    def handleFrame(self, frame):
        img = frame
        frame = super().handleFrame(frame)
        if not self.user is None:
            frame = self.user(frame)
        if not self.user1 is None:
            frame = self.user1(img, frame)
        self.video.write(frame)

