from background import Background
from video import WriteVideo, WriteVideoLegacy

class Extractor:
    def __init__(self, output, user=None, user1=None):
        self.output = output
        self.video = None
        self.background = None
        self.user = user
        self.user1 = user1
    def close(self):
        self.video.close()
    def setInfo(self, resolution, fps):
        print(f"video resolution {resolution}, fps: {fps}")
        if WriteVideo.hasFFmpeg():
            self.video = WriteVideo(self.output, resolution, fps)
        else:
            print("Unable to find ffmpeg, falling back to the opencv video writer")
            self.video = WriteVideoLegacy(self.output, resolution, fps)
        self.background = Background(resolution)
    def handleFrame(self, frame):
        if not self.background.hasImg():
            self.background.setImg(frame)
        img = frame
        frame = self.filterBackground(frame)
        if not self.user is None:
            frame = self.user(frame)
        if not self.user1 is None:
            frame = self.user1(img, frame)
        self.video.write(frame)
    def filterBackground(self, frame):
        return self.background.rmBackground(frame)
