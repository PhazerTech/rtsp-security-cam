# Copyright (c) 2023, Phazer Tech
# All rights reserved.

# View the GNU AFFERO license found in the
# LICENSE file in the root directory.

import time
import os
import cv2
import queue
import threading
import numpy as np
from datetime import datetime
from ffmpeg import FFmpeg
from skimage.metrics import mean_squared_error as ssim
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, BooleanOptionalAction
from sshkeyboard import listen_keyboard, stop_listening

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("--stream", type=str, help="RTSP address of video stream.")
parser.add_argument('--monitor', default=False, action=BooleanOptionalAction, help="View the live stream. If no monitor is connected then leave this disabled (no Raspberry Pi SSH sessions).")
parser.add_argument("--threshold", default=350, type=int, choices=range(1,10000), help="Determines the amount of motion required to start recording. Higher values decrease sensitivity to help reduce false positives. Default 350, max 10000.")
parser.add_argument("--start_frames", default=3, type=int, choices=range(1,30), help="Number of consecutive frames with motion required to start recording. Raising this might help if there's too many false positive recordings, especially with a high frame rate stream of 60 FPS. Default 3, max 30.")
parser.add_argument("--tail_length", default=8, type=int, choices=range(1,30), help="Number of seconds without motion required to stop recording. Raise this value if recordings are stopping too early. Default 8, max 30.")
parser.add_argument("--auto_delete", default=False, action=BooleanOptionalAction, help="Enables auto-delete feature. Recordings that have total length equal to the tail_length value (seconds) are assumed to be false positives and are auto-deleted.")
parser.add_argument('--testing', default=False, action=BooleanOptionalAction, help="Testing mode disables recordings and prints out the motion value for each frame if greater than threshold. Helps fine tune the threshold value.")
parser.add_argument('--frame_click', default=False, action=BooleanOptionalAction, help="Allows user to advance frames one by one by pressing any key. For use with testing mode on video files, not live streams, so set a video file instead of an RTSP address for the --stream argument.")
args = vars(parser.parse_args())

rtsp_stream = args["stream"]
monitor = args["monitor"]
thresh = args["threshold"]
start_frames = args["start_frames"]
tail_length = args["tail_length"]
auto_delete = args["auto_delete"]
testing = args["testing"]
frame_click = args["frame_click"]
if frame_click:
    testing = True
    monitor = True
    print("frame_click enabled. Press any key to advance the frame by one, or hold down the key to advance faster. Make sure the video window is selected, not the terminal, when advancing frames.")

# set up other internal variables
loop = True
cap = cv2.VideoCapture(rtsp_stream)
fps = cap.get(cv2.CAP_PROP_FPS)
period = 1/fps
tail_length = tail_length*fps
recording = False
ffmpeg_copy = 0
activity_count = 0
ret, img = cap.read()
if img.shape[1]/img.shape[0] > 1.55:
    res = (256,144)
else:
    res = (216,162)
blank = np.zeros((res[1],res[0]), np.uint8)
resized_frame = cv2.resize(img, res)
gray_frame = cv2.cvtColor(resized_frame,cv2.COLOR_BGR2GRAY)
old_frame = cv2.GaussianBlur(gray_frame, (5,5), 0)
if monitor:
    cv2.namedWindow(rtsp_stream, cv2.WINDOW_NORMAL)

q = queue.Queue()
# thread for receiving the stream's frames so they can be processed
def receive_frames():
    if cap.isOpened():
        ret, frame = cap.read()
    while ret and loop:
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                q.put(frame)

# Record the stream when object is detected
def start_ffmpeg():
    try:
        ffmpeg_copy.execute()
    except:
        print("Issue recording the stream. Trying again.")
        time.sleep(1)
        ffmpeg_copy.execute()

# functions for detecting key presses
def press(key):
    global loop
    if key == 'q':
        loop = False

def input_keyboard():
    listen_keyboard(
        on_press=press,
    )

