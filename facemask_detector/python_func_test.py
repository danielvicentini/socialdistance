from detect_mask_image_function import detect_mask_complete
from detect_mask_image_function import detect_mask_simplified 


# To use the complete version make sure you have the directories created
#if you download the whole git hub structure you are good to go.
#just add the image that you want to analyze in the images_to_be_analized directory
# before running it

#uncomment it to test it
#result_complete = detect_mask_complete("images_to_be_analyzed/example_03.png")
#print (result_complete)

#this is the simplified version that won't move or create new images
result_simplified = detect_mask_simplified("images_to_be_analyzed/example_01.png")
print (result_simplified)
