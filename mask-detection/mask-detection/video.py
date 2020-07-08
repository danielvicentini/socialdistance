from pathlib import Path
import click
import cv2
import torch
from skvideo.io import FFmpegWriter, vreader
from torchvision.transforms import Compose, Resize, ToPILImage, ToTensor
import os

from common.facedetector import FaceDetector
from train import MaskDetector

def tagVideo(modelpath=None, videopath=None, outputPath=None, outputPathMask=None):
    modelpath = "./mask-detection/models/face_mask.ckpt"
    """ detect if persons in video are wearing masks or not
    """
    model = MaskDetector()
    model.load_state_dict(torch.load(modelpath, map_location='cpu')['state_dict'], strict=False)
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    
    faceDetector = FaceDetector(
        prototype='mask-detection/models/deploy.prototxt.txt',
        model='mask-detection/models/res10_300x300_ssd_iter_140000.caffemodel',
    )
    
    transformations = Compose([
        ToPILImage(),
        Resize((100, 100)),
        ToTensor(),
    ])
    
    if outputPath:
        writer = FFmpegWriter(str(outputPath))
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    #cv2.namedWindow('main', cv2.WINDOW_NORMAL)
    labels = ['No mask', 'Mask']
    labelColor = [(10, 0, 255), (10, 255, 0)]
    try:
        for frame in vreader(str(videopath)):
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = faceDetector.detect(frame)
            for face in faces:
                xStart, yStart, width, height = face
                
                # clamp coordinates that are outside of the image
                xStart, yStart = max(xStart, 0), max(yStart, 0)
                
                # predict mask label on extracted face
                faceImg = frame[yStart:yStart+height, xStart:xStart+width]
                
                output = model(transformations(faceImg).unsqueeze(0).to(device))
                _, predicted = torch.max(output.data, 1)
                cv2.rectangle(frame,
                            (xStart, yStart),
                            (xStart + width, yStart + height),
                            (126, 65, 64),
                            thickness=2)
                
                # center text according to the face frame
                textSize = cv2.getTextSize(labels[predicted], font, 1, 2)[0]
                textX = xStart + width // 2 - textSize[0] // 2
                
                # draw prediction label
                cv2.putText(frame,
                            labels[predicted],
                            (textX, yStart-20),
                            font, 1, labelColor[predicted], 2)
            if outputPath:
                try:
                    print(labels[predicted])
                    if labels[predicted] == "No mask":
                        writer.writeFrame(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                        writer.close()
                        os.remove(videopath)
                        print ("Person with no mask detected!")
                        return("No mask")
                    elif labels[predicted] == "Mask":
                        os.remove(videopath)
                        print ("Person with mask detected!")
                        return ("Faced detected with Mask")
                except:
                    os.remove(videopath)
                    print ("No face detected!")
                    return ("No face detected!")
            #cv2.imshow('main', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    #cv2.destroyAllWindows()
    except:
        os.remove(videopath)
        print ("Image could not be opened!")

# pylint: disable=no-value-for-parameter
if __name__ == '__main__':
    tagVideo()
