import logging
import pymysql
import time
import jwt  
import json

class sql():
    def __init__(self):
        self.conn=pymysql.connect("140.112.26.241","ican","lab125a","inanalysis")
        self.cursor=self.conn.cursor()
