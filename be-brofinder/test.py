from requests import post
from random import randint, choice

objects = [
    "iphone 9", 
    "samsung s23", 
    "pincopallo", 
    "macbook",
    "ps5",
    "gianni",
    "rtx 3060 ti",
    "rtx 3090 ti"
]

user = [randint(37823783, 99999999) for i in range(0, 5000)]

for element in objects:
    post("http://localhost:8080/api/search", data={
        "text" : element,
        "user" : choice(user),
        "forward" : False,
    })