from django.shortcuts import render
from .forms import VehicleForm
from django.conf import settings

import os
import cv2
from ultralytics import YOLO
import base64
import numpy as np
import requests


# Create your views here.
def index (request):
    return render(request , 'index.html')

def try_(request):
    form = VehicleForm()
    if request.method == 'POST':
        form  = VehicleForm(request.POST,request.FILES)
        name = request.FILES['file'].name
        if 'image/' in request.FILES['file'].content_type:

            if form.is_valid():
                if ' 'in name:
                    name = name.replace(' ', '')
                    obj = form.save(commit=False)
                    obj.file.name = name
                    obj.save()
                else:
                    form.save()
                form = VehicleForm()

                # path of saved input image
                path = os.path.join(settings.MEDIA_ROOT,'vehicle','images',name,name)
                try:
                    os.mkdir(os.path.join(settings.MEDIA_ROOT,'vehicle','images',name, "crops"))
                    os.mkdir(os.path.join(settings.MEDIA_ROOT,'vehicle','images',name, "plates"))
                except OSError:
                    pass 
                crops , labels , img  , filenames = get_class(path)
                plates = []
                platestxt = []
                colors = []
                status = []
                brands = []
                for i in range(len(crops)):
                    path = os.path.join(settings.MEDIA_ROOT,'vehicle','images',name,'crops',filenames[i])
                    plate , platetxt = get_plate(path , name)
                    plates.append(plate)
                    platestxt.append(platetxt)
                    colors.append(get_color(path))
                    status.append(get_status(path))
                    brands.append(get_brand(path))
                all_list = zip(labels , crops , plates , platestxt , colors , brands , status)
                original_img_path = '/media'+'/vehicle/'+'images/'+ name +'/' +name
                output_img_path = '/media'+'/vehicle/'+'images/'+ name +'/' +'output.png'
                return render(request , 'try.html',{'form':form,'img':img , 'all_list':all_list , 'original':original_img_path, 'output':output_img_path})
            else:
                form = VehicleForm()


        elif 'video/' in request.FILES['file'].content_type:
            if form.is_valid():
                form.save()
                form = VehicleForm()
                name = request.FILES['file'].name
                path = os.path.join(settings.MEDIA_ROOT,'vehicle','videos',name)
                try:
                    os.mkdir(os.path.join(settings.MEDIA_ROOT,'vehicle','videos',name, "crops"))
                    os.mkdir(os.path.join(settings.MEDIA_ROOT,'vehicle','videos',name, "plates"))
                except OSError:
                    pass 
                get_class_vedio(path)
                out_video_path = '/media'+'/vehicle/'+'videos/'+ name +'/' +'output/'+ name
                out_video_path = replace_extension(out_video_path)
                return render(request , 'try.html',{'form':form, 'out_video_path':out_video_path})
            
        else:
            pass

    return render(request , 'try.html',{'form':form})


def get_class(img_path):
    model = YOLO("E:\\Django\\GP\\car_identification\\vclass\\best.pt")  # load a custom model
    img_name = os.path.basename(img_path)  
    results = model.predict(img_path)
    img = cv2.imread(img_path)
    img2 = cv2.imread(img_path)
    crops = []
    labels = []
    filename_croped = []
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            x1, y1, x2, y2 = result.boxes.xyxy[i].tolist()
            x, y, w, h = result.boxes.xywh[i].tolist()
            cls = result.boxes.cls[i]
            conf = result.boxes.conf[i]
            label = f"{model.names[int(cls)]} {conf:.2f}"
            if h > 75 and w > 100 :
                crop_image = img2[int(y1):int(y2), int(x1):int(x2)]
                filename_croped.append(f'{x1}.png')
                cv2.imwrite(os.path.join(settings.MEDIA_ROOT,'vehicle','images',img_name,'crops', f'{x1}.png' ), crop_image)

                cls_l= f"{model.names[int(cls)]}"
                labels.append(cls_l)
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText( img, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                retval, buffer = cv2.imencode('.jpg', crop_image)
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                crops.append(image_base64)

    
    cv2.imwrite(os.path.join(settings.MEDIA_ROOT,'vehicle','images',img_name,'output.png' ), img)     
    retval, buffer = cv2.imencode('.jpg', img)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return crops , labels , image_base64 , filename_croped

def get_plate(img_path ,original_img_name):
    model = YOLO("E:\\Django\\GP\\car_identification\\vplate\\best.pt")  # load a custom model  
    results = model.predict(img_path)
    img = cv2.imread(img_path)
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            if i==0:
                x1, y1, x2, y2 = result.boxes.xyxy[i].tolist()
                crop_image = img[int(y1):int(y2), int(x1):int(x2)]
                cv2.imwrite(os.path.join(settings.MEDIA_ROOT,'vehicle','images',original_img_name,'plates', f'{x1}.png' ), crop_image)
                txt_plate_number = get_platenumber(os.path.join(settings.MEDIA_ROOT,'vehicle','images',original_img_name,'plates', f'{x1}.png' ))
                retval, buffer = cv2.imencode('.jpg', crop_image)
                plate_image_base64 = base64.b64encode(buffer).decode('utf-8')
                return plate_image_base64 , txt_plate_number
    return None , "Unknown"

def get_platenumber(img_path):
    regions = ['mx', 'us-ca'] # Change to your country
    token = 'Token dbd16f0a9684d8a881583dff031c7d8c92dbd005'
    with open(img_path, 'rb') as fp:
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            data=dict(regions=regions),  # Optional
            files=dict(upload=fp),
            headers={'Authorization': token})
        results = response.json()
        if len(results['results']) >0:
            return results['results'][0]['plate']
    return "Unknown"


