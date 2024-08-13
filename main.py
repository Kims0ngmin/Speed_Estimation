import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import cv2
from PIL import Image, ImageTk
import os
from tkinter import scrolledtext
import transformui as t 
import imageflip as i

# Global variables
video_clip = None
canvas = None
video_label = None
root = None
play_button = None
pause_button = None
paused = True
image_filenames = []
subclip_duration = 0
video_load_on = 0
time_start = 0
width1 = 0
rt = 0
current_image_index = 0

def load_video():
    global video_clip, paused, current_time, subclip_duration
    status_label.config(text="Extracting frame from video...")
    file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if file_path:
        video_clip = VideoFileClip(file_path)

        status_label.config(text=f"Loaded video: {file_path}")
        paused = True
        current_time = 0
        subclip_duration = video_clip.duration

        # Create output folder and extract frames
        output_folder = 'extract_video'
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print("Cannot open video file.")
            return

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            time_in_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            time_in_sec = time_in_ms / 1000
            image_name = f"{output_folder}/frame_{time_in_sec:.2f}.jpg"

            cv2.imwrite(image_name, frame)
            frame_count += 1
        
        cap.release()

def resize_frame(frame, width, height):
    resized_frame = cv2.resize(frame, (width, height))
    return resized_frame

def update_frame():
    global current_image_index, images, canvas, paused, img_time, rt
    if not paused and current_image_index < len(images):
        rt = update_imgtime(current_image_index)
        rt = rt.split('_')[1].replace('.jpg', '')
        frame = images[current_image_index]
        frame = resize_frame(frame, 640, 480)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        canvas.image = imgtk
        current_image_index += 1
        root.after(20, update_frame)
    else:
        paused = True

def play_images():
    global video_load_on, folder_path, image_filenames

    if video_load_on == 0:
        global images, current_image_index
        images = []
        image_filenames = []
        current_image_index = 0
        folder_path = filedialog.askdirectory()
        if folder_path:
            for filename in sorted(os.listdir(folder_path)):
                if filename.endswith('.jpg'):
                    img_path = os.path.join(folder_path, filename)
                    img = cv2.imread(img_path)
                    if img is not None:
                        images.append(img)
                        image_filenames.append(filename)
            status_label.config(text=f"Loaded {len(images)} images from: {folder_path}")
    
    video_load_on = 1
    global paused
    paused = False
    update_frame()

def update_imgtime(new_index):
    global img_time, folder_path, image_filenames
    img_time = image_filenames[new_index]
    return img_time

def pause_images():
    global paused, current_image_index, img_time, folder_path, image_filenames
    paused = True
    if 0 <= current_image_index - 1 < len(images):
        # print(f"Paused at image index: {current_image_index - 1}")
        # print(f"Image folder path: {folder_path}")
        # print(f"Current image filename: {image_filenames[current_image_index - 1]}")
        img_time = image_filenames[current_image_index - 1]

    else:
        print("No images loaded or all images have been displayed.")

def next_frame():
    global current_image_index, images, canvas, paused, img_time
    if paused and current_image_index < len(images) - 1:
        current_image_index += 1
        img_time = update_imgtime(current_image_index)
        frame = images[current_image_index]
        frame = resize_frame(frame, 640, 480)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        canvas.image = imgtk
        output_text.insert(tk.END, f"This frame : {img_time.split('_')[1].replace('.jpg', '')} Sec\n")

def prev_frame():
    global current_image_index, images, canvas, paused, img_time
    if paused and current_image_index > 0:
        current_image_index -= 1
        img_time = update_imgtime(current_image_index)
        frame = images[current_image_index]
        frame = resize_frame(frame, 640, 480)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        canvas.image = imgtk
        output_text.insert(tk.END, f"This frame : {img_time.split('_')[1].replace('.jpg', '')} Sec\n")

def transform_action():
    global video_clip
    new_root = tk.Toplevel()
    app = t.ImageEditor(new_root, video_clip)

def speed_est():
    canvas.bind("<Button-1>", onMouse)

