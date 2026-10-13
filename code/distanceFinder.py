#from PIL import ImageGrab
#from PIL import Image
import numpy as np
import math
import pyautogui
import configparser
from display_support import MAP_CAPTURE_PROFILES, find_game_client_rect, get_game_capture_region

def read_config(name):
    config = configparser.ConfigParser()
    config.read(name, encoding='utf-8')
    resolution = config.get("Combinations", "Resolution")
    return resolution

def checkDistance(model, queue1):
  
        ######################################################################
        resolution = read_config("code/buttons.ini")

        client_rect = find_game_client_rect()
        if client_rect is None:
            queue1.put(['errorGameWindow'])
            return

        try:
            region = get_game_capture_region(client_rect, resolution)
        except ValueError as error:
            print(error)
            queue1.put(['errorResolution'])
            return

        profile = MAP_CAPTURE_PROFILES[resolution]
        size = profile[4]
        sizeReal = profile[5]
        
        sizeK = size/sizeReal
        
        screen = pyautogui.screenshot('Map.png', region=region)
        #screenScale = ImageGrab.grab(bbox =(1745, 902, 1905, 1062))
         
        #screen.save("karta.png")
        
        resizing = size != sizeReal
        
        if resizing:
            screen = screen.resize((size, size))
        
        #im1 = Image.fromarray(im1)
        #im1.save("karka.png")

        #screen = pyautogui.screenshot('karta.png', region=(1472,632, 448, 448))

        ######################################################################


        ####
        file = open('code/scale.txt', 'r')
        scale = file.read()
        file.close()
        if scale == "" or scale == "0":
            scale = "5"
            file = open('code/scale.txt', 'w')
            file.write(scale)
            file.close()
        scale = float(scale)
        #numberResults = modelNumber(screenScale, size=160)
        #print(numberResults.xyxy[0])
        #numberList = numberResults.xyxy[0].numpy().tolist()
        #if numberList == []:
        #    showErrorNumber(label, root)
        #    return
        #numberList.sort()
        #scale = ""
        #for i in numberList:
        #   scale += str(int(i[5]))
        #scale = int(scale)
        ###




        ######################################################################
        #Определяем позицию игрока и метки
        
        results = model(screen, 480)
        tankArrow = 0
        yellowMarker = 0
        
        for i in results.xyxy[0]:
            classD = int(i[5])
            if (classD == 0 or classD == 1) and type(tankArrow) is int:
                tankArrow = i.numpy(force=True)
            if classD == 2 and type(yellowMarker) is int:
                yellowMarker = i.numpy(force=True)               
        
        if type(tankArrow) is int:
            return showErrorArrow(screen, queue1)
            
        if type(yellowMarker) is int:
            return showErrorMarker(screen, queue1)

        tankPosition = ((tankArrow[2]+tankArrow[0])/2, (tankArrow[3]+tankArrow[1])/2)            
        
        if resizing:
            tankPosition = (tankPosition[0]/sizeK, tankPosition[1]/sizeK)
            
        print("Tank position",tankPosition)
        
        markerPosition = ((yellowMarker[2]+yellowMarker[0])/2, (yellowMarker[3]+yellowMarker[1])/2)
        
        if resizing:
            markerPosition = (markerPosition[0]/sizeK, markerPosition[1]/sizeK)
        
        print("Yellow marker center",markerPosition)
        
        #print(arrowResults.xyxy[0])                                   
        #      xmin    ymin    xmax   ymax  confidence  class    name
        # 0  749.50   43.50  1148.0  704.5    0.874023      0   arrow
        
        #arrowsConfidences = arrowResults.xyxy[0][:, -2].numpy().tolist()        
        #arrowsCoords = arrowResults.xyxy[0][:, :-2].numpy()
  

        ######################################################################




        #катеты по двум точкам
        katet1 = markerPosition[0] - tankPosition[0]
        katet2 = tankPosition[1] - markerPosition[1]


        ######################################################################
        #дистанция между двумя точками в пикселях
        gipotenuza = np.hypot(katet1, katet2)
        ######################################################################
        
        angel = 2*math.pi + psi if (psi := math.atan2(katet1, katet2)) < 0.0 else psi
        angel = math.degrees(angel)
            
        #азимут найден
        ######################################################################
      
        #получаем дистанцию в метрах
        distance = gipotenuza*scale
        print("Azimuth",angel)
        print("Distance",distance)
        
        queue1.put(['printResults', f'{round(distance)}', f'{round(angel,1)}'])
        return
        ######################################################################
def showErrorArrow(screen, queue1):
    file = open('not_found/your_tank_not_found/number.txt', 'r')
    number = file.read()
    if number == "":
        number = "0"
    number = int(number)
    file.close()
    file = open('not_found/your_tank_not_found/number.txt', 'w')    
    screen.save(f'not_found/your_tank_not_found/screen{number}.png')
    number+=1
    file.write(str(number))
    file.close()
    queue1.put(['errorArrow'])
    return

def showErrorMarker(screen, queue1):
    file = open('not_found/mark_not_found/number.txt', 'r')
    number = file.read()
    if number == "":
        number = "0"
    number = int(number)
    file.close()
    file = open('not_found/mark_not_found/number.txt', 'w')    
    screen.save(f'not_found/mark_not_found/screen{number}.png')
    number+=1  
    file.write(str(number))
    file.close()
    queue1.put(['errorMarker'])
    return