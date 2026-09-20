from random import randint
import time

with open("arduinodata.csv", 'w') as f:
    pass

while True:
    with open("arduinodata.csv", 'a') as f:
        time.sleep(0.1)
        data = f"""{randint(-3,3)/100}, {randint(-3,3)/100}, {randint(99,102)/100},{-randint(70,95)/100},{randint(507,607)/100},{randint(13374,13376)/100}"""
        if randint(0,10) < 2:
            data.split(',')
        f.write(data + '\n')
        print(data)