def get_color(img_path):

    image = cv2.imread(img_path)
    # Convert the image to the HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    lower_orange = np.array([10, 70, 50])
    upper_orange = np.array([20, 255, 255])

    lower_yellow = np.array([20, 70, 50])
    upper_yellow = np.array([30, 255, 255])

    lower_green = np.array([30, 70, 50])
    upper_green = np.array([60, 255, 255])

    lower_blue = np.array([100, 70, 50])
    upper_blue = np.array([130, 255, 255])

    lower_purple = np.array([130, 70, 50])
    upper_purple = np.array([160, 255, 255])

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])

    lower_gray = np.array([0, 0, 100])
    upper_gray = np.array([180, 30, 200])

    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])

    # Create masks for different colors
    red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    orange_mask = cv2.inRange(hsv_image, lower_orange, upper_orange)

    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    green_mask = cv2.inRange(hsv_image, lower_green, upper_green)

    blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

    purple_mask = cv2.inRange(hsv_image, lower_purple, upper_purple)

    white_mask = cv2.inRange(hsv_image, lower_white, upper_white)

    gray_mask = cv2.inRange(hsv_image, lower_gray, upper_gray)

    black_mask = cv2.inRange(hsv_image, lower_black, upper_black)

    # Count the number of pixels that belong to each color
    num_red_pixels = cv2.countNonZero(red_mask)
    num_orange_pixels = cv2.countNonZero(orange_mask)
    num_yellow_pixels = cv2.countNonZero(yellow_mask)
    num_green_pixels = cv2.countNonZero(green_mask)
    num_blue_pixels = cv2.countNonZero(blue_mask)
    num_purple_pixels = cv2.countNonZero(purple_mask)

    num_white_pixels = cv2.countNonZero(white_mask)
    num_gray_pixels = cv2.countNonZero(gray_mask)
    num_black_pixels = cv2.countNonZero(black_mask)

    # Estimate the percentage of the image that belongs to each color

    total_pixels = image.shape[0] * image.shape[1]
    red_percentage = int((num_red_pixels / total_pixels) * 100)
    orange_percentage = int((num_orange_pixels / total_pixels) * 100)
    yellow_percentage = int((num_yellow_pixels / total_pixels) * 100)
    green_percentage = int((num_green_pixels / total_pixels) * 100)
    blue_percentage = int((num_blue_pixels / total_pixels) * 100)
    purple_percentage = int((num_purple_pixels / total_pixels) * 100)
    white_percentage = int((num_white_pixels / total_pixels) * 100)
    gray_percentage = int((num_gray_pixels / total_pixels) * 100)
    black_percentage = int((num_black_pixels / total_pixels) * 100)

    # Define the color names and percentages
    colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "White", "Gray", "Black"]
    percentages = [red_percentage, orange_percentage, yellow_percentage, green_percentage, blue_percentage, purple_percentage, white_percentage, gray_percentage, black_percentage]
    max_num, max_idx = max((num, idx) for idx, num in enumerate(percentages))
    color = colors[max_idx]
    return color

def get_status(img_path):
    model = YOLO("E:\\Django\\GP\\car_identification\\vstatus\\best.pt")  # load a custom model  
    results = model.predict(img_path)
    img = cv2.imread(img_path)
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            if i>=0:
                return "Damaged"
        return "Not Damaged"

def get_brand(img_path):
    model = YOLO("E:\\Django\\GP\\car_identification\\vbrand\\best.pt")  # load a custom model  
    results = model.predict(img_path)
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            if i==0:
                cls = result.boxes.cls[i]
                cls_l= f"{model.names[int(cls)]}"
                return cls_l
    return "Unknown"


" Video "

def get_class_vedio(video_path):
    model = YOLO("E:\\Django\\GP\\car_identification\\vclass\\best.pt")
    video_name = os.path.basename(video_path)  
    model.predict(video_path , save=True , project=settings.BASE_DIR ,name= os.path.join(settings.MEDIA_ROOT,'vehicle','videos',video_name,'output'))

def replace_extension(filepath, new_extension='webm'):
    """
    Replace the extension of a file path with a specified extension.

    Args:
        filepath (str): The file path to modify.
        new_extension (str): The new extension to use.

    Returns:
        str: The modified file path.
    """
    # Split the file path into its base name and extension
    base_path, old_extension = os.path.splitext(filepath)

    # Create the new file path with the desired extension
    new_filepath = base_path + '.' + new_extension

    return new_filepath

