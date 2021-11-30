# Multiple-camera-recording
 Record multiple cameras synchronously with OpenCV

## Setup

* Create and activate virtualenv for backend in `venv`: 
  * `python -m venv venv`
  * `source venv/bin/activate` 
* Install packages: `pip install -r requirements.txt`

## Usage


RTSP example

``python main.py --rtsp_cameras rtsp://​<IP>:<PORT>@<USERNAME:<PASSWORD>//h264Preview_01_main, rtsp://​<IP>:<PORT>@<USERNAME:<PASSWORD>//h264Preview_01_main``

RTMP example

``python main.py --rtmp_cameras rtmp://​<IP>/bcs/channel0_​main​.bcs?channel=0&stream=0&user=​<USERNAME>&password=​<PASSWORD>, rtmp://​<IP>/bcs/channel0_​main​.bcs?channel=0&stream=0&user=​<USERNAME>&password=​<PASSWORD>``

USB camera example

``python main.py --usb_cameras /dev/video0,/dev/video1``


Recording can be stopped by pressing ``ESC`` when one of the preview images is in focus. 