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
    
def switch(choice):
    match choice:
        case "a":
            print("1")
        case "b":
            print("2")
        case "c":
            print("3")
        case "d":
            print("4")
        case "e":
            print("5")
        case "f":
            print("6")
        case "g":
            print("7")
        case "h":
            print("8")
        case "q":
            print("Goodbye.")
        case _:
            print("Invalid choice.")

if __name__ == '__main__':
    conn = connectDataBase()
    cursor = conn.cursor()

    choice = ""
    while choice != "q":
        printMenu()
        choice = input("Enter choice: ")

        switch(choice)