import random


def generate_password(length=8):
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    password = ''

    for i in range(length):
        next_index = random.randrange(len(alphabet))
        password = password + alphabet[next_index]

    return password
