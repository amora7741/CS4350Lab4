import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from client import handleInput

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

def displaySchedule(cur, startLocation, destination, date):
    query = """
        SELECT 
            "T".StartLocationName,
            "T".DestinationName,
            "TO".Date,
            "TO".ScheduledStartTime,
            "TO".ScheduledArrivalTime,
            "TO".DriverName,
            "TO".BusID
        FROM 
            Trip "T"
        INNER JOIN 
            TripOffering "TO" ON "T".TripNumber = "TO".TripNumber
        WHERE 
            "T".StartLocationName = %s AND
            "T".DestinationName = %s AND
            "TO".Date = %s;
    """

    recset = (startLocation, destination, date)

    cur.execute(query, recset)
    output = cur.fetchall()

    if not output:
        raise Exception("There are no trip offerings for this trip.")
    
    for row in output:
        print(', '.join(map(str, row.values())))

def editSchedule(cur, choice):
    if choice.lower() == "a":
        deleteOffering(cur)
    elif choice.lower() == "b":
        addOfferings(cur)

def deleteOffering(cur):
    tripNumber = handleInput("Enter the trip number or [R] to return: ", int)

    if tripNumber:
        date = handleInput("Enter the date for the offering in MM-DD-YYYY format: ", str)
        scheduledStart = handleInput("Enter the scheduled start time for the offering: ", str)
    else:
        return

    tripQuery = "SELECT * FROM TripOffering WHERE TripNumber = %s AND Date = %s AND ScheduledStartTime = %s"
    recset = [tripNumber, date, scheduledStart]

    cur.execute(tripQuery, recset)

    existingTrip = cur.fetchone()

    if existingTrip is None:
        raise Exception("This trip offering does not exist!")

    query = "DELETE FROM TripOffering WHERE TripNumber = %s AND Date = %s AND ScheduledStartTime = %s"

    cur.execute(query, recset)

def addOfferings(cur):
    numberToAdd = handleInput("How many Trip Offerings to add?: ", int)

    setOfTripOfferings = []
    for i in range(1, numberToAdd + 1):
        print("\n")
        tripOffering = {
            'TripNumber': handleInput(f"Enter the trip number for trip offering {i}: ", int),
            'Date': handleInput(f"Enter the date for trip offering {i} in MM-DD-YYYY format: ", str),
            'ScheduledStartTime': handleInput(f"Enter the Scheduled Start Time for trip offering {i}: ", str),
            'ScheduledArrivalTime': handleInput(f"Enter the Scheduled Arrival Time for trip offering {i}: ", str),
            'DriverName': handleInput(f"Enter the driver name for trip offering {i}: ", str).lower(),
            'BusID': handleInput(f"Enter the BusID for trip offering {i}: ", int)
        }
        setOfTripOfferings.append(tripOffering)

    missingTrips, missingDrivers, missingBusIDs = checkMissingEntries(cur, setOfTripOfferings)
    
    if missingDrivers or missingBusIDs or missingTrips:
        print("Some values are missing in the parent tables for the given trip(s).")
        if not confirmAddition():
            return

    addMissingEntries(cur, missingTrips, missingDrivers, missingBusIDs)

    addTripOfferingsToDB(cur, setOfTripOfferings)


def checkMissingEntries(cur, setOfTripOfferings):
    tripNumbers = {offering['TripNumber'] for offering in setOfTripOfferings}
    driverNames = {offering['DriverName'] for offering in setOfTripOfferings}
    busIDs = {offering['BusID'] for offering in setOfTripOfferings}

    missingTrips = checkMissing(cur, tripNumbers, "Trip", "TripNumber")
    missingDrivers = checkMissing(cur, driverNames, "Driver", "DriverName")
    missingBusIDs = checkMissing(cur, busIDs, "Bus", "BusID")

    return missingTrips, missingDrivers, missingBusIDs

def checkMissing(cur, items, table, column):
    missingItems = []
    for item in items:
        cur.execute(f"SELECT * FROM {table} WHERE {column} = %s", (item,))
        if cur.fetchone() is None:
            missingItems.append(item)
    return missingItems

def confirmAddition():
    choice = handleInput("\nWould you like to add those missing entries into the parent tables?\nEnter 'y' to add or 'n' to cancel: ", str).lower()
    return choice == 'y'

def addMissingEntries(cur, missingTrips, missingDrivers, missingBusIDs):
    if missingTrips:
        addMissingTrips(cur, missingTrips)
    if missingDrivers:
        addMissingDrivers(cur, missingDrivers)
    if missingBusIDs:
        addMissingBuses(cur, missingBusIDs)

def addMissingTrips(cur, missingTrips):
    for tripNumber in missingTrips:
        print(f"\nAdding missing trip number {tripNumber}")
        startLocation = handleInput("Enter the start location name: ", str).lower()
        destinationName = handleInput("Enter the destination name: ", str).lower()
        cur.execute("INSERT INTO Trip (TripNumber, StartLocationName, DestinationName) VALUES (%s, %s, %s)", 
                    (tripNumber, startLocation, destinationName))

