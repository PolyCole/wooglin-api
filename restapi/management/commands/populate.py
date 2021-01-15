import datetime
from restapi.models.members import Member
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

'''
    Author: Cole Polyak
    Date: 20 December 2020
    Purpose: This script populates the database using the DB_SEED file. 
'''


class Command(BaseCommand):
    help = 'Writes the DB_SEED Data to the Member and User tables.'

    def handle(self, *args, **options):
        print("Populating database...")
        start_time = datetime.datetime.now().replace(microsecond=0)

        file = open("/home/cole/Desktop/brothers.csv", "r")
        file.readline()

        current_line = file.readline()
        count = 1
        while current_line != '':
            processed = current_line.split(",")

            name = processed[0]

            if name == "Cole Polyak":
                account = User.objects.get(username="cole")
            else:
                account = User.objects.create_user(
                    username=name.lower().replace(" ", "."),
                    email=processed[5].strip(),
                    password=self.get_password(name, processed[7])
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

        end_time = datetime.datetime.now().replace(microsecond=0)
        print("Populating complete...")
        print("Wrote " + str(count) + " entries in " + str(end_time - start_time))

    # Don't worry, in production, this isn't how passwords are generated.
    # TODO Change this so that it generates a random string of characters and outputs to a separate passwords file.
    def get_password(self, name, rollnumber):
        name = name.split(" ")[1]
        return name + "." + str(rollnumber)

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
