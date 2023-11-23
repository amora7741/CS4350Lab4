from dbfunctions import *

def printMenu():
    print("""
[a] Find the schedule of all trips on a given date
[b] Edit the trip offerings schedule
[c] Display the stops of a given trip
[d] Display the weekly schedule of a given driver and date
[e] Add a driver
[f] Add a bus
[g] Delete a bus
[h] Insert the actual data of a given trip offering
[q] Exit program
""")
    
def switch(choice, cur, con):
    if choice.lower() == "a":
        startLocation = handleInput("Enter the starting location or [R] to return: ", str)
        if startLocation:
            destination = handleInput("Enter the destination: ", str)
            date = handleInput("Enter the date in MM-DD-YYYY format: ")
            try:
                displaySchedule(cur, startLocation, destination, date)
            except Exception as e:
                print(f"Exception: {e}")
                con.rollback()

    elif choice.lower() == "b":
        pass

    elif choice.lower() == "c":
        tripNumber = handleInput("Enter trip number or [R] to return: ", int)
        if tripNumber is not None:
            try:
                displayStops(cur, tripNumber)
            except Exception as e:
                print(f"Exception: {e}")
                con.rollback()

    elif choice.lower() == "d":
        pass

    elif choice.lower() == "e":
        driverName = handleInput("Enter driver name or [R] to return: ", str)
        if driverName:
            phoneNumber = handleInput("Enter driver's phone number: ", str)
            try:
                addDriver(cur, driverName, phoneNumber)
                con.commit()
                print("\nDriver successfully added!")
            except Exception as e:
                print(f"Exception: {e}")
                con.rollback()

    elif choice.lower() == "f":
        busID = handleInput("Enter busID or [R] to return: ", int)
        if busID is not None:
            model = handleInput("Enter model: ", str)
            year = handleInput("Enter year: ", int)
            try:
                addBus(cur, busID, model, year)
                con.commit()
                print("\nBus successfully added!")
            except Exception as e:
                print(f"Exception: {e}")
                con.rollback()

    elif choice.lower() == "g":
        busID = handleInput("Enter busID to delete or [R] to return: ", int)
        if busID is not None:
            try:
                deleteBus(cur, busID)
                con.commit()
                print(f"Bus {busID} successfully deleted!")
            except Exception as e:
                print(f"Exception: {e}")
                con.rollback()

    elif choice.lower() == "h":
        tripNumber = handleInput("Enter the trip number for the offering or [R] to return: ", int)
        if tripNumber is not None:
            date = handleInput("Enter the date for the offering in MM-DD-YYYY format: ")
            scheduledStart = handleInput("Enter the scheduled start time for the offering: ")
            actualStartTime = handleInput("Enter the actual start time of the trip: ")
            actualArrivalTime = handleInput("Enter the actual arrival time of the trip: ")
            stopNumber = handleInput("Enter the stop number: ", int)
            numberofPassengersIn = handleInput("How many passengers entered at this stop? ", int)
            numberofPassengersOut = handleInput("How many passengers exited at this stop? ", int)
            try:
                insertTripInfo(cur, tripNumber, date, scheduledStart, actualStartTime, actualArrivalTime, stopNumber, numberofPassengersIn, numberofPassengersOut)
                con.commit()
                print("Trip info successfully added!")
            except Exception as e:
                print(f"Exception: {e}")
                con.rollback()

    elif choice.lower() == "q":
        cur.close()
        con.close()
        print("Goodbye.")
    else:
        print("Invalid choice.")


def handleInput(prompt, inputType=None):
    while True:
        userInput = input(prompt)
        if userInput.lower() == 'r':
            return None
        try:
            return inputType(userInput) if inputType else userInput
        except ValueError:
            print(f"Invalid input. Please enter a valid {inputType.__name__}.")

if __name__ == '__main__':
    conn = connectDataBase()
    cur = conn.cursor()

    createTables(conn, cur)

    while True:
        printMenu()
        choice = input("Enter choice: ")
        if choice.lower() == 'q':
            break
        switch(choice, cur, conn)