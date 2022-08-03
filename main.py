from machine import I2C, Pin, ADC
import ssd1306
import framebuf
from time import sleep
from hcsr04 import HCSR04
from variables import (logo, alarma, regando)
from DHT22 import DHT22
from _thread import start_new_thread as nuevo_hilo

"""##### IMPORTS ####"""

"""#### VARIABLES #####"""

dht_sensor = DHT22(Pin(15, Pin.OUT), dht11=False)  # sensor temp y humedad
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)  # estableciendo i2c
SR = HCSR04(19, 18)  # identificando pines trig y echo del modulo hcsr04
relesonda = Pin(10, Pin.OUT)  # rele sonda suelo
relebomba = Pin(12, Pin.OUT)  # rele bomba
relesonda.value(1)  # apagados por defecto
relebomba.value(1)
led_alarma = Pin(25, Pin.OUT)
led_alarma.value(0)
sensor_awa = Pin(16, Pin.IN)  # sensor alarma agua
adc = ADC(26)  # establecemos adc en pin 26 donde esta conectada la sonda suelo
display = ssd1306.SSD1306_I2C(128, 64, i2c)  # iniciamos oled
buf_logo = bytearray(logo)  # pasando los arrays de imagenes a framebuffer
buf_alarma = bytearray(alarma)
buf_regando = bytearray(regando)
fb_alarma = framebuf.FrameBuffer(buf_alarma, 128, 64, framebuf.MONO_HLSB)
fb_logo = framebuf.FrameBuffer(buf_logo, 128, 64, framebuf.MONO_HLSB)
fb_regando = framebuf.FrameBuffer(buf_regando, 128, 64, framebuf.MONO_HLSB)

"""############ FIN VARIABLES ######################"""

"""########### BLOQUE FUNCIONES #######################"""


def riega():
    while True:
        sleep(15)
        relesonda.value(0)
        sleep(1)
        sensor_suelo = adc.read_u16()
        relesonda.value(1)
        sensor_suelo = sensor_suelo / 655.35
        humedad_suelo = 100 - sensor_suelo
        if 40 <= humedad_suelo <= 75:
            if sensor_awa.value() == 1:
                relebomba.value(0)
                regando()
                sleep(1)
                display.poweroff()
                display.fill(0)
                relebomba.value(1)
            else:
                alarma_awa()
                break

        elif humedad_suelo < 9:
            alarma_suelo()
            break


def intro():
    display.text("  Neptuno v.02", 0, 0)
    for i in range(-64, 0):
        display.blit(fb_logo, i, 16)
        display.show()
    display.text("Creado", 0, 32)
    display.text("por", 0, 40)
    display.text("APR", 0, 49)
    display.text("Con", 78, 22)
    display.text("amor", 78, 32)
    display.text("para", 78, 40)
    display.text("Mery", 78, 50)
    display.show()
    sleep(3)
    display.poweroff()
    display.fill(0)


def alarma_awa():
    display.fill(0)
    for i in range(1, 3):
        for i in range(-64, 128):
            display.fill(0)
            display.poweron()
            display.text("--ALARMA--", i, 0)
            display.blit(fb_alarma, 0, 16)
            display.text("NO HAY", 49, 20)
            display.text("AGUA EN EL", 49, 30)
            display.text(" DEPOSITO", 49, 40)
            display.show()
            led_alarma.value(1)


def alarma_suelo():
    display.fill(0)
    for i in range(1, 3):
        for i in range(-64, 128):
            display.fill(0)
            display.poweron()
            display.text("--ALARMA--", i, 0)
            display.blit(fb_alarma, 0, 16)
            display.text("Fallo del", 49, 20)
            display.text("  sensor", 49, 30)
            display.text("  suelo", 49, 40)
            display.show()
            led_alarma.value(1)


def regando():
    display.fill(0)
    display.poweron()
    display.text("Neptuno v0.2", 0, 0)
    display.blit(fb_regando, 0, 16)
    display.text("Regando...", 38, 16)
    display.show()


def mainloop():
    while True:
        if led_alarma.value() == 1:
            break
        else:
            distancia = SR.distanceCM()
            if distancia < 10:
                display.fill(0)
                display.poweron()
                display.text('Un momento...', 0, 0)
                display.show()
                relesonda.value(0)
                sleep(1)
                sensor_suelo = adc.read_u16()
                relesonda.value(1)
                sensor_suelo = sensor_suelo / 655.35
                humedad_suelo = 100 - sensor_suelo
                T, H = dht_sensor.read()
                T = round(T, 2)
                H = round(H, 2)
                humedad_suelo = round(humedad_suelo, 2)
                if sensor_awa.value() == 1:
                    deposito = "OK"
                else:
                    deposito = "ALARMA"
                display.fill(0)
                # display.poweron()
                display.text('Neptuno v0.2', 0, 0)
                display.text(f'Temp:   {T} C', 0, 16)
                display.text(f'Hum.R.: {H} %', 0, 26)
                display.text(f'Suelo: {humedad_suelo} %', 0, 36)
                display.text(f'Deposito: {deposito}', 0, 46)
                display.text(f"dist: {distancia}", 0, 56)
                display.show()
                sleep(5)
                display.poweroff()
            else:
                sleep(.5)
                continue


"""#################### FIN FUNCIONES #################"""

intro()  # intro lcd

try:
    nuevo_hilo(riega, ())  # iniciamos hilo secundario para check humedad y riego

    while True:
        mainloop()
except:
    pass


