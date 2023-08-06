import pygame

def read_mp3(path):
    
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pass

    pygame.quit()

vocal_path = "C:\\Users\\33770\\Downloads\\Test1.mp3"
read_mp3(vocal_path)

