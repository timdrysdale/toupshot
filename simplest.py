import datetime
import numpy as np
from PIL import Image
import toupcam
 
class App:
    def __init__(self):
        self.hcam = None
        self.buf = None
        self.total = 0

# the vast majority of callbacks come from toupcam.dll/so/dylib internal threads
    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.CameraCallback(nEvent)

    def CameraCallback(self, nEvent):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            try:
                self.hcam.PullImageV2(self.buf, 24, None)
                self.total += 1
                print('pull image ok, total = {}'.format(self.total))
                #do something with the image here ...
 
                ts = datetime.datetime.now().timestamp()
                array = bytes_to_array(self.buf, self.width, self.height)
                img = Image.fromarray(array)
                img.save('image-%d.png'%(ts))
                
            except toupcam.HRESULTException:
                print('pull image failed')
        else:
            print('event callback: {}'.format(nEvent))

    def run(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) > 0:
            print('{}: flag = {:#x}, preview = {}, still = {}'.format(a[0].displayname, a[0].model.flag, a[0].model.preview, a[0].model.still))
            for r in a[0].model.res:
                print('\t = [{} x {}]'.format(r.width, r.height))
            self.hcam = toupcam.Toupcam.Open(a[0].id)
            if self.hcam:
                try:
                    width, height = self.hcam.get_Size()
                    self.width = width
                    self.height = height
                    bufsize = ((width * 24 + 31) // 32 * 4) * height
                    print('image size: {} x {}, bufsize = {}'.format(width, height, bufsize))
                    self.buf = bytes(bufsize)
                    if self.buf:
                        try:
                            self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                        except toupcam.HRESULTException:
                            print('failed to start camera')
                    input('press ENTER to exit')
                finally:
                    self.hcam.Close()
                    self.hcam = None
                    self.buf = None
            else:
                print('failed to open camera')
        else:
            print('no camera found')

def bytes_to_array(data, width, height):

    # convert bytes into array - need to know image dims and data size
    intarray = [x for x in data]
    imgarray = np.array(intarray,dtype=np.uint8).reshape(width,height,3)
      

    return imgarray

            
if __name__ == '__main__':
    app = App()
    app.run()
