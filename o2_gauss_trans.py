#!/usr/bin/env python3
"""
- pull cell broadcast db from a connected android device
- displays converted coordinates in bing maps
"""

import os
import time
import sqlite3
import subprocess
import GKConverter.gkconverter as gk

TMP_DIR = '/tmp'
DB_LOCATION = '/data/data/com.android.cellbroadcastreceiver/databases/'
DB_NAME = 'cell_broadcasts.db'

def convert(broadcast):
    """
    convert from broadcast form to longitude and latitude
    """
    right = int(broadcast[:6]+'0')
    high = int(broadcast[6:]+'0')
    longitude, latitude = gk.convert_GK_to_lat_long(right, high)

    return longitude, latitude

def get_db():
    """
    pull broadcast db from android device
    """
    subprocess.call(['adb', 'kill-server'])
    subprocess.call(['adb', 'root'])
    subprocess.call(['adb', 'pull', os.path.join(DB_LOCATION, DB_NAME), TMP_DIR])

def get_broadcasts():
    """
    get broadcasts + date from sqlite db
    """
    get_db()

    conn = sqlite3.connect(os.path.join(TMP_DIR, DB_NAME))
    cursor = conn.cursor()
    broadcasts = []
    for row in cursor.execute('SELECT body,date FROM broadcasts'):
        broadcasts.append((row[0], int(str(row[1])[:10])))

    return broadcasts

def main():
    """
    main
    """
    for broadcast, date in get_broadcasts():
        longitude, latitude = convert(broadcast)
        date_string = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(date))

        print(broadcast, date_string)

        # http://www.bing.com/maps/default.aspx?v=2&cp=48.605606~12.29315&style=o&lvl=15&sp=Point.48.605606_12.29315_Kernkraftwerk%20Isar___
        subprocess.Popen(['firefox', \
                'http://www.bing.com/maps/default.aspx?v=2&cp={}~{}&style=o&lvl=20&sp=Point.{}_{}_antenna_{}_{}___'\
                .format(longitude, latitude, longitude, latitude, date_string, broadcast)])

        # ff bug
        time.sleep(0.5)

if __name__ == '__main__':
    main()
