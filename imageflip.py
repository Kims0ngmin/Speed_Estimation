import cv2
from tkinter import Entry, Tk, Label, Button, Scale, HORIZONTAL, Toplevel, filedialog, Frame
from PIL import Image, ImageTk, ImageDraw
import os
import re
import numpy as np

class ImageFlipper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Flipper")

        # Left layout 
        self.left_frame = Frame(root)
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.label = Label(self.left_frame)
        self.label.pack()

        self.button_frame = Frame(self.left_frame)
        self.button_frame.pack()

        self.flip_vert_button = Button(self.button_frame, text="Flip Vertically", command=self.flip_vertically, width=12)
        self.flip_vert_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.flip_horiz_button = Button(self.button_frame, text="Flip Horizontally", command=self.flip_horizontally, width=12)
        self.flip_horiz_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        self.rotate_left_button = Button(self.button_frame, text="Rotate Left", command=self.rotate_left, width=12)
        self.rotate_left_button.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.rotate_right_button = Button(self.button_frame, text="Rotate Right", command=self.rotate_right, width=12)
        self.rotate_right_button.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Right layout (preview window and slider)
        self.right_frame = Frame(root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.preview_label = Label(self.right_frame)
        self.preview_label.pack()

        self.slider = Scale(self.right_frame, from_=0, to=100, orient=HORIZONTAL, resolution=0.5, command=self.update_preview)
        self.slider.pack()

        self.get_dir_l_input_button = Button(self.right_frame, text="Direction setting", command=self.direction, width=12)
        self.get_dir_l_input_button.pack(side="bottom", padx=5, pady=5)

        self.process_button = Button(self.right_frame, text="Process Folder", command=self.process_folder, width=12)
        self.process_button.pack(side="bottom", padx=5, pady=5)

        self.open_button = Button(self.right_frame, text="Open Folder", command=self.open_folder)
        self.open_button.pack(side="bottom", padx=5, pady=5)

        self.close_button = Button(self.right_frame, text="Close", command=lambda: self.close_window(root))
        self.close_button.pack(side="bottom", padx=5, pady=5)
        
        self.folder_path = None
        self.original_img = None 
        self.cv_img = None
        self.flip_codes = []  # store inverted code
        self.rotation_angle = 0  # store the angle of rotation
        self.image_paths = []
        self.max_frame_number = 0

        # Initial Empty Image Settings
        self.initialize_empty_image()

    def initialize_empty_image(self):
        empty_img = Image.new('RGB', (640, 480), color='grey')
        self.cv_img = cv2.cvtColor(np.array(empty_img), cv2.COLOR_RGB2BGR)
        self.display_image()

    def open_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.image_paths = [os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
            if self.image_paths:
                # Find the maximum number by extracting a number from the image file name
                frame_numbers = [float(re.search(r'frame_(\d+\.\d+)', f).group(1)) for f in self.image_paths if re.search(r'frame_(\d+\.\d+)', f)]
                if frame_numbers:
                    self.max_frame_number = max(frame_numbers)
                    self.slider.config(to=self.max_frame_number)

                self.original_img = cv2.imread(self.image_paths[0])
                self.cv_img = self.original_img.copy()
                self.cv_img = cv2.resize(self.cv_img, (640, 480))
                self.display_image()

                # Setting default values for slider and previewing the first frame
                self.slider.set(0)
                self.update_preview(0)

    def process_folder(self):
        if self.folder_path and (self.flip_codes or self.rotation_angle != 0):
            flipped_folder = os.path.join(self.folder_path, 'flipped')
            os.makedirs(flipped_folder, exist_ok=True)
            for img_path in self.image_paths:
                img = cv2.imread(img_path)
                for code in self.flip_codes:
                    img = cv2.flip(img, code)
                if self.rotation_angle != 0:
                    if self.rotation_angle == 90:
                        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    elif self.rotation_angle == -90:
                        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                save_path = os.path.join(flipped_folder, os.path.basename(img_path))
                cv2.imwrite(save_path, img)
            print("Flip and Rotate End")
            self.root.destroy()  # Close the Tkinter window

    def flip_vertically(self):
        self.flip_codes.append(0)
        if self.cv_img is not None:
            self.cv_img = cv2.flip(self.cv_img, 0)
            self.display_image()

    def flip_horizontally(self):
        self.flip_codes.append(1)
        if self.cv_img is not None:
            self.cv_img = cv2.flip(self.cv_img, 1)
            self.display_image()

    def rotate_left(self):
        self.rotation_angle -= 90
        if self.cv_img is not None:
            self.cv_img = cv2.rotate(self.cv_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.display_image()

    def rotate_right(self):
        self.rotation_angle += 90
        if self.cv_img is not None:
            self.cv_img = cv2.rotate(self.cv_img, cv2.ROTATE_90_CLOCKWISE)
            self.display_image()

    def display_image(self):
        rgb_image = cv2.cvtColor(self.cv_img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        imgtk = ImageTk.PhotoImage(image=pil_image)
        self.label.config(image=imgtk)
        self.label.image = imgtk

    def update_preview(self, value):
        if self.folder_path:
            image_name = f"frame_{float(value):.2f}.jpg"
            preview_image_path = os.path.join(self.folder_path, image_name)
            if os.path.exists(preview_image_path):
                preview_img = cv2.imread(preview_image_path)
                preview_img = cv2.resize(preview_img, (320, 240))  # Resize for the preview
                rgb_preview_img = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                pil_preview_image = Image.fromarray(rgb_preview_img)
                imgtk_preview = ImageTk.PhotoImage(image=pil_preview_image)
                self.preview_label.config(image=imgtk_preview)
                self.preview_label.image = imgtk_preview

    def get_input_L2R(self, entry):
        global real_direction
        real_direction = 'L'
        print(real_direction)
        # Close the input window
        entry.master.destroy()

    def get_input_R2L(self, entry):
        global real_direction
        real_direction = 'R'
        print(real_direction)
        # Close the input window
        entry.master.destroy()

    def direction(self):
        # button to hand over the reference length entered in the output text box
        input_window = Toplevel(self.root)
        input_window.title("Get Input")

        entry = Entry(input_window)

        # Add labels and an entry widget for direction input
        label = Label(input_window, text="Input direction:")
        label.pack(pady=10)

        get_dir_l_input_button = Button(input_window, text=" << ", command=lambda: self.get_input_R2L(entry))
        get_dir_l_input_button.pack(side="left")

        get_dir_r_input_button = Button(input_window, text=" >> ", command=lambda: self.get_input_L2R(entry))
        get_dir_r_input_button.pack(side="right")

    def close_window(self, window):
        window.destroy()
        
def deliv_direction():
    global real_direction
    print(real_direction)
    return real_direction

if __name__ == "__main__":
    root = Tk()
    app = ImageFlipper(root)
    root.mainloop()
