import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import pyttsx3
import pandas as pd
import numpy as np
import threading
import speech_recognition as sr
import pyttsx3

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


''' 
This interface is the one I use to try to have a feedback on live
'''

class ExerciseApp:

    def __init__(self, window):

        # Create the window with the right size

        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

        self.window = window
        self.window.title("Exercise App On Live")

        self.screen_width = window.winfo_screenwidth()
        self.screen_height = int(0.9*window.winfo_screenheight()) 
        self.desired_height = int(self.screen_height*0.9)
        self.window.geometry(f"{self.screen_width}x{self.screen_height}+{0}+{0}")

        # Create frames

        self.frame_top = ctk.CTkFrame(window, width=int(0.9*self.screen_width), height=int(0.2*self.screen_height))
        self.frame_top.grid(row = 0, column = 0, sticky="nsew", padx=20, pady=20)
        self.frame_top.grid_propagate(False)

        self.frame_middle = ctk.CTkFrame(window, width =int(0.9*self.screen_width), height = int(0.6*self.screen_height))
        self.frame_middle.grid(row=1, column = 0, sticky = 'nsew', padx = 20, pady = 20)
        self.frame_middle.grid_propagate(False)

        self.frame_bottom = ctk.CTkFrame(window, width =int(0.9*self.screen_width), height = int(0.1*self.screen_height))
        self.frame_bottom.grid(row=2, column = 0, sticky = 'nsew', padx = 20, pady = 20)
        self.frame_bottom.grid_propagate(False)

        self.frame_left = ctk.CTkFrame(self.frame_middle, width =int(0.45*self.screen_width), height = int(0.6*self.screen_height))
        self.frame_left.grid(row=0, column = 0, sticky = 'nsew', padx = 20, pady = 20)
        self.frame_left.grid_propagate(False)

        self.frame_right = ctk.CTkFrame(self.frame_middle, width =int(0.45*self.screen_width), height = int(0.6*self.screen_height))
        self.frame_right.grid(row=0, column = 1, sticky = 'nsew', padx = 20, pady = 20)
        self.frame_right.grid_propagate(False)

        # Centered the frame

        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.window.rowconfigure(2, weight=1)

        self.frame_top.columnconfigure(0, weight = 1)
        self.frame_top.columnconfigure(1, weight=1)
        self.frame_top.rowconfigure(0, weight = 1)

        self.frame_middle.rowconfigure(0, weight = 1)

        self.frame_bottom.rowconfigure(0, weight = 1)
        self.frame_bottom.rowconfigure(1, weight=1)
        self.frame_bottom.columnconfigure(1, weight=1)
        self.frame_bottom.columnconfigure(0, weight = 1)

        self.frame_left.columnconfigure(0, weight=1)
        self.frame_left.rowconfigure(0, weight=1)

        self.frame_right.columnconfigure(0, weight=1)
        self.frame_right.rowconfigure(0, weight=1)

        # Global variables
        self.path_exercise = ""
        self.name_exercise = ""

        self.list_of_data_angle = []
        self.names_of_exercices = []

        self.corresponding_angle = ""
        self.corresponding_short_commentary = ""
        self.corresponding_long_commentary = ""

        self.selected_joint1 = []
        self.selected_joint2 = []
        self.selected_joint3 = []

        self.state = 'on'

        self.angle_to_show = ''

        # Usefull files and data
        self.instructions = pd.read_excel("Instructions.xlsx", header=0, sheet_name='Exercices')
        self.sheet_angle = pd.read_excel("Instructions.xlsx", header=0, sheet_name='Angle')

        self.row_1, _ = self.instructions.shape
        self.row_2, _ = self.sheet_angle.shape

        for i in range (0, self.row_1):
            self.names_of_exercices.append(self.instructions.iloc[i,0])
        for i in range(0, self.row_2):
            self.list_of_data_angle.append(self.sheet_angle.iloc[i, 0])


        # Create button

        self.select_exercise_button = ctk.CTkButton(self.frame_top, text="Select the exercise's video", command = self.select_exercise, width= 300, height = 50, anchor='center', font = ("Helvetica", 16, "bold"))
        self.select_exercise_button.grid(row=0, column=0,  padx=20, pady=(10, 10))

        self.start_exercice = ctk.CTkButton(self.frame_top, text="Start the exercise", command = self.start_training, width= 300, height = 50, anchor='center', font = ("Helvetica", 16, "bold"))
        self.start_exercice.grid(row=0, column=1,  padx=20, pady=(10, 10))

        self.close_webcam_button = ctk.CTkButton(self.frame_bottom, text="Stop the session", command = self.close_webcam_or_video)
        self.close_webcam_button.grid(row=1, column=0, padx=20, pady=(10, 10))

        self.label = ctk.CTkLabel(self.frame_bottom, text="")
        self.label.grid(row=1, column=1, padx=20, pady=(10, 10))

        self.window.protocol("WM_DELETE_WINDOW", self.close_window)  # Bind the close function

        self.feedback_detected = False
        self.recognizer = sr.Recognizer()

        self.listening_thread = threading.Thread(target=self.listen_for_feedback)
        self.listening_thread.daemon = True
        self.listening_thread.start()

    # Create functions

    def text_to_speech(self, text):  
        engine = pyttsx3.init()
        engine.setProperty('voice', "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0")
        engine.say(text)
        engine.runAndWait()

    def listen_for_feedback(self):
        with sr.Microphone() as source:
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    self.text = self.recognizer.recognize_google(audio, language="fr-FR")

                    print("You said :", self.text)
                    self.label.configure(text = self.text)

                    if "feedback" in self.text.lower():
                        self.feedback_detected = True

                        angle_to_say = round(self.angle_to_show,0)

                        min = 0.8 * self.corresponding_value
                        max = 1.2 * self.corresponding_value
                        if (angle_to_say > min and angle_to_say < max) :
                            self.text_to_speech('You are in the good position')
                        else :
                            diff = angle_to_say-90

                            if diff > 0 : sign = 'down'
                            else : sign = 'up'

                            self.text_to_speech( 'You have to move ' + str(abs(diff)) + 'degree' + sign)

                    if 'repeat' in self.text.lower():
                        self.text_to_speech(self.corresponding_short_commentary)

                    if 'more precision' in self.text.lower():
                        self.text_to_speech(self.corresponding_long_commentary)
                
                    if 'stop' in self.text.lower():
                        self.state = 'off'

                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    pass
                         
    def select_exercise(self):

        self.path_exercise = filedialog.askopenfilename()
        path_exercise_split = self.path_exercise.split("/")
        name_video = path_exercise_split[len(path_exercise_split) - 1]
        name_video_split = name_video.split("_")
        self.name_exercise = name_video_split[0]
        self.select_exercise_button.configure(text = self.name_exercise)


        for i in range (0, self.row_1):
            if self.name_exercise == self.instructions.iloc[i,0] :
                self.corresponding_angle = self.instructions.iloc[i,1]
                self.corresponding_value = self.instructions.iloc[i,2]
                self.corresponding_short_commentary = self.instructions.iloc[i,3]
                self.corresponding_long_commentary = self.instructions.iloc[i,4]

        file = self.sheet_angle
                            
        for i,angle in enumerate(self.list_of_data_angle):
                
            if self.corresponding_angle==angle:
                self.selected_joint1=file.iloc[i,1]
                self.selected_joint2=file.iloc[i,2]
                self.selected_joint3=file.iloc[i,3]
                    
    def start_training(self):

        video_thread = threading.Thread(target=self.show_video)
        audio_thread = threading.Thread(target=self.text_to_speech_commentary)
        webcam_thread = threading.Thread(target=self.show_angle_on_live)

        audio_thread.start()
        video_thread.start()
        webcam_thread.start()
        
        return
        
    def show_video(self):
        cap = cv2.VideoCapture(self.path_exercise)

        if not hasattr(self, 'canvas1_created'):
            self.canvas1 = ctk.CTkCanvas(self.frame_left, width=int(0.45 * self.screen_width), height=int(0.5 * self.screen_height))
            self.canvas1.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            self.canvas1_created = True
        

        while cap.isOpened():
            ret, frame = cap.read()

            # Vérifier si la lecture de l'image est terminée
            if not ret:
                break

            resized_frame = cv2.resize(frame, (int(0.67 * self.screen_width), int(0.81 * self.screen_height)))

            # Afficher l'image
            photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)))
            self.canvas1.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas1.photo = photo

            self.window.update()  # Utilisez self.window.update() pour mettre à jour la fenêtre Tkinter

            if self.state == 'off':
                break

        cap.release()
        cv2.destroyAllWindows()

    def text_to_speech_commentary(self):
        
        engine = pyttsx3.init()
        engine.setProperty('voice', "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0")
        engine.say(self.corresponding_short_commentary)
        engine.runAndWait()
  
    def show_angle_on_live(self):

        cap = cv2.VideoCapture(0)
        
        if not hasattr(self, 'canvas2_created'):
            
            self.canvas2 = ctk.CTkCanvas(self.frame_right, width =int(0.45*self.screen_width), height = int(0.5*self.screen_height))
            self.canvas2.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            self.canvas2_created = True

        ## Setup mediapipe instance
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                _, frame = cap.read()

                flipped_frame = cv2.flip(frame, 1)
                resized_frame = cv2.resize(flipped_frame, (int(0.67*self.screen_width), int(0.81*self.screen_height)))
                
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
                    point1 = [landmarks[self.selected_joint1].x, landmarks[self.selected_joint1].y]
                    point2 = [landmarks[self.selected_joint2].x, landmarks[self.selected_joint2].y]
                    point3 = [landmarks[self.selected_joint3].x, landmarks[self.selected_joint3].y]
                    
                    a = np.array(point1) # First
                    b = np.array(point2) # Mid
                    c = np.array(point3) # End
                    
                    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
                    angle = np.abs(radians*180.0/np.pi)
                    
                    if angle >180.0:
                        angle = 360-angle
                    
                    # # Calculate angle
                    # angle = calculate_angle(point1, point2, point3)
                    self.angle_to_show = round(angle,1)

                    # Coordinate of the corner
                    corner_coords = (int(image.shape[1] * 0.8), int(image.shape[0] * 0.15))
                    (text_width, text_height), _ = cv2.getTextSize(str(angle), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                    background_start = (corner_coords[0] - 5, corner_coords[1] - text_height - 5)
                    background_end = (corner_coords[0] + text_width + 5, corner_coords[1] + 5)

                    # Draw the background
                    cv2.rectangle(image, background_start, background_end, (255,255,255), -1)
                    
                    # Visualize angle

                    min = 0.8 * self.corresponding_value
                    max = 1.2 * self.corresponding_value
                    
                    if (angle > min and angle < max) : 

                        cv2.putText(image, str(self.angle_to_show), 
                                        corner_coords,  
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        
                    else :
                        cv2.putText(image, str(self.angle_to_show), 
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
                self.canvas2.create_image(0, 0, image=photo, anchor=tk.NW)
                self.canvas2.photo = photo

                window.update()

                if self.state=='off':
                    break


            cap.release()
            cv2.destroyAllWindows()
    
    def close_webcam_or_video(self):
        if self.state == 'on' :
            self.state = 'off'
            return self.state
        if self.state == 'off' :
            self.state = 'on'
            return self.state
    
    def close_window(self):
        # Perform any cleanup tasks here before closing the window
        self.window.destroy()

if __name__ == "__main__":
    window = ctk.CTk()
    app = ExerciseApp(window)
    window.mainloop()