def onMouse(event):
    global estimated_length, full_length, img_time, width1, time_start, direction
    full_length = t.deliv_length()
    direction = i.deliv_direction()
    
    print("full_length")
    
    print(full_length)
    width1 = 640
    x = event.x
    y = event.y
    if event:
        canvas.create_oval(x-5, y-5, x+5, y+5, outline="green", width=2)
        if direction == "R":
            estimated_length = full_length - round((x / width1) * full_length,3)
        elif direction == "L":
            estimated_length = round((x / width1) * full_length,3)
        else:
            print("Direction Error")
        img_time = img_time.split('_')[1].replace('.jpg', '')
        estimated_velocity = round((estimated_length / 1000.0) / ((float(img_time) - float(time_start)) / 3600.0), 3)
        output_text.insert(tk.END, f"-> This frame is {img_time} Sec part of the video\n")
        output_text.insert(tk.END, f"-> Length : {estimated_length} meter\n")
        output_text.insert(tk.END, f"-> Velocity : {estimated_velocity} km/h\n< < == == == == == > >\n")

# def center_window(root, width, height):
#     screen_width = root.winfo_screenwidth()
#     screen_height = root.winfo_screenheight()
#     x = int((screen_width / 2) - (width / 2))
#     y = int((screen_height / 2) - (height / 2))
#     root.geometry(f'{width}x{height}+{x}+{y}')

def start_time():
    global time_start, img_time
    img_time = img_time.split('_')[1].replace('.jpg', '')
    time_start = img_time
    output_text.insert(tk.END, f"\n-> Start Time : {time_start} Sec\n")


# Tkinter window creation
root = tk.Tk()
root.title("Simple Video Player")

# # Set window size and center it
# window_width = 950
# window_height = 600
# center_window(root, window_width, window_height)

video_frame = tk.Frame()
# Create video frame
video_frame = tk.Frame()
video_frame.pack(side=tk.LEFT, anchor="n")

status_label = tk.Label(video_frame, text="No video loaded")
status_label.pack(pady=20)

canvas = tk.Canvas(video_frame, width=640, height=480)
canvas.pack(side=tk.LEFT, anchor="nw")

# Create button frames
button_frame = tk.Frame()
button_frame.pack(side=tk.TOP, anchor="nw")

button_frame1 = tk.Frame()
button_frame1.pack(side=tk.TOP, anchor="ne")

text_frame = tk.Frame()
text_frame.pack(side=tk.TOP, anchor="c")

button_frame2 = tk.Frame()
button_frame2.pack(side=tk.BOTTOM, anchor="w")

load_button = tk.Button(button_frame, text="Load Video", command=load_video)
load_button.pack(side=tk.LEFT, anchor="nw")

play_button = tk.Button(button_frame, text="Play Video", command=play_images)
play_button.pack(side=tk.LEFT, anchor="nw")

pause_button = tk.Button(button_frame, text="Pause Video", command=pause_images)
pause_button.pack(side=tk.LEFT, anchor="nw")

next_button = tk.Button(button_frame1, text=" >>", command=next_frame)
next_button.pack(side=tk.RIGHT, anchor="ne", padx=10, pady=1)
prev_button = tk.Button(button_frame1, text="<< ", command=prev_frame)
prev_button.pack(side=tk.RIGHT, anchor="ne", padx=2, pady=1)

startcheck_button = tk.Button(text_frame, text="  Time Start  ", command=start_time)
startcheck_button.pack(side=tk.TOP, anchor="ne", padx=10, pady=1)
output_text = scrolledtext.ScrolledText(text_frame, width=40, height=10, bg="lightgrey", font=("Helvetica", 11), wrap=tk.WORD)
output_text.pack(side=tk.TOP, anchor="center", fill="y", pady=10)

perform_button = tk.Button(button_frame2, text="Transform", command=transform_action)
perform_button.pack(side=tk.LEFT, anchor="w")

perform_button1 = tk.Button(button_frame2, text="Speed Estimation", command=speed_est)
perform_button1.pack(side=tk.LEFT, anchor="w")

# Start Tkinter event loop
root.mainloop()