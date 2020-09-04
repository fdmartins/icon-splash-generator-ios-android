import xmltodict
import os
import sys
import logging
import subprocess
import optparse

android_icon_density_dict = {
    'ldpi':(36,36),
    'mdpi':(48,48),
    'hdpi':(72,72),
    'xhdpi':(96,96),
    'xxhdpi':(144,144),
    'xxxhdpi':(192,192),
}

android_splash_density_dict = { # valores para port para land eh soh inverter.
    'ldpi':(240,320),
    'mdpi':(320,480),
    'hdpi':(480,800),
    'xhdpi':(720,1280),
    'xxhdpi':(960,1600),
    'xxxhdpi':(1280,1920),
}


def readConfigXml(path="../config.xml"):
    icons = {'ios':[], 'android':[]}
    splashs = {'ios':[], 'android':[]}

    with open(path) as fd:
        doc = xmltodict.parse(fd.read())
        
        for platform in doc['widget']['platform']:
            platform_name = platform['@name']
            #print("====", platform_name, "=====")
            for icon in platform['icon']:
                #print(icon)
                icon = dict(icon)
                if "@density" in icon:
                    size = android_icon_density_dict[icon["@density"]]
                    icon.setdefault('@width' , size[1])
                    icon.setdefault('@height',size[0])
                        

                icons[platform_name].append(icon)

            for splash in platform['splash']:
                
                splash = dict(splash)
                if "@density" in splash:
                    if 'port-' in splash["@density"]:
                        #print(splash)
                        size = android_splash_density_dict[splash["@density"].replace('port-','')]
                        #print(size)
                        splash['@width'] = size[0]
                        splash['@height'] = size[1]
                        #print(splash)
                    elif 'land-' in splash["@density"]:
                        #print(splash)
                        size = android_splash_density_dict[splash["@density"].replace('land-','')]
                        #print(size)
                        splash['@width'] = size[1]
                        splash['@height'] = size[0]
                        #print(splash)
                    else:
                        # formato sem land nem port. precisamos idenitificar se eh land ou port pelo name.
                        #print(splash)
                        size = android_splash_density_dict[splash["@density"]]
                        if 'port-' in splash["@src"]:
                            splash['@width'] = size[0]
                            splash['@height'] = size[1]
                        if 'land-' in splash["@src"]:
                            splash['@width'] = size[1]
                            splash['@height'] = size[0]
                        #print(splash)
                
                splashs[platform_name].append(splash)

    return icons,splashs


def verify_dependencies():
        # http://stackoverflow.com/a/11270665
        try:
            from subprocess import DEVNULL # py3k
        except ImportError:
            DEVNULL = open(os.devnull, 'wb')

        # try to run convert command - if it fails, tell user and bail
        if subprocess.call(
                'convert -version',
                stdout=DEVNULL,
                stderr=DEVNULL,
                shell=True):
            logging.error("could not find ImageMagick " +
                    "`convert` method. Please install with - brew install imagemagick " +
                    "ImageMagick and/or add it to the path");
            sys.exit(1)

def resize( source, destination, width, height, quality=90, background=None):
    #print("- - Creating (",width, ",",height,")")

    # TODO: support other conversion types if desired (PIL?)
    _resize_imagemagick(source, destination, width, height, quality, background)

def _resize_imagemagick(source, destination, width, height, quality=90, background=None):
    # use imagemagick's convert method

    #raw_command = 'convert -background {background} "{source}" -resize {bigger}x{bigger} -gravity center -extent {width}x{height} "{destination}"'
    
    raw_command = 'convert  -background none "{source}" -resize {width}x{height}^ -gravity center -extent  {width}x{height} -quality {quality} "{destination}"'
    
    

    command = raw_command.format(
        source=source,
        destination=destination,
        width=width,
        height=height,
        bigger=max(width, height),
        background=background or 'none',
        quality=quality
    )

    #print(command)

    logging.debug(command)
    subprocess.call(command, shell=True)

    subprocess.call("./pngquant --quality=0-"+str(quality)+" -f --ext .png  '"+destination+"'",shell=True)

def formatFileName(path):
    paths = path.split('/')
    return paths[len(paths)-1]

def generateFiles(platform, icons, splashs, path="../resources/", quality=90, adaptativeIcon=False):

    splash_file = path+"splash.png"

    dest_path = path#"./test/"

    if not os.path.exists(dest_path+platform):
        os.mkdir(dest_path+platform)


    for icon in icons[platform]:
        if not os.path.exists(dest_path+platform+"/icon"):
            os.mkdir(dest_path+platform+"/icon")
            print("Directory " , dest_path+platform ,  " Created ")

    
        if adaptativeIcon:
            dest_file_foreground = dest_path+platform+"/icon/" + formatFileName(icon["@foreground"])
            dest_file_background = dest_path+platform+"/icon/" + formatFileName(icon["@background"])

            print("ICON - Gerando...", dest_file_foreground)
            print("ICON - Gerando...", dest_file_background)
            resize(path+"icon_foreground.png", dest_file_foreground, icon['@width'], icon['@height'], quality=quality)
            resize(path+"icon_background.png", dest_file_background, icon['@width'], icon['@height'], quality=quality)
        else:
            dest_file = dest_path+platform+"/icon/" + formatFileName(icon["@src"])
            
            print("ICON - Gerando...", dest_file)
            resize(path+"icon_foreground.png", dest_file, icon['@width'], icon['@height'], quality=quality)
        #exit()

    for splash in splashs[platform]:
        
        if not os.path.exists(dest_path+platform+"/splash"):
            os.mkdir(dest_path+platform+"/splash")
            print("Directory " , dest_path+platform ,  " Created ")

        dest_file = dest_path+platform+"/splash/" + formatFileName(splash["@src"])
        
        print("SPLASH - Gerando...", dest_file)

        resize(splash_file, dest_file, splash['@width'], splash['@height'], quality=quality)
        #exit()


# brew install imagemagick
verify_dependencies()

# lemos o xml.
icons,splashs = readConfigXml(path="../config.xml")
#for icon in splashs['ios']:
#    print(icon)

print("=== ANDROID ===")
#colocar em path icon_foreground.png e icon_background.png para adaptativeIcons...para nao adaptativos, usar apenas icon.png
generateFiles('android', icons, splashs, path="../resources/",quality=40, adaptativeIcon=True)

print("=== IOS ===")
generateFiles('ios', icons, splashs, path="../resources/",quality=40)