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
"""
def addDriver(cur, name, phone):
    query = "INSERT INTO Driver (DriverName, DriverTelephoneNumber) VALUES (%s, %s)"
    recset = [name, phone]
    cur.execute(query, recset)

def addBus(cur, bus_id, model, year):
    query = "INSERT INTO Bus (BusID, Model, Year) VALUES (%s, %s, %s)"
    recset = [bus_id, model, year]
    cur.execute(query, recset)

"""def deleteBus():
    #todo

def insertTripInfo():
    #todo"""

def createTables(conn, cursor):
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Trip (
            TripNumber INT PRIMARY KEY,
            StartLocationName VARCHAR(255),
            DestinationName VARCHAR(255)
        );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bus (
                BusID INT PRIMARY KEY,
                Model VARCHAR(255),
                Year INT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Driver (
                DriverName VARCHAR(255) PRIMARY KEY,
                DriverTelephoneNumber VARCHAR (20)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Stop (
                StopNumber INT PRIMARY KEY,
                StopAddress VARCHAR(255)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TripOffering (
                TripNumber INT,
                Date VARCHAR(255),
                ScheduledStartTime VARCHAR(255),
                SecheduledArrivalTime VARCHAR(255),
                DriverName VARCHAR(255),
                BusID INT,
                PRIMARY KEY (TripNumber, Date, ScheduledStartTime),
                FOREIGN KEY (TripNumber) REFERENCES Trip(TripNumber),
                FOREIGN KEY (DriverName) REFERENCES Driver(DriverName),
                FOREIGN KEY (BusID) REFERENCES Bus (BusID) ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ActualTripStopInfo (
                TripNumber INT,
                Date VARCHAR(255),
                ScheduledStartTime VARCHAR(255),
                StopNumber INT,
                ScheduledArrivalTime VARCHAR(255),
                ActualStartTime VARCHAR(255),
                ActualArrivalTime VARCHAR(255),
                NumberOfPassengerIn INT,
                NumberOfPassengerOut INT,
                PRIMARY KEY (TripNumber, Date, ScheduledStartTime, StopNumber),
                FOREIGN KEY (TripNumber, Date, ScheduledStartTime) REFERENCES TripOffering(TripNumber, Date, ScheduledStartTime) ON DELETE CASCADE,
                FOREIGN KEY (StopNumber) REFERENCES Stop(StopNumber) ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TripStopInfo (
                TripNumber INT,
                StopNumber INT,
                SequenceNumber VARCHAR(255),
                DrivingTime VARCHAR(255),
                PRIMARY KEY (TripNumber, StopNumber),
                FOREIGN KEY (TripNumber) REFERENCES Trip (TripNumber),
                FOREIGN KEY (StopNumber) REFERENCES Stop (StopNumber)
            );
        """)

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {e}")
