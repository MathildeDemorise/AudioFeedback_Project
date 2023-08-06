import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import cv2
import mediapipe as mp
import pyttsx3

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


'''
First interface I've created just to see any angle 
you can chose directly on the interface
'''



ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

window = ctk.CTk()
window.title("On live")


# Configuration the size of the interface to match the screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()   
desired_height = int(screen_height*0.9)
window.geometry(f"{screen_width}x{desired_height}+{0}+{0}")
frame_height = 0.95 * desired_height
frame_left_width = 0.25 * screen_width
frame_right_width = 0.67 * screen_width

## 

frame_1_left = ctk.CTkFrame(window, width=frame_left_width, height = frame_height)
frame_1_left.grid(row=0, column=0, rowspan=4, sticky="nsew",padx=20, pady=20)
frame_1_left.grid_propagate(False)

frame_1 = ctk.CTkFrame(window, width=frame_right_width, height = frame_height)
frame_1.grid(row=0, column=1, rowspan=4, sticky="nsew",padx=20, pady=20)
frame_1.grid_propagate(False)


##
state = 'on'

list_of_data_angle=[]
file_angle=pd.read_excel('Features.xlsx',header=None, sheet_name='Angle')
row,col = file_angle.shape
for i in range (1, row):
    list_of_data_angle.append(file_angle.iloc[i,0])

def select_angle(event):
    global selected_angle
    selected_angle = window.combobox_angle.get()

def get_webcam():

    def get_points_of_interest(file):

        selected_joint1 = []
        selected_joint2 = []
        selected_joint3 = []
                        
        for i,angle in enumerate(list_of_data_angle):
            
            if selected_angle==angle:
                selected_joint1=file.iloc[i+1,1]
                selected_joint2=file.iloc[i+1,2]
                selected_joint3=file.iloc[i+1,3]

        return selected_joint1, selected_joint2, selected_joint3
                
    angle1, angle2, angle3 = get_points_of_interest(file_angle)
    
    def calculate_angle(a,b,c):
        a = np.array(a) # First
        b = np.array(b) # Mid
        c = np.array(c) # End
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle >180.0:
            angle = 360-angle
            
        return angle 

    def text_to_speech(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def show_angle_on_live(cap, index1, index2, index3):

        if not hasattr(show_angle_on_live, 'canvas2_created'):
            
            show_angle_on_live.canvas2 = tk.Canvas(frame_1, width=1.45*frame_right_width, height=1.45*frame_height)
            show_angle_on_live.canvas2.grid(row=4, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            show_angle_on_live.canvas2_created = True

        ## Setup mediapipe instance
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                _, frame = cap.read()

                flipped_frame = cv2.flip(frame, 1)
                
                # Recolor image to RGB
                
                image = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
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
                        text_to_speech("Angle is respected")

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

        
    show_angle_on_live(cv2.VideoCapture(0), int(angle1), int(angle2), int(angle3))

def close_webcam():
    global state
    if state == 'on' :
        state = 'off'
        return state
    if state == 'off' :
        state = 'on'
        return state

window.combobox_angle = ctk.CTkComboBox(frame_1_left, values=list_of_data_angle, button_color= 'orange',command=select_angle)
window.combobox_angle.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")

window.show_webcam = ctk.CTkButton(frame_1_left, text="Open the webcam", command=get_webcam)
window.show_webcam.grid(row=2, column=0, padx=20, pady=(10, 10))

window.close_webcam = ctk.CTkButton(frame_1_left, text="Close/Re-open the webcam", command=close_webcam)
window.close_webcam.grid(row=3, column=0, padx=20, pady=(10, 10))

# close the window when we click on the cross

def close_window():
    window.destroy()
    window.quit()
window.protocol("WM_DELETE_WINDOW", close_window)

# Execution of the main loop
window.mainloop()