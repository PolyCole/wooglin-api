"""

    Author: Cole Polyak
    Date: 19 January 2021
    Purpose: This script provides encryption and decryption methods for CSV files.

"""

from cryptography.fernet import Fernet


def encrypt_file():
    filename = input("Please enter the name of the file to encrypt: ")
    try:
        input_file = open(filename, "r")
    except FileNotFoundError as e:
        print(e)
        exit(1)

    output_file = open("encrypted_" + filename, "w")

    encryption_key = Fernet.generate_key()
    print("We'll generate a cryptographically secure encryption key for you...")
    print("Encryption key:\n" + str(encryption_key.decode()))

    current_line = input_file.readline()
    while current_line != '':
        processed = current_line.strip().split(",")

        for x in range(0, len(processed)):
            csv = encrypt(processed[x], encryption_key)
            output_file.write(str(csv))
            if x < (len(processed) - 1):
                output_file.write(",")
            else:
                output_file.write("\n")
        current_line = input_file.readline()

    input_file.close()
    output_file.close()
    print("Successfully encrypted comma separated values.")


def decrypt_file():
    filename = input("Please enter the name of the file to decrypt: ")

    input_file = None

    try:
        input_file = open(filename, "r")
    except FileNotFoundError as e:
        print(e)
        exit(1)

    output_file = open("decrypted_" + filename.replace("encrypted_", ""), "w")

    encryption_key = input("Please enter the encryption key used:")
    encryption_key = encryption_key.strip().encode()

    current_line = input_file.readline()
    while current_line != '':
        processed = current_line.strip().split(",")

        for x in range(0, len(processed)):
            csv = decrypt(processed[x], encryption_key)
            output_file.write(str(csv))
            if x < (len(processed) - 1):
                output_file.write(",")
            else:
                output_file.write("\n")
        current_line = input_file.readline()

    input_file.close()
    output_file.close()
    print("Successfully decrypted comma separated values.")


def encrypt(csv, key):
    f = Fernet(key)
    encrypted = f.encrypt(csv.encode())
    return encrypted.decode()


def decrypt(csv, key):
    f = Fernet(key)
    decrypted = f.decrypt(csv.encode())
    return decrypted.decode()
