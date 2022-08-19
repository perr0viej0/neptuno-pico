# neptuno-pico
Sistema de riego automatico con raspberry pi pico

Neptuno es un montaje de raspberry pi pico y micropython, junto con los sensores necesarios para obtener
un sistema de riego automatico basado en deposito y configurable

El montaje dispone de un OLED 0.96" para mostrar informacion, un sensor dht22 para temperatura y humedad,
un sensor de nivel de agua para el deposito, una bomba sumergible, una caja de 4 reles, una sonda
de humedad de suelo y un modulo ultrasonido de medicion de distancia.

El funcionamiento es muy sencillo: neptuno tiene 2 temporizadores independientes, uno para comprobar la distancia
en el modulo de ultrasonido cada 700ms, y otro que comprueba los niveles de humedad del suelo cada hora.

Si acercamos la mano al modulo ultrasonido, se encendera el lcd y nos mostrara por pantalla valores de temperatura
y humedad del ambiente.

Cada hora se comprueba el nivel de humedad del suelo, si este es menor a un % indicado, comprueba si hay agua en el 
deposito y si la hay comienza el riego.
Si la humedad es superior a un % indicado, no se realiza ninguna accion, permitiendo que esa humedad se evapore/consuma 
y no regar en exceso.


Actualmente está en desarrollo debido a que todavía no dispongo de todos los sensores/materiales necesarios. Debido a 
la escasez de chips los plazos de entrega se han visto afectados.
