# Imports necesarios
from machine import Pin, ADC, I2C   # control de pines, adc y lcd i2c
import time                         # control de tiempo
import math                         # para el algoritmo del termistor
from lcd_api import LcdApi          # lcd_api
from I2C_LCD import I2cLcd          # i2c_lcd, ambas librerias trabajan juntas
from hcsr04 import HCSR04           # control modulo infrasonido hcsr04 (medicion distancia)
import _thread                      # ejecucion multihilo
######## fin imports#########

#########declaracion de variables####################
adc=ADC(26)         #Set ADC pin 26
I2C_ADDR     = 0x27 #direccion del lcd
I2C_NUM_ROWS = 2 #filas
I2C_NUM_COLS = 16 #columnas
i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=100000) # identificando dispositivo i2c y sus pines y freq
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS) # creando objeto lcd con parametros anteriores
SR = HCSR04(19, 18) # identificando pines trig y echo del modulo hcsr04
grados = bytearray([0x02,0x05,0x05,0x02,0x00,0x00,0x00,0x00]) # bytearray del simbolo de grados
lcd.custom_char(0, grados) # pasando el bytearray a lcd
######################Fin declaracion de variables####################

########## FUNCIONES #########################

def riega():
    cont = 0
    while True:                   # esta sera la funcion encargada de medir humedad y decidir si regar o no teniendo en cuenta nivel de agua del deposito
                                  # la definimos en una funcion aparte para lanzarla en otro core
                                  # por eso utilizamos la libreria _thread, para tener un bucle en un hilo
        print("Mensaje cada 10 seg")
        time.sleep(10)
def intro():
    lcd.putstr("  NEPTUNO v1.0  ")                  # Presentacion y esperar 2 seg
    lcd.putstr("-----by APR-----") 
    time.sleep(2)
    lcd.move_to(0,1)
    lcd.putstr("                ")                  # borrar la linea de abajo


#########FIN FUNCIONES##########################



#############---MAIN CODE---##################################

intro()                                 # intro lcd
_thread.start_new_thread(riega, ())     # iniciamos hilo secundario para check humedad y riego

while True:                         # bucle principal
     distancia = SR.distanceCM() # hacemos get de la distancia y lo guardamos en una variable
     if SR.distanceCM() < 10:     # si distancia menor que 10:
         lcd.display_on()        # encendemos el lcd
         lcd.backlight_on()       # y tambien el backlight
         adcValue = adc.read_u16()  # obtenemos los valores adc del pin 16 (termistor)
         voltage = adcValue / 65535.0 * 3.3  # Algoritmo para encontrar voltaje respecto adc
         Rt = 10 * voltage / (3.3-voltage)
         tempK = (1 / (1 / (273.15+25) + (math.log(Rt/10)) / 3950)) # algoritmo para encontrar temp K en base adc
         tempC = float(tempK - 273.15) # pasamos temp K a temp C
         adcValue = round(adcValue,0)
         print("ADC value:", adcValue, " Voltage: %0.2f"%voltage,
         " Temperature: " + str(tempC) + "C")
         print('Distance: ',distancia,'cm')         # prints de debugging, en el codigo final no estaran
         lcd.move_to(0,0)                           # mover cursor a pos inicial
         lcd.putstr("Distancia: %0.0f"%distancia)   # escribir en lcd
         lcd.putstr("cm")
         lcd.move_to(0,1)                           # mover a pos inicial linea abajo   
         lcd.putstr("Temp: %0.2f"%tempC)            # escribir temp en lcd
         lcd.putstr(chr(0) + "C")                   # escribir customchar 0  que creamos con el bytearray (simbolo grados)
         lcd.move_to(0,0)
         time.sleep(2)
         lcd.putstr("ADC:   %0.0f"%adcValue)
         lcd.putstr("        ")
         lcd.move_to(0,1)
         lcd.putstr("Temp: %0.2f"%tempC)
         lcd.move_to(0,0)
         time.sleep(2)
         lcd.putstr("Volt: %0.4f"%voltage)
         lcd.move_to(0,1)
         time.sleep(2)
         lcd.putstr("Temp: %0.2f"%tempC)
         time.sleep(2)
         

     else:
         time.sleep(.7)                             # esperar 700ms
         lcd.backlight_off()                        # apagar backlight
         lcd.display_off()                          # apagar lcd
         print('Distance: ',SR.distanceCM(),'cm')   # print de debugging en codigo final no estará
     
