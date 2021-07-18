from random import randint


def get_random_joke():
    f = open("app/sources/anecdots.txt", "r", encoding="utf-8")
    jokes = f.read().split("\n\n")
    i = randint(0, len(jokes))
    return jokes[i]


get_random_joke()
