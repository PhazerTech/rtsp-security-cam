# rtsp-security-cam
Python RTSP security camera app with motion detection features that are based on image processing instead of a dedicated sensor.  All that's required is a camera.  Lightweight and can run on a Raspberry Pi 4.

## Getting Started

To get started, first make sure your system has the required software. If using a Debian/Ubuntu based distro, you can install the required software with the following:

```bash
sudo apt update
sudo apt install gcc python3-dev git
```

Next, clone this repository:

```bash
git clone https://github.com/PhazerTech/rtsp-security-cam
```

Now install the required dependencies with pip:

```bash
cd rtsp-security-cam
pip3 install -r requirements.txt
```

## Running the App

The only argument required to run the app is --stream followed by the RTSP address of your video stream.

To run it with default settings, enter the following and replace 'ip:port/stream-name' with your stream's address.

```bash
python3 rtsp-security-cam.py --stream rtsp://ip:port/stream-name
```

To open a window where you can view the stream while the program is running, include the --monitor argument.
Only use this if you have a monitor connected (no Raspberry Pi SSH sessions).

```bash
python3 rtsp-security-cam.py --stream rtsp://ip:port/stream-name --monitor
```

The program will print a message whenever it starts a recording and ends a recording, and also provide a timestamp.  It will create a folder with the current date for storing that day's recordings. A new folder will be created each day with the current date so that it can be left to run indefinitely.

```bash
$ python3 rtsp-security-cam.py --stream rtsp://192.168.0.156:8554/frontdoor
13-05-09 recording started
13-05-30 recording stopped
14-01-01 recording started
14-01-09 recording stopped
```

## Advanced Settings

If the default motion detection settings are providing poor results, additional arguments can be provided to tweak the sensitivity of the motion detection algorithm and to enable testing mode
that helps to find the optimal threshold value.

--threshold - Threshold value determines the amount of motion required to trigger a recording. Higher values decrease sensitivity to help reduce false positives. Default is 350. Max is 10000.

--start_frames - The number of consecutive frames with motion activity required to start a recording. Raising this value might help if there's too many false positive recordings, especially when using a high frame rate stream greater than 30 FPS. Default is 3. Max is 30.

--tail_length - The number of seconds without motion activity required to stop a recording. Raising this value might help if the recordings are stopping too early. Default is 8. Max is 30.

--auto_delete - Entering this argument enables the auto-delete feature. Recordings that have a total length equal to the tail_length value are assumed to be false positives and are auto-deleted.

--testing - Testing mode disables recordings and prints out the motion value for each frame if greater than threshold. Helpful when fine tuning the threshold value.

--frame_click - Allows the user to advance frames one by one by pressing any key. For use with testing mode on video files, not live streams, so make sure to provide a video file instead of an RTSP address for the --stream argument if using this feature.

Check out my video about this app on my YouTube channel for more details: https://www.youtube.com/channel/phazertech

## Contact

If you have any questions feel free to contact me at https://phazertech.com/contact.html

## Copyright

Copyright (c) 2023, Phazer Tech

This source code is licensed under the Affero GPL. See the LICENSE file for details.
