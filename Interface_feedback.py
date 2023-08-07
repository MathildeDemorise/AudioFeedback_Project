import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
import cv2
import mediapipe as mp
import pyttsx3
import time
import pygame
import pandas as pd


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


''' 
This interface is the one I use to try to have a feedback on live
'''

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

window = ctk.CTk()
window.title("On live")

# Configuration the size of the interface to match the screen
screen_width = window.winfo_screenwidth()
screen_height = int(0.9*window.winfo_screenheight()) 
desired_height = int(screen_height*0.9)
window.geometry(f"{screen_width}x{screen_height}+{0}+{0}")

#Create frames

frame_top = ctk.CTkFrame(window, width=int(0.9*screen_width), height=int(0.2*screen_height))
frame_top.grid(row = 0, column = 0, sticky="nsew", padx=20, pady=20)
frame_top.grid_propagate(False)

frame_middle = ctk.CTkFrame(window, width =int(0.9*screen_width), height = int(0.6*screen_height))
frame_middle.grid(row=1, column = 0, sticky = 'nsew', padx = 20, pady = 20)
frame_middle.grid_propagate(False)

frame_bottom = ctk.CTkFrame(window, width =int(0.9*screen_width), height = int(0.1*screen_height))
frame_bottom.grid(row=2, column = 0, sticky = 'nsew', padx = 20, pady = 20)
frame_bottom.grid_propagate(False)

frame_left = ctk.CTkFrame(frame_middle, width =int(0.45*screen_width), height = int(0.6*screen_height))
frame_left.grid(row=0, column = 0, sticky = 'nsew', padx = 20, pady = 20)
frame_left.grid_propagate(False)

frame_right = ctk.CTkFrame(frame_middle, width =int(0.45*screen_width), height = int(0.6*screen_height))
frame_right.grid(row=0, column = 1, sticky = 'nsew', padx = 20, pady = 20)
frame_right.grid_propagate(False)

# Centered the frame

window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)

frame_top.columnconfigure(0, weight = 1)
frame_top.columnconfigure(1, weight=1)
frame_top.rowconfigure(0, weight = 1)

frame_middle.rowconfigure(0, weight = 1)

frame_bottom.rowconfigure(0, weight = 1)
frame_bottom.columnconfigure(0, weight = 1)

frame_left.columnconfigure(0, weight=1)
frame_left.rowconfigure(0, weight=1)

frame_right.columnconfigure(0, weight=1)
frame_right.rowconfigure(0, weight=1)

# Global variables

path_exercise = ""
name_exercise = ""
list_of_data_angle = []
state = 'on'

# Usefull files and data

instructions = pd.read_excel("Instructions.xlsx", header=0, sheet_name='Exercices')
sheet_angle = pd.read_excel("Instructions.xlsx", header=0, sheet_name='Angle')

row_1, _ = instructions.shape
row_2, _ = sheet_angle.shape

for i in range(0, row_2):
    list_of_data_angle.append(sheet_angle.iloc[i,0])
    

# Create functions

def select_exercise():

    global path_exercise
    global name_exercise

    path_exercise = filedialog.askopenfilename()
    path_exercise_split = path_exercise.split("/")
    name_video = path_exercise_split[len(path_exercise_split) - 1]
    name_video_split = name_video.split("_")
    name_exercise = name_video_split[0]
    select_exercise_button.configure(text = name_exercise)

