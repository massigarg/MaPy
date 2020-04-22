import os
import sys
from PIL import Image
import folium
from folium.plugins import MarkerCluster
import base64

this_py_file = os.path.dirname(sys.argv[0])
folder_name = os.path.basename(this_py_file)


# the path where to save resized images
resize_path = os.path.dirname(sys.argv[0])+'/Resized_Shapes/'
# create new folder
if not os.path.exists(resize_path):
    os.makedirs(resize_path)


def get_data_and_resize():
    print("Getting data and resizing...Please Wait...")
    global gps_coord_degrees
    gps_coord_degrees = {}
    global dates
    dates = {}
    index = 0
    for image in os.listdir(this_py_file):
        imagename = os.fsdecode(image)
        if imagename.endswith(('.jpeg', '.jpg', '.png', '.gif')) or imagename.endswith(('.JPEG', 'JPG', '.PNG', '.GIF')):
            print(imagename)
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

                    width, height = image.size

                    try:
                        image_orientation = image_exif[274]
                        if image_orientation == 6:
                            baseheight = 200
                            hpercent = (baseheight / float(image.size[1]))
                            wsize = int(
                                (float(image.size[0]) * float(hpercent)))
                            image = image.resize(
                                (wsize, baseheight), Image.ANTIALIAS)
                            image = image.rotate(-90, resample=0, expand=True)
                            image.save(resize_path + imagename,
                                       'jpeg', quality=30)

                        if image_orientation == 3:
                            baseheight = 200
                            hpercent = (baseheight / float(image.size[1]))
                            wsize = int(
                                (float(image.size[0]) * float(hpercent)))
                            image = image.resize(
                                (wsize, baseheight), Image.ANTIALIAS)
                            image = image.rotate(180, resample=0, expand=True)
                            image.save(resize_path + imagename,
                                       'jpeg', quality=30)

                        if image_orientation == 8:
                            baseheight = 200
                            hpercent = (baseheight / float(image.size[1]))
                            wsize = int(
                                (float(image.size[0]) * float(hpercent)))
                            image = image.resize(
                                (wsize, baseheight), Image.ANTIALIAS)
                            image = image.rotate(90, resample=0, expand=True)
                            image.save(resize_path + imagename,
                                       'jpeg', quality=30)
                        else:
                            basewidth = 200
                            wpercent = (basewidth / float(image.size[0]))
                            hsize = int(
                                (float(image.size[1]) * float(wpercent)))
                            image = image.resize(
                                (basewidth, hsize), Image.ANTIALIAS)
                            image.save(resize_path + imagename,
                                       'jpeg', quality=30)
                    except KeyError:
                        print(f"No orientation Exif available for: {imagename}")
                    finally:
                        if width>height:
                            basewidth = 200
                            wpercent = (basewidth / float(image.size[0]))
                            hsize = int(
                                (float(image.size[1]) * float(wpercent)))
                            image = image.resize(
                                (basewidth, hsize), Image.ANTIALIAS)
                            image.save(resize_path + imagename,
                                       'jpeg', quality=30)
                        else:
                            baseheight = 200
                            hpercent = (baseheight / float(image.size[1]))
                            wsize = int(
                                (float(image.size[0]) * float(hpercent)))
                            image = image.resize(
                                (wsize, baseheight), Image.ANTIALIAS)
                            image = image.rotate(-90, resample=0, expand=True)
                            image.save(resize_path + imagename,
                                       'jpeg', quality=30)


                index += 1
            except:
                pass

    print(f"{index} pictures processed...")


def get_coord_dec():
    print("Getting coordinates...")
    gps_coord_decimals = {}
    for image in gps_coord_degrees:
        lat = gps_coord_degrees[image][1]
        long = gps_coord_degrees[image][3]
        gps_coord_decimals[image] = [((lat[0][0]) + (lat[1][0] / 60) + (
            lat[2][0] / 360000)), ((long[0][0]) + (long[1][0] / 60) + (long[2][0] / 360000))]
        if gps_coord_degrees[image][0] == "S":
            gps_coord_decimals[image][0] *= -1
        if gps_coord_degrees[image][2] == "W":
            gps_coord_decimals[image][1] *= -1

    return gps_coord_decimals


def make_map():
    m = folium.Map(location=[43.760024, 7.232068], zoom_start=5)

    marker_cluster = MarkerCluster(
        name='1000 clustered icons',
        overlay=False,
        control=False,
        icon_create_function=None
    ).add_to(m)

    get_data_and_resize()
    coordinates = get_coord_dec()
    print("Making map...Please Wait...")
    for image in os.listdir(resize_path):
        imagename = os.fsdecode(image)
        image = Image.open(imagename)
        encoded = base64.b64encode(open(resize_path + imagename, 'rb').read())
        width, height = image.size

        try:
            image_exif = image._getexif()
            image_orientation = image_exif[274]

            if image_orientation == 6 or image_orientation == 8:
                html = '<img src="data:image/jpeg;base64,{}">'.format
                resolution, width, height = 20, 10, (width / height * 10.5)
            else:
                html = '<img src="data:image/jpeg;base64,{}">'.format
                resolution, width, height = 20, 10, (height / width * 10.5)
        except:
            width, height = image.size

            html = '<img src="data:image/jpeg;base64,{}">'.format
            resolution, width, height = 20, 10, (height / width * 10.5)

        iframe = folium.IFrame(html(encoded.decode(
            'UTF-8')), width=(resolution*width) + 20, height=(resolution*height) + 20)
        popup = folium.Popup(iframe, min_width=150, min_height=150)
        icon = folium.Icon(color="blue", icon="ok")
        tooltip = dates[imagename]
        folium.Marker(location=coordinates[imagename], popup=popup, tooltip=tooltip, icon=icon).add_to(marker_cluster)

    m.save(f"{folder_name}_Map.html")


make_map()
