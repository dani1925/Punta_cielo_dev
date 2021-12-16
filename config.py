txt="""
Copyright 2021, RTS, All rights reserved.
Developed by ROBOTIC TECHNOLOGY SYSTEMS 
for Punta del Cielo
contact: contacto@mxrts.com

"""
url ="https://robo-arm-dev-fh3gwffhxq-uc.a.run.app/v1/users/5504dbde4c1d4b81a6b8f1cacfe973ec"
url_template ="/home/jrts/Punta_Dev/jetson/HTML/MALIN/index-2-constellation.html"                #"/home/pi/Desktop/proyecto2/Punta_cielo/index.html"
url_info ="/home/jrts/Punta_Dev/jetson/HTML/MALIN/indexURL.html"
url_screen_save="/home/jrts/Punta_Dev/jetson/HTML/MALIN/screen_save.html"               #"/home/pi/Desktop/Copia de HTML TEMPLATE/MALIN/index-2-constellation.html"
pwd="123"
pws="1234"
qr_port = "/dev/ttyUSB0"
teensy_port= "/dev/ttyACM0"
#con_string="host=localhost port=5432 user=admin password=admin dbname=data_base"
con_string="host=34.71.0.47 port=5432 user=postgres password=r0b04rm dbname=postgres"
orders_table ="arm.orders_1"
sql_1="SELECT * FROM "+orders_table+" where num_tkt='"   #CHANGE Num_tkt TO arm.orders  && num_tkt TO transacction_id_transaccion
sql_2="UPDATE "+orders_table+" SET status='Escan' WHERE num_tkt='"  
sql_3="UPDATE "+orders_table+" SET status='Finalizado' WHERE num_tkt='"
sql_test = "UPDATE "+orders_table+" SET status='" 
dict_bebidas={
    "B1T1": ["Capuccino", b"A"],
    "B2T1": ["Expresso", b"A"],
    "B3T1": ["LAtte", b"A"]
	
} 
