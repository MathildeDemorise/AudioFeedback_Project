import speech_recognition as sr
import pyttsx3

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0")
    engine.say(text)
    engine.runAndWait()

angle_test= 140
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say YES to start...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(text)
        if text == 'yes':
            if (angle_test > 85 and angle_test < 95) :
                text_to_speech('You are in the good position')
            else :
                diff = angle_test-90

                if diff > 0 : sign = 'down'
                else : sign = 'up'

                text_to_speech('You have to move ' + str(abs(diff)) + 'degree' + sign)
        else:
            text_to_speech('Repeat please')
            speech_to_text()
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Error requesting results: {0}".format(e))

if __name__ == "__main__":
    speech_to_text()
