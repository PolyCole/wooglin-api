"""
    Author: Cole Polyak
    Date: 19 January 2021
    Purpose: This script populates the database using an encrypted DB Seed file.
"""

import datetime
from restapi.models.members import Member
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import string
import random
import os


'''

Game plan:


 - check for encryption key env variable. 
    * throw hands if it doesn't exist.
 - check for encrypted seed file
    * throw hands if it doesn't exist.
    
 - create file wherein encrypted credentials will live.
    
 - read line from file, separate arguments by comma.
    * send each argument to a decrypt method. 
    
 - whole, if name == 'Cole Polyak', jazz. 
 
 - continue adding member to db. 
 
 - when it comes time to create the user account
    * when creating password, generate random password.
    * add user account to the DB.
    * encrypt randomly generated password, ENSURE TEMP_PASSWORD is set to true.
    * write encrypted username and password to output file.
 - profit. 

'''


class Command(BaseCommand):
    help = 'Seeds the database based on an encrypted seed file, and encryption key stored in DB_ENCRYPTION_KEY.'

    def handle(self, *args, **options):
        print("Attempting to populate database...")
        start_time = datetime.datetime.now().replace(microsecond=0)

        try:
            key = os.environ['DB_ENCRYPTION_KEY']
            key.encode()
        except KeyError as e:
            end_time = datetime.datetime.now().replace(microsecond=0)
            print(e)
            print("Operation failed in " + str(end_time - start_time))

        filename = input("Please enter the name of the encrypted DB seed:")

        try:
            file = open(filename, "r")
        except FileNotFoundError as e:
            end_time = datetime.datetime.now().replace(microsecond=0)
            print(e)
            print("Operation failed in " + str(end_time - start_time))

        output = open("encrypted_credentials.txt", "w")

        file.readline()

        current_line = file.readline()
        count = 1
        while current_line != '':
            processed = current_line.split(",")
            processed = self.decrypt(processed, key)

            name = processed[0]

            if name == "Cole Polyak":
                account = User.objects.get(username="cole")
            else:
                username = name.lower().replace(" ", ".")
                password = self.get_password()

                output.write(self.encrypt(username, key) + "," + self.encrypt(password, key))

                account = User.objects.create_user(
                    username=username,
                    email=processed[5].strip(),
                    password=password
                )

            brother = Member.objects.get_or_create(
                user=account,
                name=name,
                first_name=processed[1],
                last_name=processed[2],
                legal_name=processed[3],
                address=processed[4],
                email=processed[5],
                phone=processed[6],
                rollnumber=processed[7],
                member_score=processed[8],
                inactive_flag=self.get_boolean(processed[9]),
                abroad_flag=self.get_boolean(processed[10]),
                present=processed[11],
                position=self.get_position(processed[12])
            )[0]

            count += 1
            current_line = file.readline()
        
        output.close()
        end_time = datetime.datetime.now().replace(microsecond=0)
        print("Populating complete...")
        print("Wrote " + str(count) + " entries in " + str(end_time - start_time))

    def get_password(self):
        char_pool = string.ascii_lowercase + string.ascii_uppercase + string.punctuation + string.digits
        char_pool.replace("`", "")
        char_pool.replace("|", "")
        temp = random.sample(char_pool, 12)
        return "".join(temp)

    def get_boolean(self, boolean):
        if boolean == "FALSE":
            return False
        elif boolean == "TRUE":
            return True
        else:
            raise Exception("Something went wrong when reading flags." + "\n" + str(boolean))

    def get_position(self, pos):
        if len(pos.strip()) == 0:
            return "Brother"
        return pos.strip()

    def encrypt(self, value, key):
        f = Fernet(key)
        encrypted = f.encrypt(value.encode())
        return encrypted.decode()

    def decrypt(self, list, key):
        return_list = []
        f = Fernet(key)

        for value in list:
            decrypted = f.decrypt(value.encode())
            return_list.append(decrypted.decode())

        return return_list