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
    
    headers = ["startlocationname", "destinationname", "date", "scheduledstarttime", "scheduledarrivaltime", "drivername", "busid"]
    maxLengths = {header: len(header) for header in headers}
    for row in output:
        for header in headers:
            maxLengths[header] = max(maxLengths[header], len(str(row[header])))

    headerLine = "   ".join(header.capitalize().ljust(maxLengths[header]) for header in headers)
    print("\n")
    print(headerLine)
    print("=" * len(headerLine))
    
    for row in output:
        print("   ".join(str(row[header]).ljust(maxLengths[header]) for header in headers))

def editSchedule(cur, choice):
    if choice.lower() == "a":
        deleteOffering(cur)
    elif choice.lower() == "b":
        addOfferings(cur)
    elif choice.lower() == "c":
        changeDriver(cur)
    elif choice.lower() == "d":
        changeBus(cur)
    else:
        raise Exception("Invalid choice!")

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

    print("Offering successfully deleted!")

def addOfferings(cur):
    prompt = "\nWould you like to add those missing entries into the parent tables?\nEnter 'y' to add or 'n' to cancel: "
    numberToAdd = handleInput("How many would you like to add? (Enter [R] to return): ", int)

    if not numberToAdd:
        return

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
        if not confirmAddition(prompt):
            return

    addMissingEntries(cur, missingTrips, missingDrivers, missingBusIDs)

    addTripOfferingsToDB(cur, setOfTripOfferings)

    print("Trip offering successfuly added!")

def changeDriver(cur):
    prompt = "\nThe given driver does not exist! Would you like to add them? [y/n]: "
    tripNumber = handleInput("Enter the trip number for the offering or [R] to return: ", int)
    
    if not tripNumber:
        return
    
    date = handleInput("Enter the date for the trip offering in MM-DD-YYYY format: ", str)
    scheduledStart = handleInput("Enter the scheduled start time for the offering: ", str)

    query = "SELECT * FROM TripOffering WHERE TripNumber = %s AND Date = %s AND ScheduledStartTime = %s"
    recset = [tripNumber, date, scheduledStart]

    cur.execute(query, recset)

    if cur.fetchone() is None:
        raise Exception("The given trip offering does not exist!")
    
    driverName = handleInput("Enter the name of the driver you would like: ", str).lower()

    missingDrivers = checkMissing(cur, [driverName], "Driver", "DriverName")

    if missingDrivers:
        if confirmAddition(prompt):
            addMissingDrivers(cur, missingDrivers)
            print("New driver added!\n")
        else:
            return

    query = "UPDATE TripOffering SET DriverName = %s WHERE TripNumber = %s AND Date = %s AND ScheduledStartTime = %s"
    recset = [driverName, tripNumber, date, scheduledStart]

    cur.execute(query, recset)
    print("Driver updated successfully!")

def changeBus(cur):
    prompt = "\nThe given bus does not exist! Would you like to add it? [y/n]: "
    tripNumber = handleInput("Enter the trip number for the offering or [R] to return: ", int)
    
    if not tripNumber:
        return
    
    date = handleInput("Enter the date for the trip offering in MM-DD-YYYY format: ", str)
    scheduledStart = handleInput("Enter the scheduled start time for the offering: ", str)

    query = "SELECT * FROM TripOffering WHERE TripNumber = %s AND Date = %s AND ScheduledStartTime = %s"
    recset = [tripNumber, date, scheduledStart]

    cur.execute(query, recset)

    if cur.fetchone() is None:
        raise Exception("The given trip offering does not exist!")
    
    busID = handleInput("Enter the BusID you would like to use: ", int)

    missingBuses = checkMissing(cur, [busID], "Bus", "BusID")

    if missingBuses:
        if confirmAddition(prompt):
            addMissingBuses(cur, missingBuses)
            print("New bus added!\n")
        else:
            return

    query = "UPDATE TripOffering SET BusID = %s WHERE TripNumber = %s AND Date = %s AND ScheduledStartTime = %s"
    recset = [busID, tripNumber, date, scheduledStart]

    cur.execute(query, recset)
    print("Bus updated successfully!")

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

def confirmAddition(prompt):
    choice = handleInput(prompt, str).lower()
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

    if len(stopInfo) == 0:
        print("This trip has no stop data.")
        prompt = "Would you like to add stop information for this trip? (y/n): "
        if confirmAddition(prompt):
            addTripStopInfo(cur, tripNumber)
        return
    
    headers = ["tripnumber", "stopnumber", "sequencenumber", "drivingtime"]
    maxLengths = {header: len(header) for header in headers}

    for row in stopInfo:
        for header in headers:
            maxLengths[header] = max(maxLengths[header], len(str(row[header])))

    headerLine = "   ".join(header.capitalize().ljust(maxLengths[header]) for header in headers)
    print("\n")
    print(headerLine)
    print("=" * len(headerLine))
    
    for row in stopInfo:
        print("   ".join(str(row[header]).ljust(maxLengths[header]) for header in headers))

def addTripStopInfo(cur, tripNumber):
    stopCount = handleInput("How many stops would you like to add? ", int)
    for _ in range(stopCount):
        stopNum = handleInput("Enter Stop Number: ", int)
        sequenceNum = handleInput("Enter Sequence Number: ", str)
        drivingTime = handleInput("Enter Driving Time: ", str)

        cur.execute("SELECT * FROM Stop WHERE StopNumber = %s", (stopNum,))
        if cur.fetchone() is None:
            prompt = f"Stop number {stopNum} does not exist. Would you like to add it? (y/n): "
            if confirmAddition(prompt):
                addStop(cur, stopNum)
            else:
                return
        
        cur.execute("INSERT INTO TripStopInfo (TripNumber, StopNumber, SequenceNumber, DrivingTime) VALUES (%s, %s, %s, %s)", 
                    (tripNumber, stopNum, sequenceNum, drivingTime))

