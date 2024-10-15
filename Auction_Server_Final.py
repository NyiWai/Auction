import datetime as dt
import socket
import Encry_Decrypt
import os, pytz
from datetime import datetime, timedelta

class Server:
    def __init__(self):
        self.encrypt = Encry_Decrypt.A3Encryption()
        self.decrypt = Encry_Decrypt.A3Decryption()
        self.server_ip = "localhost"
        self.server_port = 10004

    def main(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.server_ip, self.server_port))
        server.listen()
        print("Server listen on port: {} and ip {}".format(self.server_port, self.server_ip))
        try:
            while True:
                client, address = server.accept()
                print("Accepted Connection from - {} : {}".format(address[0], address[1]))
                self.client_control(client)
        except Exception as error:
            print(error)

    def client_control(self, client_sock):
        rc = RequestControl()
        rc.load_data_to_dict()
        with client_sock as sock:
            from_client = client_sock.recv(4096)
            data_list = from_client.decode("utf-8")
            decrypted = self.decrypt.startDecryption(data_list)
            print("#:", decrypted)
            decrypted_list = decrypted.split(' ')
            if decrypted_list[0] == 'reg':
                rc.register(decrypted_list, sock)
            elif decrypted_list[0] == 'log':
                rc.login(decrypted_list, sock)
            elif decrypted_list[0] == 'emailcheck':
                rc.email_checking(decrypted_list, sock)
            elif decrypted_list[0] == 'check_E_P':
                rc.checking_email_pass(decrypted_list, sock)
            elif decrypted_list[0] == 'load_data':
                rc.load_auctions(decrypted_list, sock)
            elif decrypted_list[0] == "create_auction":
                rc.create_auctions(decrypted_list, sock)
            elif decrypted_list[0] == "item_existOrNot":
                rc.item_exist_orNot(decrypted_list, sock)
            elif decrypted_list[0] == "place_bid":
                rc.place_bid_session(decrypted_list, sock)

class Auction:
    def __init__(self, item, start_price, end_time):
        self.item = item
        self.current_bid_amount = int(start_price)
        self.highest_bidder = None
        self.end_time = end_time

    def place_bid(self, amount_bid, user):
        current_date = dt.datetime.now(pytz.timezone('Asia/Yangon'))
        current_date = current_date.strftime("%d-%m-%Y %H:%M")
        current_date = datetime.strptime(current_date, "%d-%m-%Y %H:%M")
        end_time = datetime.strptime(self.end_time, "%d-%m-%Y %H:%M")
        if current_date < end_time:
            if int(amount_bid) > self.current_bid_amount:
                self.current_bid_amount, self.highest_bidder = amount_bid, user
                return f"Highest bidder, '{user}' bids {amount_bid} for {self.item}"
            else:
                return f"Sorry '{user}', your bid amount's not enough. Current bid amount is {str(self.current_bid_amount)}"
        else:
            return "Time_Over"

