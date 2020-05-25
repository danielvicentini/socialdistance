# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import cv2
import os
import time
import shutil

""" 
There is two versions of the function: complete, simplified

The complete version of the function not only analyze the image provided but also 
store a new copy of the image with the analysis made, move the original image
to a new directory, and also save just the face image with or without mask
in a separate directory for a future analysis or use in data labeling.
To correct use this function make sure you have all the files and directories
needed. 

The simplified version just analyze the image provided.
"""

def detect_mask_complete(image_file_path):
	# construct the argument parser and parse the arguments
	args = {'face': 'face_detector', 'model': 'mask_detector.model', 'confidence': 0.5}
	#image_file = "images_to_be_analyzed/example_01.png"
	args["image"] = str(image_file_path)

	#directories that will be used so store the images
	dir_faces_detected_with_mask = "faces_detected_with_mask/"
	dir_faces_detected_without_mask = "faces_detected_without_mask/"
	dir_images_without_faces = "no_faces_detected/"
	dir_images_processed_results = "results/"
	#ideally use this directory to store the images that will be analyzed
	#if you do after the analysis the image will be moves to images_processed
	dir_images_to_be_processed = "images_to_be_analyzed/"
	dir_images_processed = "images_analyzed/" 

	# load our serialized face detector model from disk
	print("[INFO] loading face detector model...")
	prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
	weightsPath = os.path.sep.join([args["face"],
		"res10_300x300_ssd_iter_140000.caffemodel"])
	net = cv2.dnn.readNet(prototxtPath, weightsPath)

	# load the face mask detector model from disk
	print("[INFO] loading face mask detector model...")
	model = load_model(args["model"])

	# load the input image from disk, clone it, and grab the image spatial
	# dimensions
	try:
		image = cv2.imread(args["image"])
		orig = image.copy()
		(h, w) = image.shape[:2]
	except:
		print("Image not found in the path")
		exit()

	# construct a blob from the image
	blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
		(104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the face detections
	print("[INFO] computing face detections...")
	net.setInput(blob)
	detections = net.forward()

	#start # faces counter and results dictionary
	number_faces = 0
	results = {}
	#Split the file name from the complete path
	filename = os.path.split(image_file_path)[1]
	#print(filename)
	results ["filename"] = filename
	results ["faces"] = {}
	results ["number_of_faces"] = {}

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the detection
		confidence = detections[0, 0, i, 2]
		
		# filter out weak detections by ensuring the confidence is
		# greater than the minimum confidence

		if confidence > args["confidence"]:
			# compute the (x, y)-coordinates of the bounding box for
			# the object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# ensure the bounding boxes fall within the dimensions of
			# the frame
			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

			# extract the face ROI, convert it from BGR to RGB channel
			# ordering, resize it to 224x224, and preprocess it
			number_faces = number_faces + 1
			face = image[startY:endY, startX:endX]
			face_saved = face
			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
			face = cv2.resize(face, (224, 224))
			face = img_to_array(face)
			face = preprocess_input(face)
			face = np.expand_dims(face, axis=0)

			# pass the face through the model to determine if the face
			# has a mask or not
			(mask, withoutMask) = model.predict(face)[0]
			# determine the class label and color we'll use to draw
			# the bounding box and text
			label = "using mask" if mask > withoutMask else "not using mask"
			color = (0, 255, 0) if label == "using mask" else (0, 0, 255)
			
			#store the face analysis result in the results dictionary
			results ["faces"][number_faces] = [label, round(max(mask,withoutMask) * 100,2)]

			# include the probability in the label
			#label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
			label = "{} ({:.2f}%)".format(label, round(max(mask, withoutMask) * 100,2))
			
			# display the label and bounding box rectangle on the output
			# frame
			cv2.putText(image, label, (startX, startY - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
			cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)

			#Save the faces detected with the timestamp in the right folder
			if mask > withoutMask:
				new_filename = dir_faces_detected_with_mask + str(time.time()) + "_" + filename
				cv2.imwrite(new_filename,face_saved)
			else:
				new_filename = dir_faces_detected_without_mask + str(time.time()) + "_" + filename
				cv2.imwrite(new_filename,face_saved)
			#Print on console the results of the analysis
			print ("Face #" + str(number_faces) + " detected " + label +  " - saved as " + new_filename)
			
	#FC if no faces detected save in a different folder
	if number_faces == 0: 
		#print on console that no faces were detected
		print("No face faces in the imagem")
		new_filename = dir_images_without_faces + str(time.time()) + "_" + filename
		cv2.imwrite(new_filename,image)
		del results['faces']
		results["number_of_faces"] = 0
	else:
		#print on console the number of faces detected
		print("Total number of faces identified: " + str(number_faces))
		results["number_of_faces"] = number_faces
		

	#FC save image analysis
	new_filename = dir_images_processed_results + str(time.time()) + "_" + filename
	cv2.imwrite(new_filename,image)

	#move analysed image to the "image_analized" directory
	shutil.move(dir_images_to_be_processed + filename, dir_images_processed + filename)

	#Results of the analysis with the name of the filename, number of faces
	# and the analysis per face detected
	return(results)


def detect_mask_simplified(image_file_path):
	# construct the argument parser and parse the arguments
	args = {'face': 'face_detector', 'model': 'mask_detector.model', 'confidence': 0.5}
	#image_file = "images_to_be_analyzed/example_01.png"
	args["image"] = str(image_file_path)

	#directories that will be used so store the images
	dir_faces_detected_with_mask = "faces_detected_with_mask/"
	dir_faces_detected_without_mask = "faces_detected_without_mask/"
	dir_images_without_faces = "no_faces_detected/"
	dir_images_processed_results = "results/"
	#ideally use this directory to store the images that will be analyzed
	#if you do after the analysis the image will be moves to images_processed
	dir_images_to_be_processed = "images_to_be_analyzed/"
	dir_images_processed = "images_analyzed/" 

	# load our serialized face detector model from disk
	print("[INFO] loading face detector model...")
	prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
	weightsPath = os.path.sep.join([args["face"],
		"res10_300x300_ssd_iter_140000.caffemodel"])
	net = cv2.dnn.readNet(prototxtPath, weightsPath)

	# load the face mask detector model from disk
	print("[INFO] loading face mask detector model...")
	model = load_model(args["model"])

	# load the input image from disk, clone it, and grab the image spatial
	# dimensions
	try:
		image = cv2.imread(args["image"])
		orig = image.copy()
		(h, w) = image.shape[:2]
	except:
		print("Image not found in the path")
		exit()

	# construct a blob from the image
	blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
		(104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the face detections
	print("[INFO] computing face detections...")
	net.setInput(blob)
	detections = net.forward()

	#start # faces counter and results dictionary
	number_faces = 0
	results = {}
	#Split the file name from the complete path
	filename = os.path.split(image_file_path)[1]
	#print(filename)
	results ["filename"] = filename
	results ["faces"] = {}
	results ["number_of_faces"] = {}

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the detection
		confidence = detections[0, 0, i, 2]
		
		# filter out weak detections by ensuring the confidence is
		# greater than the minimum confidence

		if confidence > args["confidence"]:
			# compute the (x, y)-coordinates of the bounding box for
			# the object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# ensure the bounding boxes fall within the dimensions of
			# the frame
			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

			# extract the face ROI, convert it from BGR to RGB channel
			# ordering, resize it to 224x224, and preprocess it
			number_faces = number_faces + 1
			face = image[startY:endY, startX:endX]
			face_saved = face
			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
			face = cv2.resize(face, (224, 224))
			face = img_to_array(face)
			face = preprocess_input(face)
			face = np.expand_dims(face, axis=0)

			# pass the face through the model to determine if the face
			# has a mask or not
			(mask, withoutMask) = model.predict(face)[0]
			# determine the class label and color we'll use to draw
			# the bounding box and text
			label = "using mask" if mask > withoutMask else "not using mask"
			color = (0, 255, 0) if label == "using mask" else (0, 0, 255)
			
			#store the face analysis result in the results dictionary
			results ["faces"][number_faces] = [label, round(max(mask,withoutMask) * 100,2)]

			# include the probability in the label
			#label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
			label = "{} ({:.2f}%)".format(label, round(max(mask, withoutMask) * 100,2))
			
			# display the label and bounding box rectangle on the output
			# frame
			cv2.putText(image, label, (startX, startY - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
			cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)

			
	#FC if no faces detected save in a different folder
	if number_faces == 0: 
		#print on console that no faces were detected
		print("No faces identified in the imagem")
		del results['faces']
		results["number_of_faces"] = 0
	else:
		#print on console the number of faces detected
		print("Total number of faces identified: " + str(number_faces))
		results["number_of_faces"] = number_faces
		
	#Results of the analysis with the name of the filename, number of faces
	# and the analysis per face detected
	return(results)