def addStop(cur, stopNum):
    stopAddress = handleInput("Enter Stop Address: ", str)
    cur.execute("INSERT INTO Stop (StopNumber, StopAddress) VALUES (%s, %s)", (stopNum, stopAddress))
    print(f"Stop {stopNum} added successfully.")

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
    
    headers = ["tripnumber", "date", "scheduledstarttime", "scheduledarrivaltime", "drivername", "busid"]
    maxLengths = {header: len(header) for header in headers}
    for trip in schedule:
        for header in headers:
            maxLengths[header] = max(maxLengths[header], len(str(trip[header])))

    headerLine = "   ".join(header.capitalize().ljust(maxLengths[header]) for header in headers)
    print("\n")
    print(headerLine)
    print("=" * len(headerLine))

    for trip in schedule:
        print("   ".join(str(trip[header]).ljust(maxLengths[header]) for header in headers))

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

    data = cur.fetchone()
    if data is None:
        raise Exception("This trip offering does not exist.")
    
    valuesList = list(data.values())
    scheduledArrival = valuesList[3]

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

def insertDummyData(conn, cursor):
    try:
        trips = [
            (1, 'Downtown Center', 'Greenfield Village'),
            (2, 'Eastside Station', 'Westside Terminal'),
            (3, 'North Plaza', 'South Beach'),
            (4, 'City Hall', 'Harbor Point'),
            (5, 'University Campus', 'Airport')
        ]
        for trip in trips:
            cursor.execute(f"""
                INSERT INTO Trip (TripNumber, StartLocationName, DestinationName)
                VALUES ({trip[0]}, '{trip[1].lower()}', '{trip[2].lower()}');
            """)

        buses = [
            (1, 'Volvo 9700', 2018),
            (2, 'Mercedes-Benz Tourismo', 2020),
            (3, 'Setra S417', 2019)
        ]
        for bus in buses:
            cursor.execute(f"""
                INSERT INTO Bus (BusID, Model, Year)
                VALUES ({bus[0]}, '{bus[1].lower()}', {bus[2]});
            """)

        drivers = [
            ('John Smith', '5551012021'),
            ('Emily Johnson', '5552023032'),
            ('Michael Brown', '5553034043')
        ]
        for driver in drivers:
            cursor.execute(f"""
                INSERT INTO Driver (DriverName, DriverTelephoneNumber)
                VALUES ('{driver[0].lower()}', '{driver[1]}');
            """)

        stops = [
            (1, '100 Main St.'),
            (2, '200 Oak Ave.'),
            (3, '300 Pine Rd.'),
            (4, '400 Elm St.'),
            (5, '500 Maple Dr.')
        ]
        for stop in stops:
            cursor.execute(f"""
                INSERT INTO Stop (StopNumber, StopAddress)
                VALUES ({stop[0]}, '{stop[1].lower()}');
            """)

        tripOfferings = [
            (1, '03-15-2023', '08:00 AM', '12:00 PM', 'John Smith', 1),
            (2, '03-16-2023', '09:00 AM', '01:00 PM', 'Emily Johnson', 2),
            (3, '03-17-2023', '10:00 AM', '02:00 PM', 'Michael Brown', 3),
            (4, '03-18-2023', '11:00 AM', '03:00 PM', 'John Smith', 1),
            (5, '03-19-2023', '12:00 PM', '04:00 PM', 'Emily Johnson', 2)
        ]
        for offering in tripOfferings:
            cursor.execute(f"""
                INSERT INTO TripOffering (TripNumber, Date, ScheduledStartTime, ScheduledArrivalTime, DriverName, BusID)
                VALUES ({offering[0]}, '{offering[1]}', '{offering[2]}', '{offering[3]}', '{offering[4].lower()}', {offering[5]});
            """)

        actualTripStopInfo = [
            (1, '03-15-2023', '08:00 AM', 1, '12:00 PM', '08:05 AM', '12:35 PM', 10, 5),
            (2, '03-16-2023', '09:00 AM', 2, '01:00 PM', '09:05 AM', '01:35 PM', 15, 8),
            (3, '03-17-2023', '10:00 AM', 3, '02:00 PM', '10:05 AM', '02:35 PM', 20, 10),
            (4, '03-18-2023', '11:00 AM', 4, '03:00 PM', '11:05 AM', '03:35 PM', 25, 12),
            (5, '03-19-2023', '12:00 PM', 5, '04:00 PM', '12:05 PM', '04:35 PM', 30, 15)
        ]
        for info in actualTripStopInfo:
            cursor.execute(f"""
                INSERT INTO ActualTripStopInfo (TripNumber, Date, ScheduledStartTime, StopNumber, ScheduledArrivalTime, ActualStartTime, ActualArrivalTime, NumberOfPassengerIn, NumberOfPassengerOut)
                VALUES ({info[0]}, '{info[1]}', '{info[2]}', {info[3]}, '{info[4]}', '{info[5]}', '{info[6]}', {info[7]}, {info[8]});
            """)

        tripStopInfo = [
            (1, 1, '1233', '1 Hour'),
            (2, 2, '2143', '1 Hour'),
            (3, 3, '3001', '3 Hours'),
            (4, 4, '4412', '2 Hours'),
            (5, 5, '5067', '5 Hours')
        ]

        for info in tripStopInfo:
            cursor.execute(f"""
                INSERT INTO TripStopInfo (TripNumber, StopNumber, SequenceNumber, DrivingTime)
                VALUES ({info[0]}, {info[1]}, '{info[2]}', '{info[3]}');
            """)

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Exception: {e}")