# -*- coding: utf-8 -*-
import os
from threading import Condition
import psycopg2
import sys
import concurrent.futures
import logging
from string import Template
from numpy import void
#from numpy.lib.function_base import _quantile_dispatcher
import webview
import time
import serial 
from serial import SerialException
from config import pwd
from config import pws
from config import dict_bebidas
from config import url
from config import url_template
from config import url_info
from config import url_screen_save
from config import txt
from config import con_string
from config import sql_1
from config import sql_2
from config import qr_port
from config import teensy_port
from config import sql_test
import pandas as pd
import requests


# --------------CONFIGURACION DE PUERTOS SERIE---------------------
#Serial Configuration
portname_= qr_port
baudrate_= 9600
timeout_=1 
Num_Ticket =0
num_bites = 10
Teen_portname=teensy_port
Teen_baudrate_= 9600
Teen_timeout_=1 
Tenn_num_bites = 255
#---------------------------------------------------------------
#---------------------------------------------------------------

num=0
i=1
lst_datos = [0,0,0,0,0]
j=0 #DELETE

def escribir_db (numero,status):
    try:
        numero=str(numero)
        sql_query=sql_test+status+"' WHERE num_tkt='"+numero+"';"
        print(sql_query)
        conn_string = con_string
        connection = psycopg2.connect(conn_string)
        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()
        return
    except Exception as e:
        logging.warning("Error en escribir_db",e)


def obtener_bebida(beb):
    try:
        for key, value in dict_bebidas.items():
            if beb == key:
                return value
    except Exception as e:
        logging.warning("Error en Obtener_bebida",e)            

def validacion(contrasena):

    if pws == contrasena:
        logging.warning("contrasena exitosa")
        return
       
    else:
        logging.warning("####---ACCESO DENEGADO---####")
        print("####---ACCESO DENEGADO---####")
        sys.exit()

def init (window):  
    internet_on()
    webview.start(reload, window , http_server=False,gui='qt' ) 

def internet_on():
    print("verificando Conexion a Internet...")
    try:
        time.sleep(2)
        request = requests.get(url,timeout=5)
        code = request.status_code
        if code == 200:
            print("Conexion a internet exitosa")
            logging.warning("Conexion Succesfull with Server")
            return True
    except:
        logging.warning("No hay acceso a internet")
        print("No hay conexion a interntet: Verifica tu conexion")
        sys.exit()
        return False

def reload(window):
    while True :
        num = "0"
        global j
        j+=1 

        print(j," ok")
        if i == 1:
            toggle_fullscreen(window)
    
        #-------LECTURA DE PUERTO SERIAL QR---------------    
        ser.flushInput() 
        num =ser.read(num_bites)
        num = num.decode("utf-8")
        #-----------------------------------------------------
        #------Separar Codigo recibido por escanner-----------
        firts_chars = num[0:5]
        num=num[5:]
        #----------------------------------------------------

        #----VERIFICAR SI ES UN QR PROPIO....................
        if firts_chars == "MXRTS" :
            code_ver(num)
        #--------CODIGO PARA DETENER EJECUCION------------------    
        elif firts_chars =="1":
            window.destroy()
            sys.exit()
        #.....................................................

        condicion = lst_datos[0]
        numero_ticket_bd = lst_datos[4]

        if condicion == "Load_1":
            print("Correcto")
            variable2 = "¡Hola! "+ lst_datos[1]
            variable1 = "Tu "+lst_datos[2]+" se esta preparando"
            d = {"bebida":variable1, "nombre": variable2}
            escritura_HTML(d)

            cadena_test=[window,numero_ticket_bd]    
            thread_1 = concurrent.futures.ThreadPoolExecutor().submit(test,cadena_test)
            window.load_url(url_info)
            thread_1.result()


        elif condicion=="Load_2":
            print("LOAD_2 lst_datos[4", numero_ticket_bd)
            variable2 = "¡Tu "+lst_datos[2]+" esta listo !"   
            print("lst_datos[3", lst_datos[3])
            print("tipo lst_datos[3",type(lst_datos[3]))    
            variable1 = "Puedes recogerlo en la charola "+lst_datos[3]
            d = {"bebida":variable1, "nombre": variable2}
            escritura_HTML(d)
            cadena_test=[window,numero_ticket_bd,lst_datos[3]]    
            thread_2 = concurrent.futures.ThreadPoolExecutor().submit(test2,cadena_test)
            window.load_url(url_info)
            thread_2.result()

def test(window_):
    Numero_de_tkt = window_[1]
    print("Actualizando base de datos....")
    escribir_db(Numero_de_tkt,"En proceso")
    wait_teensy()
    print("Bebida finalizada...")
    escribir_db(Numero_de_tkt,"FINALIZADO")
    window =window_[0]      
    print("terminando cuerda")
    lst_datos[0] = False
    window.load_url(url_screen_save)
    reload(window)

def test2 (window_):
    Numero_de_tkt = int(window_[1])
    print("Alcance test2 y el numero es:")
    wait_teensy()
    escribir_db(Numero_de_tkt,"ENTREGADO")
    window =window_[0]      
    print("terminando cuerda 2")
    lst_datos[0] = False
    window.load_url(url_screen_save)
    reload(window)

