import meraki, datetime, json, requests, os.path, shutil, time, threading, os, sys
sys.path.append(os.path.abspath('..'))
from config import *
from config_shared import api_key
from video import *
from bdware import bd_update
from os import path



sys.path.append(os.path.abspath('../DB'))



#Local path to save Images
rooting = os.path.abspath(os.getcwd()) + "/mask-detection"
save_path = rooting + "/static/images/downloaded/"
imagesAnalized = "/static/images/images-analized/"
save_checked = rooting + imagesAnalized
save_checkedMasked = rooting + "/static/images/Masked/"
publishUrl = "http://36e7827354fb.ngrok.io"
publishPath = publishUrl + imagesAnalized

#Function to format the Time
def frmtTime(timeStamp):
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S-%f"):
        if fmt in ("%Y-%m-%d %H:%M:%S.%f"):
            timeStamp = datetime.datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S.%f")
            timeStamp = datetime.datetime.strftime(timeStamp, "%Y-%m-%dT%H:%M:%S-03:00")
            print("passei aqui")
            print (timeStamp)
            return(timeStamp)
        elif fmt in ("%Y-%m-%dT%H:%M:%S-%f"):
            timeStamp = datetime.datetime.strptime(timeStamp, "%Y-%m-%dT%H:%M:%S-%f")
            timeStamp = datetime.datetime.strftime(timeStamp, "%Y-%m-%dT%H:%M:%S-03:00")
            print("passei aqui")
            print (timeStamp)
            return(timeStamp)    

def loopVerification(network_id, mv_serial, statusfile): 
    while path.exists(statusfile):
        eterno = getMerakiImage.main(network_id, mv_serial)
        time.sleep(1) 

#Function to save the image file
def saveFile(myFileName, snapShotUrl):
    global myfileAndPath
    myfileAndPath = os.path.join(save_path, myFileName)
    time.sleep(5)
    response = requests.get(snapShotUrl, stream = True)
    response.raw.decode_content = True
    with open(myfileAndPath,'wb') as f:
        shutil.copyfileobj(response.raw, f)
    checkMask(myfileAndPath)
    return(myfileAndPath)

#Class to handle the POST
class  getMerakiImage:
    def main(network_id, mv_serial, timeStamp=None):
        if timeStamp is None:
            timeStamp = datetime.datetime.now() - datetime.timedelta(minutes=2)
            timeStamp = frmtTime(str(timeStamp))
        global dbTimeStamp
        dbTimeStamp = timeStamp
        myTime = datetime.datetime.strptime(timeStamp, "%Y-%m-%dT%H:%M:%S%z")
        myTime = datetime.datetime.strftime(myTime, "%Y-%m-%d-%H-%M-%S")
        dashboard = meraki.DashboardAPI(api_key=api_key ,suppress_logging=True)
        my_orgs = dashboard.organizations.getOrganizations()
        try:
            mySnap = dashboard.cameras.generateNetworkCameraSnapshot(network_id, mv_serial, timestamp=timeStamp )
            snapShotUrl = mySnap["url"]
        except:
            print("No image available to this camera at this time.")
        global notifyMV
        notifyMV = mv_serial
        global notifyNETID
        notifyNETID = network_id
        global myFileName
        global myNoMaskImage
        myFileName = "From-" + mv_serial + "-at-" + myTime + ".jpeg"
        myNoMaskImage = publishPath + myFileName
        try:
            saveFile(myFileName, snapShotUrl)
        except:
            return ("File available at:" + myNoMaskImage)
    

def checkMask(myfileAndPath):
    mySavedFile = save_checked + myFileName
    mySavedFileMasked = save_checkedMasked + myFileName
    checkImage = tagVideo(videopath=myfileAndPath, outputPath=mySavedFile, outputPathMask=mySavedFileMasked)
    if checkImage == "No mask":
        print ("Pessoa sem mascara detectada.")
        notifyBot(checkImage)
        print ("BOT Notified")

def notifyBot(checkImage):
    body = {
	"alarm": "distance-bot",
	"data": {
		"type": "01",
		"message": "Pessoa sem mascara detectada.",
		"who": notifyMV,
		"image": myNoMaskImage
	        }
        }
    body = json.dumps(body)
    headers = {
  'Content-Type': 'application/json'
    }
    botAddress = "http://159.89.238.176:7000/"
    response = requests.request("POST", url=botAddress, headers=headers, data=body)
    payload={
        "type":"sanitymask",
        "local":"SALA-Log3",
        "network":notifyNETID,
        "serial":notifyMV,
        "url":myNoMaskImage,
        "time": dbTimeStamp
        }
    bd_update(payload)


if __name__ == '__main__':
    getIt = getMerakiImage.main()