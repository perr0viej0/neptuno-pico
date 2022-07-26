# Imports necesarios
from machine import Pin, ADC, I2C  # control de pines, adc y lcd i2c
from time import sleep  # control de tiempo
from lcd_api import LcdApi  # lcd_api
from I2C_LCD import I2cLcd  # i2c_lcd, ambas librerias trabajan juntas
from hcsr04 import HCSR04  # control modulo infrasonido hcsr04 (medicion distancia)
from _thread import start_new_thread as nuevo_hilo  # ejecucion multihilo
from DHT22 import DHT22

######## fin imports#########

#########declaracion de variables####################
adc = ADC(26)  # Set ADC pin 26
I2C_ADDR = 0x27  # direccion del lcd
I2C_NUM_ROWS = 2  # filas
I2C_NUM_COLS = 16  # columnas
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)  # identificando dispositivo i2c y sus pines y freq
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)  # creando objeto lcd con parametros anteriores
SR = HCSR04(19, 18)  # identificando pines trig y echo del modulo hcsr04
grados = bytearray([0x02, 0x05, 0x05, 0x02, 0x00, 0x00, 0x00, 0x00])  # bytearray del simbolo de grados
lcd.custom_char(0, grados)  # pasando el bytearray a lcd
dht_sensor = DHT22(Pin(15, Pin.OUT), dht11=False)
sensor_awa = Pin(16, Pin.IN)
led_alarma = Pin(25, Pin.OUT)
rele = Pin(22, Pin.OUT)
led_alarma.value(0)
rele.value(1)


######################Fin declaracion de variables####################

########## FUNCIONES #########################

def riega():
    while True:  # esta sera la funcion encargada de medir humedad y decidir si regar o no teniendo en cuenta nivel de agua del deposito
        if sensor_awa.value() == 1:
            led_alarma.value(0)
            rele.value(0)
            print("Regando.....")  # la definimos en una funcion aparte para lanzarla en otro core
            sleep(1)
            rele.value(1)
        else:
            print("SIN AGUA EN DEPOSITO")  # por eso utilizamos la libreria _thread, para tener un bucle en un hilo
            led_alarma.value(1)
            break

        sleep(10)


def intro():
    lcd.putstr("  NEPTUNO v1.0  ")  # Presentacion y esperar 2 seg
    lcd.putstr("-----by APR-----")
    sleep(2)
    lcd.move_to(0, 1)
    lcd.putstr("                ")  # borrar la linea de abajo


def mainloop():
    if led_alarma.value() == 1:
        lcd.display_on()
        lcd.backlight_on()
        lcd.move_to(0, 0)
        lcd.putstr("-----ALARMA-----")
        lcd.putstr("----SIN AGUA----")
    else:
        distancia = SR.distanceCM()  # hacemos get de la distancia y lo guardamos en una variable
        if distancia < 10:  # si distancia menor que 10:
            lcd.display_on()  # encendemos el lcd
            lcd.backlight_on()  # y tambien el backlight
            T, H = dht_sensor.read()
            lcd.move_to(0, 0)  # mover cursor a pos inicial
            lcd.putstr("Temp: %0.2f" % T)  # escribir en lcd
            lcd.putstr(chr(0) + "C    ")
            lcd.move_to(0, 1)  # mover a pos inicial linea abajo
            lcd.putstr("Hum.Rel.: %0.2f" % H)  # escribir temp en lcd
            lcd.putstr("%")  # escribir customchar 0  que creamos con el bytearray (simbolo grados)
            lcd.move_to(0, 0)
            sleep(2)


        else:
            sleep(.7)  # esperar 700ms
            lcd.backlight_off()  # apagar backlight
            lcd.display_off()  # apagar lcd
            # print('Distance: ',SR.distanceCM(),'cm')   # print de debugging en codigo final no estará


#########FIN FUNCIONES##########################


#############---MAIN CODE---##################################

intro()  # intro lcd

try:
    nuevo_hilo(riega, ())  # iniciamos hilo secundario para check humedad y riego

    while True:  # bucle principal
        mainloop()
except:
    pass

