import pyfirmata
import time
from pynput.keyboard import Key, Controller
keyboard = Controller()

board = pyfirmata.Arduino("COM2")
it=pyfirmata.util.Iterator(board)
it.start()

#defining sensor pins and input type
sensor1 = board.get_pin('d:3:i')
sensor2 = board.get_pin('d:5:i')
sensor3 = board.get_pin('d:6:i')
sensor4 = board.get_pin('d:9:i')

def sensor1_triggered():
    if sensor1.read() == False:
        return True
    
def sensor2_triggered():
    if sensor2.read() == False:
        return True
    
def sensor3_triggered():
    if sensor3.read() == False:
        return True

def sensor4_triggered():
    if sensor4.read() == False:
        return True
    
sensor_key_map = {
    sensor1_triggered: Key.left,
    sensor2_triggered: Key.up,
    sensor3_triggered: Key.down,
    sensor4_triggered: Key.right,
    # Add more sensors and keys as needed
}


while True:

    for sensor_triggered, key in sensor_key_map.items():
        if sensor_triggered():
            keyboard.press(key)  # press key
            keyboard.release(key)  # release key
    time.sleep(0.01)  # sleep for a bit to avoid overwhelming the CPU

    #If first sensor is trigger press left otherwise release
    digital_value1 = sensor1.read()
    #print('Sensor 1:', digital_value1)
    if digital_value1 == False:
        keyboard.press(Key.left)


    # #If Second sensor is trigger press up otherwise release
    # digital_value2 = sensor2.read()
    # #print('Sensor 2:', digital_value2)
    # if digital_value2 == False:
    #     keyboard.press(Key.up)
    # else:
    #     keyboard.release(Key.up)


    # #If third sensor is trigger press down otherwise release
    # digital_value3 = sensor3.read()
    # #print('Sensor 3:', digital_value3)
    # if digital_value3 == False:
    #     keyboard.press(Key.down)
    # else:
    #     keyboard.release(Key.down)

    # #If fourth sensor is trigger press right otherwise release
    # digital_value4 = sensor4.read()
    # #print('Sensor 4:', digital_value4)
    # if digital_value4 == False:
    #     keyboard.press(Key.right)
    # else:
    #     keyboard.release(Key.right)

    

