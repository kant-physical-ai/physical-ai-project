from lib import device_libs
# from . import is_available_video_device  # 또는
class Tot :
    def __init__(self) :
        pass

    def test(self) :
        device_libs.is_available_video_device(0)
        print("test")



