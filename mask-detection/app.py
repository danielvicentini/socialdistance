from flask import Flask, request, render_template, redirect, url_for
from dwImages import getMerakiImage, loopVerification
import threading, os, time
from os import path
app = Flask(__name__)

statuspath = os.path.abspath(os.getcwd()) + "/mask-detection/status/"

@app.route('/', methods=['GET', 'POST'])
def imagesAPI():
    if request.method == 'POST':
        network_id = request.values.get("network_id", type=str, default=None)
        mv_serial = request.values.get("mv_serial", type=str, default=None)
        timeStamp = request.values.get("timeStamp", type=str, default=None)
        return str(getMerakiImage.main(network_id, mv_serial, timeStamp))
    if request.method == 'GET':
        return redirect(url_for('static', filename='/' + myFileName), code=301)

@app.route('/loop', methods=['GET', 'POST'])
def loopImages():
    if request.method == 'POST':
        network_id = request.values.get("network_id", type=str, default=None)
        mv_serial = request.values.get("mv_serial", type=str)
        turn = request.values.get("turn", type=str, default=None)
        print (mv_serial)
        print (network_id)
        statusfile = os.path.join(statuspath, mv_serial)
        if turn == "on":
            if path.exists(statusfile) is False:
                f= open(statusfile,"w+")
                f.close()
                thread = threading.Thread(target=loopVerification, args=(network_id, mv_serial, statusfile))
                thread.start()
                return("Analysis started to camera: " + str(mv_serial))
            else:
                os.remove(statusfile)
                time.sleep(2)
                f= open(statusfile,"w+")
                f.close()
                thread = threading.Thread(target=loopVerification, args=(network_id, mv_serial, statusfile))
                thread.start()
                return("This camera already has an ongoing analysis. Restarting the process!")
        if turn == "off":
            try:
                os.remove(statusfile)
                return("Analysis stopped to camera: " + str(mv_serial))
            except:
                return ("Analysis does not exist.")
        else:
            return ("Please, send the option ""turn"" with the value ""one"" to enable or ""off"" to disable the analysis.")
    else:
        return "You need to send a POST containing the required arguments (network_id, mv_serial and timestamp or turn on|off option)"
if __name__ == '__main__':
    app.run(host="159.89.238.176", port=10000, debug=True, threaded=True)
