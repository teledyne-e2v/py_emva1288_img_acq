# py_emva1288_img_acq
Python script to get images from OPTIMOM 2M for EMVA1288 image analysis

## Install V4L2 tools
```
sudo apt install v4l-utils
```

## Install pip2 for python2 package installation
```
sudo apt update
sudo apt install python-pip
```

## Install v4l2 package for python 2.7.17 (preinstalled in the Jetson image)
```
pip2 install v4l2
```

## Run the scripts with commands:
```
git clone https://github.com/teledyne-e2v/py_emva1288_img_acq
cd py_emva1288_img_acq 
```

### in dark condition (no light)
```
python image_EMVA1288_dark_spatial.py
python image_EMVA1288_dark_temporal.py
```

### in light condition (light on - fixed intensity - monochromatic)
```
python image_EMVA1288_light_spatial.py
python image_EMVA1288_light_temporal.py
```

## IMPORTANT NOTICE
Check the parameters values required for each scripts before executing
* setup the exposure time needed to obtain mid-dynamic image: **exposure_vsat_2**
* setup the exposure time needed to obtain fully saturated image: **exposure_max**