def start_training():

    for i in range (0, row_1):
        if name_exercise == instructions.iloc[i,0] :
            corresponding_angle = instructions.iloc[0,1]
            corresponding_commentary = instructions.iloc[0,2]
    
    video = cv2.VideoCapture(path_exercise)

    def show_video(cap, new_width, new_height):

        if not hasattr(show_video, 'canvas1_created'):
            
            show_video.canvas1 = ctk.CTkCanvas(frame_left,  width =int(0.45*screen_width), height = int(0.5*screen_height))
            show_video.canvas1.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            show_video.canvas1_created = True
    
        while cap.isOpened():
            ret, frame = cap.read()
        
            # Vérifier si la lecture de l'image est terminée
            if not ret:
                break
            
            resized_frame = cv2.resize(frame, (new_width, new_height))

                # Afficher l'image
            photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)))
            show_video.canvas1.create_image(0, 0, image=photo, anchor=tk.NW)
            show_video.canvas1.photo = photo
                
            window.update()
                
            if state == 'off': 
                break

        cap.release()
        cv2.destroyAllWindows()

    # show_video(video, int(0.67*screen_width), int(0.81*screen_height))
    
    def text_to_speech(text):
        engine = pyttsx3.init()
        engine.setProperty('voice', "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0")
        engine.say(text)
        engine.runAndWait()

    text_to_speech(corresponding_commentary)

    def calculate_angle(a,b,c):
        a = np.array(a) # First
        b = np.array(b) # Mid
        c = np.array(c) # End
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle >180.0:
            angle = 360-angle
            
        return angle 

    def show_angle_on_live(cap, index1, index2, index3):

        if not hasattr(show_angle_on_live, 'canvas2_created'):
            
            show_angle_on_live.canvas2 = ctk.CTkCanvas(frame_right, width =int(0.45*screen_width), height = int(0.5*screen_height))
            show_angle_on_live.canvas2.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            show_angle_on_live.canvas2_created = True

        ## Setup mediapipe instance
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                _, frame = cap.read()

                flipped_frame = cv2.flip(frame, 1)
                resized_frame = cv2.resize(flipped_frame, (int(0.67*screen_width), int(0.81*screen_height)))
                
                # Recolor image to RGB
                
                image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
            
                # Make detection
                results = pose.process(image)
            
                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
           
                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark
                    
                    # Get coordinates
                    point1 = [landmarks[index1].x, landmarks[index1].y]
                    point2 = [landmarks[index2].x, landmarks[index2].y]
                    point3 = [landmarks[index3].x, landmarks[index3].y]
                    
                    # Calculate angle
                    angle = calculate_angle(point1, point2, point3)
                    angle_to_show = round(angle,1)

                    # Coordinate of the corner
                    corner_coords = (int(image.shape[1] * 0.8), int(image.shape[0] * 0.15))
                    (text_width, text_height), _ = cv2.getTextSize(str(angle), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                    background_start = (corner_coords[0] - 5, corner_coords[1] - text_height - 5)
                    background_end = (corner_coords[0] + text_width + 5, corner_coords[1] + 5)

                    # Draw the background
                    cv2.rectangle(image, background_start, background_end, (255,255,255), -1)
                    
                    # Visualize angle
                    
                    if (angle > 85 and angle < 95) : 
                        # text_to_speech("You reach 90 degree")
                        cv2.putText(image, str(angle_to_show), 
                                        corner_coords,  
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        
                    else :
                        cv2.putText(image, str(angle_to_show), 
                                        corner_coords,  
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    
                except:
                    pass
                
                
                # Render detections
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                        )               


                photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
                show_angle_on_live.canvas2.create_image(0, 0, image=photo, anchor=tk.NW)
                show_angle_on_live.canvas2.photo = photo

                window.update()

                if state=='off':
                    break


            cap.release()
            cv2.destroyAllWindows()

    def get_points_of_interest(file):

        selected_joint1 = []
        selected_joint2 = []
        selected_joint3 = []
                        
        for i,angle in enumerate(list_of_data_angle):
            
            if corresponding_angle==angle:
                selected_joint1=file.iloc[i,1]
                selected_joint2=file.iloc[i,2]
                selected_joint3=file.iloc[i,3]

        return selected_joint1, selected_joint2, selected_joint3
                
    angle1, angle2, angle3 = get_points_of_interest(sheet_angle)

    show_angle_on_live(cv2.VideoCapture(0), angle1, angle2, angle3)

def close_webcam_or_video():
    global state
    if state == 'on' :
        state = 'off'
        return state
    if state == 'off' :
        state = 'on'
        return state
    
# Create button

select_exercise_button = ctk.CTkButton(frame_top, text="Select the exercise's video", command=select_exercise, width= 300, height = 50, anchor='center', font = ("Helvetica", 16, "bold"))
select_exercise_button.grid(row=0, column=0,  padx=20, pady=(10, 10))

start_exercice = ctk.CTkButton(frame_top, text="Start the exercise", command=start_training, width= 300, height = 50, anchor='center', font = ("Helvetica", 16, "bold"))
start_exercice.grid(row=0, column=1,  padx=20, pady=(10, 10))

close_webcam_button = ctk.CTkButton(frame_bottom, text="Stop the session", command=close_webcam_or_video)
close_webcam_button.grid(row=3, column=0, padx=20, pady=(10, 10))

label = ctk.CTkLabel(frame_right, text="")
label.grid(row=0, column=0, padx=20, pady=20)

# Close the window when we click on the cross

def close_window():
    window.destroy()
    window.quit()
window.protocol("WM_DELETE_WINDOW", close_window)

# Execution of the main loop
window.mainloop()