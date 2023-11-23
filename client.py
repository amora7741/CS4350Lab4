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
    match choice.lower():
        case "a":
            while True:
                try:
                    startLocation = input("Enter the starting location: ").lower()
                    destination = input("Enter the destination: ").lower()
                    date = input("Enter the date in MM-DD-YYYY format: ")

                    displaySchedule(cur, startLocation, destination, date)

                    break
                except Exception as e:
                    print(f"Exception: {e}")
                    con.rollback()

        case "b":
            print("2")
        case "c":
            while True:
                try:
                    tripNumber = getValidInput("Enter trip number: ", int)

                    displayStops(cur, tripNumber)

                    break
                
                except Exception as e:
                    print(f"Exception: {e}")
                    con.rollback()
        case "d":
            print("4")
        case "e":
            while True:
                try:
                    driverName = input("Enter driver name: ")
                    phoneNumber = input("Enter driver's phone number: ")

                    phoneNumber = ''.join(filter(str.isdigit, phoneNumber))

                    addDriver(cur, driverName, phoneNumber)
                    con.commit()

                    print("\nDriver successfully added!")

                    break
                except Exception as e:
                    print(f"Exception: {e}")
                    con.rollback()
        case "f":
            while True:
                try:
                    busID = getValidInput("Enter busID: ", int)
                    model = input("Enter model: ")
                    year = getValidInput("Enter year: ", int)

                    addBus(cur, busID, model, year)
                    con.commit()

                    print("\nBus successfully added!")

                    break
                except Exception as e:
                    print(f"Exception: {e}")
                    con.rollback()

        case "g":
            while True:
                try:
                    busID = getValidInput("Enter busID: ", int)

                    deleteBus(cur, busID)
                    con.commit()

                    print(f"Bus {busID} successfully deleted!")
                    break

                except Exception as e:
                    print(f"Exception: {e}")
                    con.rollback()


        case "h":
            while True:
                try:
                    tripNumber = getValidInput("Enter the trip number for the offering: ", int)
                    date = input("Enter the date for the offering in MM-DD-YYYY format: ")
                    scheduledStart = input("Enter the scheduled start time for the offering: ")
                    actualStartTime = input("Enter the actual start time of the trip: ")
                    actualArrivalTime = input("Enter the actual arrival time of the trip: ")
                    stopNumber = getValidInput("Enter the stop number: ", int)
                    numberofPassengersIn = getValidInput("How many passengers entered at this stop? ", int)
                    numberofPassengersOut = getValidInput("How many passengers exited at this stop? ", int)

                    insertTripInfo(cur, tripNumber, date, scheduledStart, actualStartTime, actualArrivalTime, stopNumber, numberofPassengersIn, numberofPassengersOut)
                    con.commit()

                    print("Trip info successfully added!")

                except Exception as e:
                    print(f"Exception: {e}")
                    con.rollback()


        case "q":
            cur.close()
            con.close()
            print("Goodbye.")
        case _:
            print("Invalid choice.")

def getValidInput(prompt, inputType):
    while True:
        try:
            userInput = inputType(input(prompt))
            return userInput
        except ValueError:
            print(f"Invalid input. Please enter a valid {inputType.__name__}.")

if __name__ == '__main__':
    conn = connectDataBase()
    cur = conn.cursor()

    createTables(conn, cur)

    choice = ""
    while choice != "q":
        printMenu()
        choice = input("Enter choice: ")

        switch(choice, cur, conn)