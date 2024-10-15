import pytz, sys
import datetime as dt
import socket
import S_Encrypt_and_Decrypt as E_D
from colorama import Fore, Style
from datetime import datetime, timedelta


class Auction_Client:
    def __init__(self):
        self.target_ip = "localhost"
        self.target_port = 10004
        self.userKey = self.getting_key()
        self.encrypt = E_D.A3Encryption()
        self.decrypt = E_D.A3Decryption()

    def getting_key(self):
        userKey: str = input("Enter your encryption key for the whole process : ")
        return userKey

    def client_runner(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.target_ip, self.target_port))
        return client

    def client_menu(self):
        print("This is client menu\n")
        user_data = input("reg:to register\nlog:to login\nquit:to exit- ")
        if user_data == 'reg':
            self.registration()
        elif user_data == "log":
            self.login()
        elif user_data == "quit":
            sys.exit()

    def date_time(self):
        current_date = dt.datetime.now(pytz.timezone('Asia/Yangon'))
        Day = int(input("Amount of days that auction will end : "))
        days_later = current_date + timedelta(days=Day)
        return days_later.strftime('%d-%m-%Y %H:%M')

    def count_date_time_to_show(self, date):
        current_date = dt.datetime.now(pytz.timezone('Asia/Yangon'))
        current_date = current_date.strftime("%d-%m-%Y %H:%M")
        current_date = datetime.strptime(current_date, "%d-%m-%Y %H:%M")
        end_date = datetime.strptime(date, "%d-%m-%Y %H:%M")
        left_date = end_date - current_date
        return (f"{left_date}")

    def create_auction(self):
        client = self.client_runner()
        item_name = input("Enter the item name: ")
        starting_price = float(input("Enter the starting price: $"))
        highest_bidder = None #check this shit
        Day = self.date_time()
        sms = "create_auction" + " " + item_name + " " + str(starting_price) + " " + str(highest_bidder) + " " + Day + " " + self.userKey
        encrypt_data = self.encrypt.start_encryption(sms, self.userKey)
        client.send(bytes(encrypt_data, 'utf-8'))
        recv_data = client.recv(4096).decode('utf-8')
        client.close()

    def load_auctions(self):
        CLIENT = self.client_runner()
        sms = 'load_data' + " " + self.userKey
        encrypted_data = self.encrypt.start_encryption(sms, self.userKey)
        CLIENT.send(bytes(encrypted_data, 'utf-8'))
        data_list = CLIENT.recv(4096).decode('utf-8')
        decrypted_data = self.decrypt.startDecryption(data_list)
        List_Data = decrypted_data.split(",")
        List_Data.pop()
        flag_list = []
        child_list = []
        amount_list = len(List_Data) // 4
        x = 0
        y = 4
        for i in range(0, amount_list):
            for j in range(x, y):
                child_list.append(List_Data[j])
            flag_list.append(child_list)
            child_list = []
            x += 4
            y += 4
        CLIENT.close()
        return flag_list

    def show_all_items(self, auctions):
        if len(auctions) != None:
            print("\nHere is auction items list")
            print("**************************\n")
            for i in range(0, len(auctions)):
                item, current_pid, highest_bidder, End_time = auctions[i][0], auctions[i][1], auctions[i][2], auctions[i][3]
                end_time = self.count_date_time_to_show(End_time)
                if highest_bidder == "None":
                    print(f"{item} (Nobody has bidded yet!)\n(highest bid => {current_pid}) {end_time} left\n")
                else: 
                    print(f"{item} ({highest_bidder} is highest bidder)\n(highest bid => {current_pid}) {end_time} left\n")
            return 1
        else:
            return 0

    def email_check_inTXTDB(self, email):
        data = "emailcheck" + " " + email + " " + self.userKey
        Client = self.client_runner()
        encry = E_D.A3Encryption()
        decry = E_D.A3Decryption()
        encrypted_data = encry.start_encryption(data, self.userKey)
        sms = bytes(encrypted_data, "utf-8")
        Client.send(sms)
        received = Client.recv(4096)
        received = received.decode("utf-8")
        received = decry.startDecryption(received)
        if received == "notExist":
            Client.close()
            return True
        else:
            Client.close()
            return False

    def check_email_pass_user(self, email, password):
        client = self.client_runner()
        text = "check_E_P" + " " + email + " " + password + " " + self.userKey
        encrypted_data = self.encrypt.start_encryption(text, self.userKey)
        sms = bytes(encrypted_data, 'utf-8')
        client.send(sms)
        recv = client.recv(4096).decode('utf-8')
        decrypted_data = self.decrypt.startDecryption(recv)
        client.close()
        return decrypted_data

    def registration(self):
        while True:
            email = input("Enter email address you want - ")
            flag = self.email_checking(email)
            if flag == 1:
                pass
            else:
                print(Fore.RED + "Email Form Invalid\nTry Again!")
                print(Style.RESET_ALL)
            check = self.email_check_inTXTDB(email)
            if check and flag == 1:
                break
            elif flag == 1:
                print(Fore.RED + "This email already exist!")
                print(Style.RESET_ALL)
        while True:
            pass1 = input("Enter your password to register : ")
            pass_check = self.password_check(pass1)
            if pass_check == 1:
                pass2 = input("Confirm your password again to register : ")
                if pass2 == pass1:
                    break
                else:
                    print(Fore.RED + "*Msg* : You need to put same password above to confirm! Plz try again")
                    print(Style.RESET_ALL)
            else:
                print(Fore.RED + "One lower case, one upper case, one number and one special char have to include in your password!")
                print(Style.RESET_ALL)
        name = input("Enter your name : ")
        content = input("Enter your phone number : ")
        data_form = "reg" + " " + email + " " + pass1 + " " + name + " " + content + " " + self.userKey
        client = self.client_runner()
        encrypted_data = self.encrypt.start_encryption(data_form, self.userKey)
        sms = bytes(encrypted_data, "utf-8")
        client.send(sms)
        recv = client.recv(4096).decode("utf-8")
        self.decrypt.startDecryption(recv)
        client.close()
        if recv:
            print(Fore.GREEN + "Registration Success!")
            print(Style.RESET_ALL)
            self.place_bid_session(name)

    def place_bid_session(self, user):
        global bid_amount
        while True:
            auctions = self.load_auctions()
            client = self.client_runner()
            temp = self.show_all_items(auctions)
            if temp == 0:
                print(Fore.RED + "There is no auction items.")
                print(Style.RESET_ALL)
                break
            auction_name = input("Enter the item name for the auction : ")
            sms = "item_existOrNot" + " " + auction_name + " " + self.userKey
            sms = self.encrypt.start_encryption(sms, self.userKey)
            client.send(bytes(sms, 'utf-8'))
            recv_data = client.recv(4096).decode('utf-8')
            decrypted_data = self.decrypt.startDecryption(recv_data)
            client.close()
            if decrypted_data == 'Exist':
                try:
                    bid_amount = float(input("Enter your bid: $ "))
                except ValueError:
                    print("Invalid input. Please enter a valid bid amount.")
                Client = self.client_runner()
                sms = "place_bid" + " " + auction_name + " " + str(bid_amount) + " " + user + " " + self.userKey
                encrypt_data = self.encrypt.start_encryption(sms, self.userKey)
                Client.send(bytes(encrypt_data, 'utf-8'))
                Recv_Data = Client.recv(4096).decode('utf-8')
                Decrypt_Data = self.decrypt.startDecryption(Recv_Data)
                Client.close()
                if Decrypt_Data == "Time_Over":
                    print("Auction time for this item is over. Sorry!!!")
                    pass
                elif Decrypt_Data[0:5] == "Sorry":
                    print(Fore.RED + Decrypt_Data)
                    print(Style.RESET_ALL)
                    pass
                else:
                    print(Fore.GREEN + Decrypt_Data)
                    print(Style.RESET_ALL)
                check = input("Keep placing bid? y/n - ")
                if check.lower() == 'y':
                    pass
                elif check.lower() == 'n':
                    break
            else:
                print(Fore.RED + f"No active auction found with the item name '{auction_name}'.")
                print(Style.RESET_ALL)

    def login(self):
        global user
        print("\nThis is log-in session.")
        print("***********************")
        while True:
            email = input("Enter your email (login): ")
            password = input("Enter your password : ")
            flag = self.check_email_pass_user(email, password)
            flag = flag.split(" ")
            name = ""
            flag1 = flag[-1]
            for i in range(0, len(flag) - 1):
                name += flag[i] + " "
            user = name.rstrip()
            if flag1 == 'Exist':
                while True:
                    choice = input("\n1 to create auction\n2 to place bid\n3 to quit - ")
                    if choice == '1':
                        self.create_auction()
                    elif choice == '2':
                        self.place_bid_session(user)
                    elif choice == "3":
                        break
                    else:
                        print(Fore.RED + "Please enter valid numbers!")
                        print(Style.RESET_ALL)
                break
            else:
                print(Fore.RED + "Email or password is wrong!")
                print(Style.RESET_ALL)

    def password_check(self, password):
        charSpecial = "[@_!#$%^&*()<>?/\|}{~:]"
        charNum = "1234567890"
        count_s, count_l, count_i, count_Sp = 0, 0, 0, 0
        for i in password:
            if i.islower() and count_s < 1:
                count_s += 1
            elif i.isupper() and count_l < 1:
                count_l += 1
            elif (i in charSpecial) and count_Sp < 1:
                count_Sp += 1
            elif (i in charNum) and count_i < 1:
                count_i += 1
        if count_s == 1 and count_i == 1 and count_l == 1 and count_Sp == 1:
            return 1
        else:
            return 0

    def email_checking(self, r_email):
        name_flag: int = 0
        char_counter = 0
        for i in range(len(r_email)):
            if r_email[i] == "@":
                break
            char_counter += 1
        mail_name = r_email[0:char_counter]
        mail_form = r_email[char_counter:]
        name_flag = 0
        email_flag = 0
        for i in range(len(mail_name)):
            aChar = mail_name[i]
            if (ord(aChar) > 31 and ord(aChar) < 48) or (ord(aChar) > 57 and ord(aChar) < 65) or (
                    ord(aChar) > 90 and ord(aChar) < 97) or (ord(aChar) > 122 and ord(aChar) < 128):
                name_flag = -1
                break
        email_form = "@gmail.com"
        if email_form == mail_form:
            email_flag = 1
        if name_flag == -1 or email_flag == 0:
            return -1
        else:
            return 1


if __name__ == "__main__":
    Auction_Client = Auction_Client()
    while True:
        Auction_Client.client_menu()
