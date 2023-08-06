import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


'''
This code is just the first I have created to open 
your webcam and show the angle of the left elbow
'''

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


    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1500)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 900)

    window_name = 'Webcam'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # Utilisation de WINDOW_NORMAL pour redimensionner la fenêtre

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
                
                # Visualize angle
                cv2.putText(image, str(angle), 
                            tuple(np.multiply(point2, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                        
            except:
                pass
            
            
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                    )               
            
            cv2.imshow(window_name, image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

show_angle_on_live(cv2.VideoCapture(0), 13,15,17)



