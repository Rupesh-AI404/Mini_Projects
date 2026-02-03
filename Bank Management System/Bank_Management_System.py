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


    @classmethod
    def __update__(cls):
        with open(cls.database, 'w') as fs:
            fs.write(json.dumps(Bank.data))


    @classmethod
    def __accountgenerate(cls):
        alpha = random.choices(string.ascii_letters, k = 3)
        num = random.choices(string.digits, k = 3)
        spchar = random.choices("!@#$%^&*_", k = 1)
        id = alpha + num + spchar
        random.shuffle(id)
        return ''.join(id)

    def Createaccount(self):
        info = {
            "username": input("Enter your username: "),
            "age": int(input("Enter your age: ")),
            "email": input("Enter your email: "),
            "pin": input("Enter your pin:"),
            "accountNo" : Bank.__accountgenerate(),
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
            Bank.__update__()


    def depositmoney(self):
        accountNo = input("Enter your account number: ")
        pin = input("Enter your pin: ")

        userdata = [i for i in Bank.data if i['accountNo'] == accountNo and i['pin'] == pin]

        if userdata == False:
            print("Data is not Found")
        else:
            amount = int(input("Enter the amount to be deposited: "))
            if amount >= 10000 or amount <= 0:
                print("Sorry, you can deposit amount between 1 to 10000 only")
            else:

                print(userdata)

                userdata[0]['balance'] += amount
                print(f"Your amount {amount} is successfully deposited")
                Bank.__update__()


    def withdrawmoney(self):
        accountNo = input("Enter your account number: ")
        pin = input("Enter your pin: ")

        userdata = [i for i in Bank.data if i['accountNo'] == accountNo and i['pin'] == pin]

        if userdata == False:
            print("Data is not Found")
        else:
            amount = int(input("Enter the amount to be withdrawn: "))
            if userdata[0]['balance'] < amount:
                print("Sorry, you can withdraw amount")
            else:

                print(userdata)

                userdata[0]['balance'] -= amount
                print(f"Your amount {amount} is successfully withdrew")
                Bank.__update__()


    def showdetails(self):
        accountNo = input("Enter your account number: ")
        pin = input("Enter your pin: ")

        userdata = [i for i in Bank.data if i['accountNo'] == accountNo and i['pin'] == pin]

        print("Your account details are as follows:")
        for i in userdata[0]:
            print(f"{i} : {userdata[0][i]}")



    def updatedetails(self):
        accountNo = input("Enter your account number: ")
        pin = input("Enter your pin: ")

        userdata = [i for i in Bank.data if i['accountNo'] == accountNo and i['pin'] == pin]

        if not userdata:
            print("Data is not Found")
            return
        else:
            print("You can only change the age, account number and balance")
            print("Fill the details you want to change or leave it blank if you don't want to change it")

            newdata = {
                "username" : input("Enter your new name: "),
                "email" : input("Enter your new email: "),
                "pin" : input("Enter your new pin: "),
            }

            if newdata["username"] == "":
                newdata["username"] = userdata[0]['username']
            if newdata["email"] == "":
                newdata["email"] = userdata[0]['email']
            if newdata["pin"] == "":
                newdata["pin"] = userdata[0]['pin']

            newdata['age'] = userdata[0]['age']
            newdata['accountNo'] = userdata[0]['accountNo']
            newdata['balance'] = userdata[0]['balance']


            if type(newdata['pin']) == str:
                newdata['pin'] = int(newdata['pin'])

            for i in newdata:
                if newdata[i] == userdata[0][i]:
                    continue
                else:
                    userdata[0][i] = newdata[i]

            Bank.__update__()
            print("Your details are updated successfully")

    def Delete(self):
        accountNo = input("Enter your account number: ")
        pin = input("Enter your pin: ")

        userdata = [i for i in Bank.data if i['accountNo'] == accountNo and i['pin'] == pin]

        if not userdata:  # FIXED: Changed from 'if userdata == False:'
            print("Data is not Found")
        else:
            check = input("Are you sure you want to delete your account?(y/n): ")
            if check == "y":
                index = Bank.data.index(userdata[0])
                Bank.data.pop(index)
                Bank.__update__()
                print("Your account is deleted successfully")




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


if check == 2:
    print("Depositing the money in the bank.")
    user.depositmoney()


if check == 3:
    print("Withdrawing the money from the bank.")
    user.withdrawmoney()


if check == 4:
    print("Viewing the details of the account.")
    user.showdetails()


if check == 5:
    print("Updating the details of the account.")
    user.updatedetails()


if check == 6:
    print("Deleting the account.")
    user.Delete()