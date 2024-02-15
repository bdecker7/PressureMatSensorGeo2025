import serial

import time


def stringToIntList(string: str) -> list[int]:
    return [int(num) for num in string if num not in ['[',']',',']]


# open serial port
serialcomm = serial.Serial('COM7')
serialcomm.timeout = 1

while True:
    # get input command
    command = input("Enter Input: ").strip()

    if command == "done":

        print('Finished')

        break

    if command == "on" or command == "off":

        serialcomm.write(command.encode())

        # time.sleep(0.5)

        # val = serialcomm.readline().decode('ascii')

        # print(val)

    if command == "write":
        
        serialcomm.write(command.encode())
    
    if command == "read":

        while(1):
            time.sleep(.05)
            print("Reading")
            string = serialcomm.read_all()
            serialcomm.write(0b1)
            # print(type(string))
            # print(string)
            var_decoded = string.decode('ascii')
            # print(type(var_decoded))
            print(var_decoded)
        # listV = stringToIntList(var_decoded)
        # print(type(listV))
        # print(listV)

        # print(serialcomm.read_all().decode('ascii'))
    

    # print(serialcomm.readline().decode('ascii'))

serialcomm.close()