def toggle_fullscreen(window):
    global i
    i+=1 
    print("En modo de Pantalla completa")
    window.toggle_fullscreen()  

def code_ver(validar):
    num_=validar
    sql =sql_1+num_ +"';" 
    sql2 =sql_2+num_+"';"
    try:
        conn_string = con_string
        connection = psycopg2.connect(conn_string)
        cursor = connection.cursor()
        cursor.execute(sql)
        all_values = cursor.fetchmany() 
        print("All values", all_values )


        if (str(all_values[0][1]) == num_) & (all_values[0][4]=="Gen"):   #EXISTE EL NUMERO DE TKT EN BASE DE DATOS 
                                                                            #y tiene condicion de GENERADO?
            print("Procesa la bebida")
            try:
                lst_datos[0]="Load_1"                          # ELEMENTO 0 = CONDICION
                lst_datos[3]=all_values[0][1]                  # ELEMENTO 1 = NUMERO TKT 
                lst_datos[1]=all_values[0][2]                  # ELEMENTO 2 = NOMBRE 
                lst_datos[2]=all_values[0][3]                  # ELEMENTO 3 BEBIDA
                lst_datos[4]=num_                              # ELEMENTO 4 RETORNO DE NUM TKT
                Bebida = all_values[0][3]
            except Exception as e:
                print("Bandera 1",e)

            try:
                #...... OBTENER TEXTO Y VARIABLE A ESCRIBIR EN EL PUERTO SERIAL DEL TEENSY.................
                dict_values = obtener_bebida(Bebida)
                lst_datos[2]= dict_values[0]
                serial_write = dict_values[1] 
            except Exception as e :
                print("Bandera 2", e)

            try:
                #...... ASIGNAR TRAY LIBRE A LA ORDEN......................................................
                Data_return = Tray_selector()
                print("Data return", Data_return)
                Tray_selected=Data_return[0]
            except Exception as e:
                print("Bandera 3", e)    
            tray_bin=Data_return[1]

               
            #...... CAMBIAR STATUS DEL TRAY A OCUPADO......................................................
            Change_tray_status(Tray_selected,"OCUPADO")

            print("Selected tray = ",tray_bin)
            print("Selected tray = ",type(tray_bin))
            print ("Teensy serial write",type(serial_write))

            #...... ASIGNAR LA ORDEN AL TRAY LIBRE......................................................
            Asig_tray_order(Tray_selected,num_)


            teensy.write(serial_write)
            time.sleep(0.2)
            teensy.write(tray_bin)
            cursor.execute(sql2)     #Cambio de estado a ESCANEADO
            connection.commit()      #Descomentar en Produccion
            teensy.flush()
            return lst_datos


        if (str(all_values[0][1]) == num_) & (all_values[0][4]=="FINALIZADO"):   #EXISTE EL NUMERO DE TKT EN BASE DE DATOS 
                                                                         #y tiene condicion de FINALIZADO?
            print("Entregar bebida")
            lst_datos[0]="Load_2"  
            lst_datos[3]=all_values[0][1]                  # ELEMENTO 1 = NUMERO TKT 
            lst_datos[1]=all_values[0][2]                  # ELEMENTO 2 = NOMBRE 
            lst_datos[2]=all_values[0][3]                  # ELEMENTO 3 BEBIDA
            lst_datos[4]=num_                              # ELEMENTO 4 RETORNO DE NUM TKT
            #...... BUSCAR EL TRAY ASIGNADO A LA ORDEN EN CSV......................................................
            print("ESTADO 1 ")
            Bebida = all_values[0][3]

            #-----OBTENER Y ORANIZAR DATOS DE BEBIDAS EN DICCIONARIO DE CONFIG----------
            dict_values = obtener_bebida(Bebida)
            lst_datos[2]= dict_values[0]

            order= int(num_)
            print("ESTADO 2 ")

            Order_in_tray=Find_tray_from_order(order)


            #...... CAMBIAR STATUS DEL TRAY A LIBRE......................................................
            Change_tray_status(int(Order_in_tray),"LIBRE")
            print("ORDER IN TRAY ",Order_in_tray)
            print("ESTADO 3 ")

            #...... PARAR BITE PARA ESCRIBIR EN TEESNY......................................................

            Teensy_tray_bite=Teensy_tray_to_turn(Order_in_tray)
            print("ESTADO 4 ")

            teensy.write(Teensy_tray_bite)
            print("ESTADO 5 ")
            print ("order in Tray", Order_in_tray)
            lst_datos[3]=str(Order_in_tray)
            return lst_datos

        else:
            print("No hay comunicacion con servidor ")
            lst_datos[2] = "Sin comunicacion"
            return lst_datos
    except Exception as e:
        logging.warning("EXCEPTION IN CODE_VER", e)
        lst_datos[2] = "Sin comunicacion"
        return lst_datos