class RequestControl:
    def __init__(self):
        self.auctions = {}
        self.server = Server()
        self.encrypt = self.server.encrypt
        self.decrypt = self.server.decrypt

    def load_auctions(self, datalist, sock):
        data = ""
        if os.path.exists("auctions.txt"):
            with open("auctions.txt", "r") as file:
                for line in file:
                    item, current_bid, highest_bidder, end_time = line.strip().split(',')
                    data += f"{item},{current_bid},{highest_bidder},{end_time},"
            encry = self.encrypt.start_encryption(data, datalist[-1])
            sock.send(bytes(encry, 'utf-8'))

    def register(self, data_list, sock):
        name = ""
        for i in range(3, (len(data_list) - 2)):
            name += data_list[i] + " "
        name = name.rstrip()
        contant = (data_list[len(data_list) - 2])
        with open("user_info.txt", "a+") as file:
            file.write(f"{data_list[1]},{data_list[2]},{name},{contant}\n")
        sms = "Registration complete!"
        encrypt_sms = self.encrypt.start_encryption(sms, data_list[5])
        sock.send(bytes(encrypt_sms, "utf-8"))

    def email_checking(self, datalist, sock):
        if os.path.exists("user_info.txt"):
            with open("user_info.txt", "r") as file:
                List1 = []
                count = 0
                for line in file:
                    List = line.strip().split(',')
                    List1.append(List)
                    if datalist[1] == List1[count][0]:
                        Exist = self.encrypt.start_encryption("exist", datalist[2])
                        sock.send(bytes(Exist, "utf-8"))
                    count += 1
                notExist = self.encrypt.start_encryption("notExist", datalist[2])
                sock.send(bytes(notExist, "utf-8"))
        else:
            notExist = self.encrypt.start_encryption("notExist", datalist[2])
            sock.send(bytes(notExist, "utf-8"))

    def checking_email_pass(self, datalist, sock):
        if os.path.exists("user_info.txt"):
            with open("user_info.txt", "r") as file:
                List1 = []
                count = 0
                for line in file:
                    List = line.strip().split(",")
                    List1.append(List)
                    if datalist[1] == List1[count][0] and datalist[2] == List1[count][1]:
                        sms = List1[count][2] + " " + "Exist"
                        Exist = self.encrypt.start_encryption(sms, datalist[-1])
                        sock.send(bytes(Exist, "utf-8"))
                    count += 1
                NExist = self.encrypt.start_encryption("notExist", datalist[-1])
                sock.send(bytes(NExist, "utf-8"))
        else:
            NExist = self.encrypt.start_encryption("notExist", datalist[-1])
            sock.send(bytes(NExist, "utf-8"))

    def save_auctions(self, auctions):
        with open("auctions.txt", "w") as file:
            for item, auction in auctions.items():
                file.write(f"{item},{auction.current_bid_amount},{auction.highest_bidder},{auction.end_time}\n")

    def create_auctions(self, decrypted_list, sock):
        with open("auctions.txt", 'a+') as file:
            file.write(f"{decrypted_list[1]},{decrypted_list[2]},{decrypted_list[3]},{decrypted_list[4]} {decrypted_list[5]}\n")
        sms = "Create auction success"
        encrypt_sms = self.encrypt.start_encryption(sms, decrypted_list[-1])
        sock.send(bytes(encrypt_sms, 'utf-8'))

    def date_time(self):
        current_date = dt.datetime.now(pytz.timezone('Asia/Yangon'))
        Day = int(input("Amount of days that auction will end : "))
        days_later = current_date + timedelta(days=Day)
        return days_later.strftime('%d-%m-%Y %H:%M')

    def item_exist_orNot(self, data_list, sock):
        if data_list[1] in self.auctions:
            sms = self.encrypt.start_encryption('Exist', data_list[-1])
            sock.send(bytes(sms, 'utf-8'))
        else:
            sms = self.encrypt.start_encryption('notExist', data_list[-1])
            sock.send(bytes(sms, 'utf-8'))

    def load_data_to_dict(self):
        self.auctions = {}
        if os.path.exists("auctions.txt"):
            with open("auctions.txt", "r") as file:
                for line in file:
                    item, current_bid, highest_bidder, end_time = line.strip().split(',')
                    self.auctions[item] = Auction(item, float(current_bid), end_time)
                    self.auctions[item].highest_bidder = highest_bidder
        return self.auctions

    def place_bid_session(self, data_list, sock):
        name = ''
        for i in range(3, len(data_list) - 1):
            name += data_list[i] + " "
        user = name.rstrip()
        return_place_bid = self.auctions[data_list[1]].place_bid(float(data_list[2]), user)
        self.save_auctions(self.auctions)
        sms = self.encrypt.start_encryption(return_place_bid, data_list[-1])
        sock.send(bytes(sms, 'utf-8'))


if __name__ == "__main__":
    global rc
    server = Server()
    server.main()
