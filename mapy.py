import os
import sys
from PIL import Image
import folium
import base64

this_py_file = os.path.dirname(sys.argv[0])
folder_name=this_py_file.split("/")[-1]

resize_path = os.path.dirname(sys.argv[0])+'/Resized_Shapes/' #the path where to save resized images
# create new folder
if not os.path.exists(resize_path):
    os.makedirs(resize_path)

def get_data_and_resize():
    print("Getting data and resizing...")
    global gps_coord_degrees
    gps_coord_degrees = {}
    global dates
    dates = {}
    index=0
    for image in os.listdir(this_py_file):
        imagename = os.fsdecode(image)
        if imagename.endswith(('.jpeg', '.jpg', '.png', '.gif')) or imagename.endswith(('.JPEG', 'JPG', '.PNG', '.GIF')):
            image = Image.open(imagename)
            try:
                image_exif = image._getexif()
                if image_exif[34853]:
                    gps_coord_degrees[imagename] = [image_exif[34853][1]]
                    gps_coord_degrees[imagename].append(image_exif[34853][2])
                    gps_coord_degrees[imagename].append(image_exif[34853][3])
                    gps_coord_degrees[imagename].append(image_exif[34853][4])

                    try:
                        dates[imagename] = image_exif[36867]
                    except KeyError:
                        dates[imagename] = "No Date Available"

                    try:
                        image_orientation = image_exif[274]
                        if image_orientation == 6:
                            baseheight = 200
                            hpercent = (baseheight / float(image.size[1]))
                            wsize = int((float(image.size[0]) * float(hpercent)))
                            image = image.resize((wsize, baseheight), Image.ANTIALIAS)
                            image = image.rotate(-90, resample=0, expand=True)
                            image.save(resize_path + imagename, 'jpeg', quality=70)

                        if image_orientation == 3:
                            baseheight = 200
                            hpercent = (baseheight / float(image.size[1]))
                            wsize = int((float(image.size[0]) * float(hpercent)))
                            image = image.resize((wsize, baseheight), Image.ANTIALIAS)
                            image = image.rotate(180, resample=0, expand=True)
                            image.save(resize_path + imagename, 'jpeg', quality=70)

                        if image_orientation == 8:
                            baseheight = 200
                            hpercent = (baseheight / float(image.size[1]))
                            wsize = int((float(image.size[0]) * float(hpercent)))
                            image = image.resize((wsize, baseheight), Image.ANTIALIAS)
                            image = image.rotate(90, resample=0, expand=True)
                            image.save(resize_path + imagename, 'jpeg', quality=70)
                        else:
                            basewidth = 200
                            wpercent = (basewidth / float(image.size[0]))
                            hsize = int((float(image.size[1]) * float(wpercent)))
                            image = image.resize((basewidth, hsize), Image.ANTIALIAS)
                            image.save(resize_path + imagename, 'jpeg', quality=70)
                    except TypeError:
                        pass
                    except KeyError:
                        pass
                index+=1
            except TypeError:
                pass
            except KeyError:
                pass
    print(f"{index} pictures processed...")

def get_coord_dec():
    print("Getting coordinates...")
    gps_coord_decimals = {}
    for image in gps_coord_degrees:
        lat = gps_coord_degrees[image][1]
        long = gps_coord_degrees[image][3]
        gps_coord_decimals[image] = [((lat[0][0]) + (lat[1][0] / 60) + (lat[2][0] / 360000)), ((long[0][0]) + (long[1][0] / 60) + (long[2][0] / 360000))]
        if gps_coord_degrees[image][0] == "S":
            gps_coord_decimals[image][0] *= -1
        if gps_coord_degrees[image][2] == "W":
            gps_coord_decimals[image][1] *= -1

    return gps_coord_decimals


m = folium.Map(location=[43.760024, 7.232068],zoom_start=5)

def make_map():
    get_data_and_resize()
    coordinates=get_coord_dec()
    print("Making map...")
    for image in os.listdir(resize_path):
        imagename= os.fsdecode(image)

        image = Image.open(this_py_file + "/" + imagename)
        image_exif = image._getexif()
        image_orientation = image_exif[274]
        if imagename.endswith(('.jpeg', '.jpg', '.png', '.gif')) or imagename.endswith(('.JPEG', '.JPG', '.PNG', '.GIF')):
            encoded = base64.b64encode(open(resize_path+imagename, 'rb').read())
            if image_orientation==6 or image_orientation==8:
                html = '<img src="data:image/jpeg;base64,{}">'.format
                resolution, width, height = 20, 10, 14
            else:
                html = '<img src="data:image/jpeg;base64,{}">'.format
                resolution, width, height = 20, 10, 8

            iframe = folium.IFrame(html(encoded.decode('UTF-8')), width=(resolution*width) + 20, height=(resolution*height) + 20)
            popup = folium.Popup(iframe, min_width=150, min_height=150)
            icon = folium.Icon(color="blue", icon="ok")
            tooltip = dates[imagename]
            marker = folium.Marker(location=coordinates[imagename], popup=popup, tooltip=tooltip, icon=icon)

            marker.add_to(m)
            m.save(f"{folder_name}_Map.html")



make_map()

