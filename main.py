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
SR = HCSR04(19, 18)                                 # identificando pines trig y echo del modulo hcsr04
relesonda = Pin(10, Pin.OUT)                        # rele sonda suelo
relebomba = Pin(12, Pin.OUT)                        # rele bomba
relesonda.value(1)                                  # apagados por defecto
relebomba.value(1)
led_alarma = Pin(25, Pin.OUT)                       # led de alarma, por el momento 25 (fase dev)
led_alarma.value(0)                                 # apagado por defecto
sensor_awa = Pin(16, Pin.IN)                        # sensor alarma agua
adc = ADC(26)                                       # establecemos adc en pin 26 donde esta conectada la sonda suelo
display = ssd1306.SSD1306_I2C(128, 64, i2c)         # iniciamos oled
buf_logo = bytearray(logo)                          # pasando los arrays de imagenes a framebuffer
buf_alarma = bytearray(alarma)
buf_regando = bytearray(regando)
fb_alarma = framebuf.FrameBuffer(buf_alarma, 128, 64, framebuf.MONO_HLSB)
fb_logo = framebuf.FrameBuffer(buf_logo, 128, 64, framebuf.MONO_HLSB)
fb_regando = framebuf.FrameBuffer(buf_regando, 128, 64, framebuf.MONO_HLSB)

"""############ FIN VARIABLES ######################"""

"""########### BLOQUE FUNCIONES #######################"""


def riega():  # funcion riega, controla riego, voltaje bateria y nivel de agua
    while True:
        sleep(5)  # tiempo para bucle, def= 3600
        Vsys = ADC(29)  # leemos voltaje vsys
        Pin(29, Pin.IN)
        conversion = (3.3 / (65535)) * 3
        volts = Vsys.read_u16() * conversion
        porcent = (volts - 2.7) * 83.333
        volts = round(volts, 2)
        porcent = round(porcent, 2)
        if porcent <= 20:  # si es menor de 20%
            display.fill(0)  # sacamos warning por display 3 segundos
            display.poweron()
            display.text("WARNING", 0, 0)
            display.text(f"queda un {porcent}%", 0, 16)
            display.text("de bateria", 0, 26)
            display.text(f"{volts} V in", 0, 36)
            display.show()
            sleep(3)
            display.poweroff()
        else:
            pass
        relesonda.value(0)  # encendemos sonda
        sleep(.5)  # esperamos 500ms
        sensor_suelo = adc.read_u16()  # leemos valor de sonda
        relesonda.value(1)  # apagamos sonda
        sensor_suelo = sensor_suelo / 655.35  # pasamos valor a %
        humedad_suelo = 100 - sensor_suelo  # obtenemos % seco, lo restamos a 100 para tener % humedad
        if humedad_suelo < 9:
            alarma_suelo()  # alarma sonda suelo, display alarma
            break
        elif humedad_suelo >= 95:
            alarma_suelo()
            break
        elif humedad_suelo <= 60:  # valores para mantener: entre 40% y 75% humedad
            if sensor_awa.value() == 1:  # comprobamos si hay agua
                relebomba.value(0)  # y encendemos bomba
                regando()  # display regadera
                sleep(3)  # tiempo de riego
                display.poweroff()
                display.fill(0)
                relebomba.value(1)  # apagado de bomba
            else:
                alarma_awa()  # alarma deposito sin agua, display alarma
                break


def intro():
    display.text("  Neptuno v0.3", 0, 0)
    for i in range(-64, 0):                         # funcion intro animada en display
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


def alarma_awa():                       # funcion alarma deposito
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


def alarma_suelo():                 # funcion alarma sonda suelo
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


def regando():                  # funcion regadera display
    display.fill(0)
    display.poweron()
    display.text("Neptuno v0.3", 0, 0)
    display.blit(fb_regando, 0, 16)
    display.text("Regando...", 38, 16)
    display.show()


def mainloop():
    while True:                     # si ha habido alarma, se comprueba y se para
        if led_alarma.value() == 1:
            break
        else:
            distancia = SR.distanceCM()     # estos no son los androides que buscais...
            if distancia < 10:
                display.fill(0)
                display.poweron()
                display.text('Un momento...', 0, 0)
                display.show()
                relesonda.value(0)              # encender sonda suelo, leer, apagar
                sleep(1)
                sensor_suelo = adc.read_u16()
                relesonda.value(1)
                sensor_suelo = sensor_suelo / 655.35
                humedad_suelo = 100 - sensor_suelo      # calcular % humedad suelo
                T, H = dht_sensor.read()
                T = round(T, 2)
                H = round(H, 2)                         # leer Temp y humedad relativa
                humedad_suelo = round(humedad_suelo, 2)
                Vsys = ADC(29)                          # establecer vsys en pin 29
                Pin(29, Pin.IN)                         # 29 pull up
                conversion = (3.3 / (65535)) * 3        # factor de conversion
                volts = Vsys.read_u16() * conversion    # lectura voltaje vsys
                porcent = (volts - 2.7) * 83.333        # calc % en base a voltaje celda Li 18650 (min. 2.7, max 3.7)
                volts = round(volts, 2)
                porcent = round(porcent, 2)
                if sensor_awa.value() == 1:
                    deposito = "OK"
                else:
                    deposito = "ALARMA"
                display.fill(0)
                display.text('Neptuno v0.3', 0, 0)       # sacamos info por display: temp, hum, suelo, deposito y volts
                display.text(f'Temp:   {T} C', 0, 16)
                display.text(f'Hum.R.: {H} %', 0, 26)
                display.text(f'Suelo: {humedad_suelo} %', 0, 36)
                display.text(f'Deposito: {deposito}', 0, 46)
                display.text(f'B:{volts}V {porcent}%', 0, 56)
                display.show()
                sleep(3)
                display.poweroff()
            else:
                sleep(.5)
                continue


"""#################### FIN FUNCIONES #################"""

intro()

try:
    nuevo_hilo(riega, ())  # iniciamos hilo secundario para check humedad y riego

    while True:
        mainloop()
except:
    pass