def timer():
    delay = False
    period = 1
    now = datetime.now()
    now_time = now.time()
    start1 = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    start2 = now_time.replace(hour=0, minute=0, second=1, microsecond=10000)
    start_t=time.time()
    while loop:
        now = datetime.now()
        now_time = now.time()
        if(now_time>=start1 and now_time<=start2):
            day_num = now.weekday()
            if day_num == 0: print("Monday "+now.strftime('%m-%d-%Y'))
            elif day_num == 1: print("Tuesday "+now.strftime('%m-%d-%Y'))
            elif day_num == 2: print("Wednesday "+now.strftime('%m-%d-%Y'))
            elif day_num == 3: print("Thursday "+now.strftime('%m-%d-%Y'))
            elif day_num == 4: print("Friday "+now.strftime('%m-%d-%Y'))
            elif day_num == 5: print("Saturday "+now.strftime('%m-%d-%Y'))
            elif day_num == 6: print("Sunday "+now.strftime('%m-%d-%Y'))
            delay = True
        time.sleep(period - ((time.time() - start_t) % period))
        if delay:
            delay = False
            time.sleep(period - ((time.time() - start_t) % period))

# start the background threads
receive_thread = threading.Thread(target=receive_frames)
receive_thread.start()
keyboard_thread = threading.Thread(target=input_keyboard)
keyboard_thread.start()
timer_thread = threading.Thread(target=timer)
timer_thread.start()

# main loop
while loop:
    if q.empty() != True:
        img = q.get()

        # resize image, make it grayscale, then blur it
        resized_frame = cv2.resize(img, res)
        gray_frame = cv2.cvtColor(resized_frame,cv2.COLOR_BGR2GRAY)
        final_frame = cv2.GaussianBlur(gray_frame, (5,5), 0)

        # calculate difference between current and previous frame, then get ssim value
        diff = cv2.absdiff(final_frame, old_frame)
        result = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)[1]
        ssim_val = int(ssim(result,blank))
        old_frame = final_frame

        # print value for testing mode
        if testing and ssim_val > thresh:
            print("motion: "+ str(ssim_val))

        # count the number of frames where the ssim value exceeds the threshold value, and begin
        # recording if the number of frames exceeds start_frames value
        if not recording:
            if ssim_val > thresh:
                activity_count += 1
                if activity_count >= start_frames:
                    filedate = datetime.now().strftime('%H-%M-%S')
                    if not testing:
                        folderdate = datetime.now().strftime('%Y-%m-%d')
                        if not os.path.isdir(folderdate):
                            os.mkdir(folderdate)
                        filename = '%s/%s.mkv' % (folderdate,filedate)
                        ffmpeg_copy = (
                            FFmpeg()
                            .option("y")
                            .input(
                                rtsp_stream,
                                rtsp_transport="tcp",
                                rtsp_flags="prefer_tcp",
                            )
                            .output(filename, vcodec="copy", acodec="copy")
                        )
                        ffmpeg_thread = threading.Thread(target=start_ffmpeg)
                        ffmpeg_thread.start()
                        print(filedate + " recording started")
                    else:
                        print(filedate + " recording started - Testing mode")
                    recording = True
                    activity_count = 0
            else:
                activity_count = 0

        # if already recording, count the number of frames where there's no motion activity and stop
        # recording if it exceeds the tail_length value
        else:
            if ssim_val < thresh:
                activity_count += 1
                if activity_count >= tail_length:
                    filedate = datetime.now().strftime('%H-%M-%S')
                    if not testing:
                        ffmpeg_copy.terminate()
                        ffmpeg_thread.join()
                        ffmpeg_copy = 0
                        print(filedate + " recording stopped")
                        # delete recording if total length is equal to the tail_length value,
                        # indicating a false positive
                        if auto_delete:
                            recorded_file = cv2.VideoCapture(filename)
                            recorded_frames = recorded_file.get(cv2.CAP_PROP_FRAME_COUNT)
                            if recorded_frames < tail_length + (fps/2) and os.path.isfile(filename):
                                os.remove(filename)
                                print(filename + " was auto-deleted")
                    else:
                        print(filedate + " recording stopped - Testing mode")
                    recording = False
                    activity_count = 0
            else:
                activity_count = 0

        # monitor the stream
        if monitor:
            cv2.imshow(rtsp_stream, img)
            if frame_click:
                cv_key = cv2.waitKey(0) & 0xFF
                if cv_key == ord("q"):
                    loop = False
                if cv_key == ord("n"):
                    continue
            else:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    loop = False
    else:
        time.sleep(period/2)

# gracefully end threads
stop_listening()
if ffmpeg_copy:
    ffmpeg_copy.terminate()
    ffmpeg_thread.join()
receive_thread.join()
keyboard_thread.join()
timer_thread.join()
cv2.destroyAllWindows()
print("Exiting")