def addMissingDrivers(cur, missingDrivers):
    for driverName in missingDrivers:
        print(f"\nAdding missing driver {driverName}")
        phoneNumber = handleInput("Enter the driver's telephone number: ", str)
        phoneNumber = ''.join(filter(str.isdigit, phoneNumber))
        cur.execute("INSERT INTO Driver (DriverName, DriverTelephoneNumber) VALUES (%s, %s)", 
                    (driverName, phoneNumber))

def addMissingBuses(cur, missingBusIDs):
    for busID in missingBusIDs:
        print(f"\nAdding missing bus ID {busID}")
        model = handleInput("Enter the bus model: ", str).lower()
        year = handleInput("Enter the bus year: ", int)
        cur.execute("INSERT INTO Bus (BusID, Model, Year) VALUES (%s, %s, %s)", 
                    (busID, model, year))
        
def addTripOfferingsToDB(cur, setOfTripOfferings):
    for offering in setOfTripOfferings:
        cur.execute("INSERT INTO TripOffering (TripNumber, Date, ScheduledStartTime, ScheduledArrivalTime, DriverName, BusID) VALUES (%s, %s, %s, %s, %s, %s)", 
                    (offering['TripNumber'], offering['Date'], offering['ScheduledStartTime'], offering['ScheduledArrivalTime'], offering['DriverName'], offering['BusID']))


def displayStops(cur, tripNumber):
    query = "SELECT * FROM Trip WHERE TripNumber = %s"
    recset = [tripNumber]
    cur.execute(query, recset)
    existingTrip = cur.fetchone()

    if existingTrip is None:
        raise Exception(f"Trip with ID {tripNumber} does not exist.")
    
    query = "SELECT * FROM TripStopInfo WHERE TripNumber = %s"
    cur.execute(query, recset)
    stopInfo = cur.fetchall()

    if(len(stopInfo) == 0):
        print("This trip has no stop data.")
        return
    
    for row in stopInfo:
        print(', '.join(map(str, row.values())))

def displayDriverSchedule(cur, driverName, startDate):
    try:
        endDate = (datetime.strptime(startDate, "%m-%d-%Y") + timedelta(days=6)).strftime("%m-%d-%Y")
    except Exception as e:
        raise Exception(f"The date was not formatted properly.")
    
    query = "SELECT * FROM Driver WHERE DriverName = %s"
    recset = [driverName]
    cur.execute(query, recset)
    existingDriver = cur.fetchone()

    if existingDriver is None:
        raise Exception(f"The driver {driverName} does not exist!")
    
    query = """SELECT * FROM TripOffering "TO" WHERE "TO".DriverName = %s AND "TO".Date BETWEEN %s AND %s"""
    recset = [driverName, startDate, endDate]
    cur.execute(query, recset)

    schedule = cur.fetchall()

    if not schedule:
        raise Exception(f"No schedule found for {driverName} in the given week.")

    for trip in schedule:
        print(', '.join(map(str, trip.values())))

def addDriver(cur, name, phone):
    query = "INSERT INTO Driver (DriverName, DriverTelephoneNumber) VALUES (%s, %s)"
    recset = [name, phone]
    cur.execute(query, recset)

def addBus(cur, bus_id, model, year):
    query = "INSERT INTO Bus (BusID, Model, Year) VALUES (%s, %s, %s)"
    recset = [bus_id, model, year]
    cur.execute(query, recset)

def deleteBus(cur, busID):
    checkValid = "SELECT * FROM Bus WHERE BusID = %s"
    recset = [busID]
    cur.execute(checkValid, recset)
    existingBus = cur.fetchone()

    if existingBus is None:
        raise Exception(f"Bus with ID {busID} does not exist.")

    deleteQuery = "DELETE FROM Bus WHERE busid = %s"
    cur.execute(deleteQuery, recset)


def insertTripInfo(cur, tripNumber, date, scheduledStart, actualStart, actualArrival, stopNum, numPassIn, numPassOut):
    query = "SELECT * FROM TripOffering WHERE TripNumber = %s AND Date = %s AND ScheduledStartTime = %s"
    recset = [tripNumber, date, scheduledStart]
    cur.execute(query, recset)

    data = cur.fetchall()
    if not data:
        raise Exception("This trip offering does not exist.")
    
    scheduledArrival = data[0][3]

    query = "SELECT * FROM Stop WHERE StopNumber = %s"
    recset = [stopNum]
    cur.execute(query, recset)

    data = cur.fetchone()

    if data is None:
        raise Exception(f"Stop number {stopNum} does not exist.")
    
    query = """
        INSERT INTO ActualTripStopInfo 
            (TripNumber, Date, ScheduledStartTime, StopNumber, ScheduledArrivalTime, 
            ActualStartTime, ActualArrivalTime, NumberOfPassengerIn, NumberOfPassengerOut) 
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    recset = [tripNumber, date, scheduledStart, stopNum, scheduledArrival, actualStart, actualArrival, numPassIn, numPassOut]
    cur.execute(query, recset)

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
                ScheduledArrivalTime VARCHAR(255),
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
