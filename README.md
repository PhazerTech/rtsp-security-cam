# rtsp-security-cam
Python RTSP security camera app with motion detection features.  Lightweight and can run on a Raspberry Pi 4.

## Getting Started

To get started, you'll first need to clone the repository:

```bash
git clone https://github.com/PhazerTech/rtsp-security-cam
```

Next, install the required dependencies:

```bash
pip3 install -r requirements.txt
```

## Running the App

The only argument required to run the app is the --stream parameter followed by the RTSP address of your video stream.

To run it with default settings, enter the following and replace 'ip:port/stream-name' with your stream's address.

```bash
cd rtsp-security-cam
python3 rtsp-security-cam.py --stream rtsp://ip:port/stream-name
```

To open a window where you can view the stream while the program is running, include the --monitor parameter.
Only use this if you have a monitor connected (no Raspberry Pi SSH sessions).

```bash
python3 rtsp-security-cam.py --stream rtsp://ip:port/stream-name --monitor
```

## Advanced Settings

If the default motion detection settings are providing poor results, additional arguments can be provided to tweak the sensitivity of the motion detection algorithm and to enable testing mode
that helps to find the optimal threshold value.

--threshold - Threshold value determines the amount of motion required to trigger a recording. Higher values decrease sensitivity to help reduce false positives. Default is 350. Max is 10000.

--start_frames - Number of consecutive frames with motion activity required to start a recording. This value will depend on your stream's FPS and desired sensitivity. Raising this value might help if there's too many false positive recordings. Default is 3. Max is 30.

--tail_length - Number of seconds without motion activity required to stop a recording. Raising this value might help if the recordings are stopping too early. Default is 8. Max is 30.

--no_auto_delete - Recordings that have a total length close to the tail_length value are assumed to be false positives and are auto-deleted by default. Entering this argument disables the auto-delete feature.

--testing - Testing mode disables recordings and prints out the motion value for each frame if greater than threshold. Helps fine tune the threshold value.

--frame_click - Allows user to advance frames one by one by pressing any key. For use with testing mode on video files, not live streams, so make sure to provide a video file instead of an RTSP address for the --stream argument if using this feature.

Check out my video about this app on my YouTube channel for more details: https://www.youtube.com/channel/phazertech

## Contact

If you have any questions feel free to contact me at https://phazertech.com/contact.html

## Copyright

Copyright (c) 2023, Phazer Tech

This source code is licensed under the Affero GPL. See the LICENSE file for details.
