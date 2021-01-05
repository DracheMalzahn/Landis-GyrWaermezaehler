#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import serial, time
import numpy as np
from datetime import datetime
import MySQLdb

# Zum Speichern der Messwerte brauchen wir ein Array welches zu jedem Wert 3 Objekte speichern kann
# [0] ist der Index Wert
# [1] ist der Messwert 
# [2] ist die Einheit des Messwertes wenn Sie vorhanden ist
messdaten = np.zeros([128,3], dtype='object')
mysqlWerte = [ 0, 0, 0, 0, 0 ]
hilfsstring = ''
messdatenindex = 0


# Oeffnen der seriellen Schnittstelle. Hier haben wir vorher mit den udev Rules
#  einen Alias mit der Seriennummer auf den Warmezaehler erstellt
ser = serial.Serial("/dev/Waermezaehler", baudrate=300, bytesize=7, parity="E", stopbits=1, timeout=2, xonxoff=0, rtscts=0)

#Senden der Initialen Message, damit der Zaehler uns seine Werte verraten wird.
ser.write("\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
ser.write("\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

#Dies ist der eigendliche Request den der Zaehler braucht um mit der Uebertragung zu beginnen
ser.write("/?!\x0D\x0A")
ser.flush();
time.sleep(.5)

# Die erste Antwort vom Zaehler ist eine Selbstidentifizierung des Modells. In meinem Fall hier ein
# -> /LUGCUH50
# Diese bracuhe ich aber nicht und kann sie deshalb nach dem lesen sofort verwerfen.
ser.readline()

#Setze die Baudrate auf 2400 Baud hoch
ser.baudrate=2400

try:
    # Dies ist die Schleife die die ankommenden Daten von der seriellen Schnittstelle abholen wird.
    #  sobald ein einzelnes ! empfangen wird, ist die Uebertragung vom Zaehler vollstaendig
    while True:
        response = ser.readline()
        
        # So, wir haben nun eine Zeile vom Zaehler erhalten und wollen diese in Indexwerte der Messpunkte  und Werte splitten
        for x in response:
            # Sobald eine ( erscheint ist der Indexwert abgeschlossen. Der Indexwert beginnt immer direkt am Anfang
            #  einer Zeile oder direkt nach einem )
            if x == '(':
                messdaten[messdatenindex, 0] = hilfsstring
                hilfsstring = ''

            # Sobald eine ) erscheint ist der Messwert abgeschlossen. Der Messwert ist immer in () eingeschlossen und beginnt immer 
            #  in einer Zeile direkt nach dem Indexwert und einer (
            if x == ')':
                gesplittet = np.str.split(hilfsstring,'*',1)
                #print("DEBUG: Hilfsstring zur Einheitenzerlegung ->", len(gesplittet) )
                #print("DEBUG: Hilfsstring zur Einheitenzerlegung ->", gesplittet )
                #print("DEBUG: --------------------------------------------------------------")

                messdaten[messdatenindex, 1] = gesplittet[0]
                if len(gesplittet) >=2:
                    messdaten[messdatenindex, 2] = gesplittet[1]
                hilfsstring = ''
                messdatenindex += 1

            # Hier filtern wir noch unerwuenschte Zeiten heraus wie die () CR / LF oder ein "Start of Text"
            #  Sollte es sich nicht um solche Zeichen handeln, so speichern wir es in einem Hilfstext und eintscheiden aufgrund der
            #  nachfolgenden () ob es ein Index oder Messwert war.
            if x not in '()\n\r\x02':
                hilfsstring += x

        # Wie oben schon beschrieben. Bei dem Request zum senden wird ein ! die Uebertragung beenden.
        if "!" in response:
            break
finally:
    # Schliessen der serielle Schnittstelle
    ser.close()

# Jetzt suchen wir uns die Messdaten heraus die wir brauchen. Dafuer durchsuchen wir das Array mit argwhere
#  argwhere liefert ein Array zurueck in dem die Werte gefunden wurden. Dies ist ein array of 2D
#  dazu muessen wir in den Messwerten erst einmal die richtige Arrayposition finden
#  argwhere [0,0] ist die Indexposition in dem der Wert gefunden wurde
#  in den messwerten ist der Wert dann index,1 gespeichert

mysqlWerte[0] =  int(messdaten[(np.argwhere(messdaten == '6.8' )[0,0])][1])
mysqlWerte[1] =  float(messdaten[(np.argwhere(messdaten == '6.26')[0,0])][1])
mysqlWerte[2] =  int(messdaten[(np.argwhere(messdaten == '6.31')[0,0])][1])
mysqlWerte[3] =  int(messdaten[(np.argwhere(messdaten == '6.32')[0,0])][1])
mysqlWerte[4] =  int(messdaten[(np.argwhere(messdaten == '9.31')[0,0])][1])


myConnect = MySQLdb.connect( "localhost", "root", "", "HannahDB" )
myCursor  = myConnect.cursor()

add_messwerte = ("INSERT INTO waermezaehler "
                 "( zaehlerstand, durchlauf, betriebsstunden, fehlstunden, flowhours ) "
                 "VALUES (%s, %s, %s, %s , %s)")

# Neue Zeile in die DB schreiben.
myCursor.execute(add_messwerte, mysqlWerte )

# Make sure data is committed to the database
myConnect.commit()

myCursor.close()
myConnect.close()




