import psycopg2
from psycopg2.extras import RealDictCursor

def connectDataBase():
    DB_NAME = "CS4350_Lab4"
    DB_USER = "postgres"
    DB_PASS = "123"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    try:
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            cursor_factory=RealDictCursor,
        )


        return conn

    except:
        print("Database not connected successfully!")

"""def displaySchedule():
    #todo

def editSchedule():
    #todo

def displayStops():
    #todo

def displayDriverSchedule():
    #todo

def addDrive():
    #todo

def addBus():
    #todo

def deleteBus():
    #todo

def insertTripInfo():
    #todo"""