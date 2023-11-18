from dbfunctions import *

def printMenu():
    print("""
[1] Find the schedule of all trips on a given date
[2] Edit the trip offerings schedule
[3] Display the stops of a given trip
[4] Display the weekly schedule of a given driver and date
[5] Add a driver
[6] Add a bus
[7] Delete a bus
[8] Insert the actual data of a given trip offering
[0] Exit program
""")

if __name__ == '__main__':
    conn = connectDataBase()

    cursor = conn.cursor()

    printMenu()