def escritura_HTML (d):

    try: 
            #Sustituir variables
            filein=open(url_template)#,"r")
            src = Template(filein.read())
            result = src.substitute(d)
            filein.close()
            logging.warning("Variable sustituida en index")
    except:
            print("No se pudo cargar archivo index template")
            logging.warning("No se pudo cargar url_template",e)
            #sys.exit()
            #---------------------------------------------------------------
    try:
            filein2 = open(url_info,"w")
            filein2.writelines(result)
            filein2.close() 
            logging.warning("Se escribio correcta,ente en alrchivo html")    
    except KeyError:
            logging.warning("No se logro abrir el archivo indexX.html")
    return

def wait_teensy():
    teensy.flush()
    terminacion = teensy.readline()
    terminacion = str(terminacion.decode("utf-8"))
    if terminacion == "End":
        print("Bebida Terminada")
        return
    else:
        time.sleep(0.1)
        wait_teensy()

def Tray_selector():
    try:
        csv_file = pd.read_csv('/home/jrts/Punta_Dev/tray.csv')
        data_list = csv_file.values.tolist()
        print("data_list in tray selector",data_list)
        for items, values, orders in data_list:
            if values == "LIBRE":
                print("Items =", type(items))
                tray = items
                if tray == 1:
                    print("Tray1 sleceted")
                    Serial_write = [tray,b'1']
                    return Serial_write
                elif tray == 2:
                    Serial_write = [tray,b'2']
                    print("Tray2 sleceted")    
                    return Serial_write
                elif tray == 3:
                    Serial_write = [tray,b'3']
                    print("Tray3 sleceted")    
                    return Serial_write
   
    except Exception as e:
        print("Error en Tray_selector",e)
        logging.warning("Error en Tray_selector",e)    
        return Serial_write
        
def Change_tray_status(tray,status):
    try:
        csv_file = pd.read_csv('/home/jrts/Punta_Dev/tray.csv')
        csv_file.loc[csv_file.TRAY == tray, "STATUS"]=status
        csv_file.to_csv('/home/jrts/Punta_Dev/tray.csv',index=False)
    except Exception as e:
        print("Error en Change_Tray_status",e)
        logging.warning("Error en Change_tray_status",e)    
def Asig_tray_order(tray,order):
    try:
        csv_file = pd.read_csv('/home/jrts/Punta_Dev/tray.csv')
        csv_file.loc[csv_file.TRAY == tray, "ORDER"]=order
        csv_file.to_csv('/home/jrts/Punta_Dev/tray.csv', index=False)
    except Exception as e :
        print("Error en Asign_tray_order")
        logging.warning("Error en Assign_tray_to_order",e)    

        
def Find_tray_from_order(order):
    try:
        csv_file = pd.read_csv('/home/jrts/Punta_Dev/tray.csv')
    except Exception as e:
        print("Error en Find_tray_from_order")
        logging.warning("Error en Find_tray_from_order",e)    

    csv_file.set_index("TRAY")
    try:
        print("order type", type(order))
        print("order", order)
        A = csv_file.loc[csv_file.ORDER == order].TRAY.item()
    except Exception as e:
        print("Error 2 en find tray from order",e)
        logging.warning("Error 4 en Find_tray_from_order",e)    

    return A

def Teensy_tray_to_turn(tray):
    if tray == 1:
        Tray_bit = b'X'
    elif tray == 2:
        Tray_bit = b'X'
    else:
        Tray_bit = b'X'
    return Tray_bit    
#--------------------Inicio-----------------------------
        
if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.WARNING, 
    datefmt="%D:%H:%M:%S", filename='debug.log')
    logging.warning("######--Arranque de sistema--#######")
    print(txt)
    validacion(input("Digite Contraseña para continuar :"))
    window = webview.create_window('hello', url_screen_save)

    try:
        logging.info("Tratando de conectar al puerto serie (Lector QR)")
        ser = serial.Serial(port= portname_,  baudrate=baudrate_, timeout=timeout_)
        ser.flushInput()
        logging.warning("Conectado al puerto serial (Lector QR)")
        print("Conectado al puerto serie (Lector QR)", ser.portstr)
        
    except:
        logging.warning("No se pudo conectar con lector QR")
        print("No se pudo conectar con lector QR")
        sys.exit()

    try:
        logging.info("Tratando de conectar al puerto serie (Teensy 3.5)")
        teensy = serial.Serial(port= Teen_portname,  baudrate=Teen_baudrate_, timeout=Teen_timeout_)
        teensy.flushInput()
        logging.warning("Conectado al puerto serial (Teensy 3.5)")
        print("Conectado al puerto serie (Teensy 3.5)", teensy.portstr)
        #init(window)

    except SerialException:
        logging.warning("No se pudo conectar con Teensy 3.5")
        print("No se pudo conectar con Teensy 3.5")
        sys.exit()

    try:
        conn_string = con_string
        print(conn_string)
        connection = psycopg2.connect(conn_string)
        cursor = connection.cursor()
        print("Conexion establecida con BD")
        init(window)
    except Exception as e:
        print("No se pudo conectar con DB", e)






