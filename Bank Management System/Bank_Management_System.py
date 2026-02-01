import json
import random
import string
from pathlib import Path

class Bank:
    database = 'data.json'
    data = []

    try:
        if Path(database).exists():
           with open(database, 'r') as fs:
                data = json.load(fs)
        else:
            print("File not found")

    except Exception as err:
        print(err)


    @staticmethod
    def update():
        with open(Bank.database, 'w') as fs:
            fs.write(json.dumps(Bank.data))

    def Createaccount(self):
        info = {
            "username": input("Enter your username: "),
            "age": int(input("Enter your age: ")),
            "email": input("Enter your email: "),
            "pin": input("Enter your pin:"),
            "accountNo" : 1234,
            "balance" : 0,
        }

        if info['age'] < 18 or len(str(info['pin'])) != 4:
            self.data.append(info)
            print("You are not eligible to open an account")
        else:
            print("Account created successfully")

            for i in info:
                print(f"{i} : {info[i]}")
            print("Thank you for using our service, Note your account number")


            Bank.data.append(info)
            Bank.update()

user = Bank()

print("Press 1 for creating an account")
print("Press 2 for Depositing the money in the bank")
print("Press 3 for withdrawing the money from the bank")
print("Press 4 for viewing the details of the account")
print("Press 5 for updating the details of the account")
print("Press 6 for deleting the account")


check = int(input("Enter your choice: "))

if check == 1:
    user.Createaccount()