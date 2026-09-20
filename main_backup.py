from random import randint
from collections import deque
import time

import numpy as np

MAX = 1023
class hand(object):
    def __init__(self, fingers:list=[0,0,0,0,0],    #3 fingers
                 acceleration:list=[0,0,0],         #3 accel
                 angles:list=[0,0,0]):              #3 angles

        # Fingers
        self.thumb, self.index, self.middle, self.ring, self.pinky = [0.0 for x in range(5)]    
        self.fingers = fingers

        # Angles
        self.angles = angles

        # Acceleration
        self.accel = acceleration

    def __repr__(self):
        return(f"f: {str(self.fingers):<22}, ac: {str(self.accel):<22}, an: {str(self.angles):<22}")

    # checking acceleration
    @property
    def accel(self):
        return self._accel

    @accel.setter
    def accel(self, values:list):

        if len(values) != 3:
            raise ValueError(f"input list is not of length 3")

        for val in values:
            if not(isinstance(val, float) or isinstance(val, int)):
                raise TypeError(f"value \"{val}\" is not type float")

        self._accel = np.array([float(x) for x in values])


    # checking finger values
    @property
    def fingers(self):
        return self._fingers

    @fingers.setter
    def fingers(self, values:list):
        
        if len(values) != 5:
            raise ValueError(f"input list is not of length 5")

        for val in values:
            if not(0 <= val <= MAX):
                print(values)
                raise ValueError(f"values must be between 0 and 4 (inclusive)")

        self._fingers = np.array([float(x) for x in values])
        self.thumb, self.index, self.middle, self.ring, self.pinky = self._fingers


    # checking angles values
    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, values:list):

        for i, val in enumerate(values):
            if not(-360<= val <= 360):
                values[i] = val%360

        self._angles = np.array([float(x) for x in values])



def follow(path):
    with open(path, "r") as f:
        # Optional: start at end; remove this seek if you want from beginning
        # f.seek(0, 2)

        while True:

            line = f.readline()
            if not line:
                # No new data yet, wait a bit
                time.sleep(0.1)
                continue

            if len(line.strip().split(',')) < 9:
                print("Error:", line.strip().split(','))
                continue

            yield "".join(line.split())

def two_wide_array(in_string) -> list:
    #makes a two wide array for the low pass filter

    in_data = float(in_string)
    i = 0
    two_wide_array = []

    if i == 0:
        two_wide_array.insert(0, in_data)
        two_wide_array.insert(0, in_data)
    else:
        two_wide_array.pop()
        two_wide_array.insert(0, in_data)

    i += 1

    return two_wide_array

class tri_axis_data(object):
    def __init__(self, x:float=0, y:float=0, z:float=0):

        self.x = x
        self.y = y
        self.z = z

        self.values = [self.x, self.y, self.z]

class pos(object):
    def __init__(self, x:float=0, y:float=0, z:float=0):
        self.position = tri_axis_data(x, y, z)
        self.angle = tri_axis_data(0,0,0)

    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value:tri_axis_data):
        #print(value.x, value.y, value.z )
        self._angle = tri_axis_data(value.x%360, value.y%360, value.z%360)  
    
    def __repr__(self):
        return f'pos: ({self.position.x:<10.2f}, {self.position.y:<10.2f}, {self.position.z:<10.2f}), angle: ({self.angle.x:<10.2f}, {self.angle.y:<10.2f}, {self.angle.z:<10.2f})'

def low_pass_filter_nine_channel(data, alpha=0.1) -> list[float]:
    #y_t = a * x_t + (1 - a) * y_t-a
    #uses the old data to return the new one
    #array size is 2

    filtered = np.zeros_like(data)
    filtered[0] = data[0]
    for t in range(0, len(data)-1):
        filtered[t] = alpha * data[t] + (1 - alpha) * filtered[t - 1]
    
    return filtered
    
def main():
    # Stores hands in a special list
    np.set_printoptions(suppress=True)
    calibration = True
    hands = deque([])
    moving_avg = deque([])
    waveness = 1

    test_object = pos(0,0,0) # object positions

    for line in follow("arduinodata.csv"):

        # formats data
        try:
            
            h_temp = [float(x) for x in line.split(',')]
            h_temp[-1:] = [h_temp[-1],0,0]

            if MAX == 4:
                h_temp[6:] = [ 5*x//1024 for x in h_temp[6:]]

            # uses first 50 data points to calibrate data
            if calibration:
            
                if len(hands) < 100:
                    hands.append(hand(acceleration=h_temp[:3], angles=h_temp[3:6], fingers=h_temp[6:]))
                    #print('hand succesful')
                else:

                    data = np.array([0,0,0,0,0,0,0,0,0,0,0])
                    for x in hands:
                        data = data + np.concatenate((x.accel, x.angles, x.fingers))

                    cal_data = np.round(data/len(hands), 2) + [0,0,-1,0,0,0,-MAX,-MAX,-MAX,0,0]
                    cal_data[6:] = [ 0 for x in cal_data[6:]]
                    calibration = False
                    hands = deque([]) # reset hands after calibration
                    #print(f"calibrated: {cal_data}")
                    
            else:
                h_temp = h_temp-cal_data
                
                if len(moving_avg) < 10:
                    moving_avg.append(h_temp)
                else:
                    moving_avg.popleft()
                    moving_avg.append(h_temp)

                h_temp = np.round(np.array(moving_avg).mean(axis=0), 2)
                h_temp[6:] = [ round(x) for x in h_temp[6:]]
                #print(f"moving avg: {moving_avg}")

                if len(hands) < 50:
                    hands.append(hand(acceleration=h_temp[:3], angles=h_temp[3:6], fingers=h_temp[6:]))
                else:
                    hands.popleft()
                    hands.append(hand(acceleration=h_temp[:3], angles=h_temp[3:6], fingers=h_temp[6:]))

                test_object.position.x += h_temp[0]
                test_object.position.y += h_temp[1]
                test_object.position.z += (h_temp[2]-1)

                test_object.angle = tri_axis_data(h_temp[3]+test_object.angle.x, h_temp[4]+test_object.angle.y, h_temp[5]+test_object.angle.z)
                
                waveness -= 1
                out = "..."
                if hands[-1].index < 600 and hands[-1].thumb > 1023/2 and hands[-1].middle > 1023/2:
                    out = "No!"

                if hands[-1].thumb > 1023/2 and hands[-1].middle < 1023/2:
                    out = "Gig Em!"

                if 300 < hands[-1].thumb < 700 and hands[-1].middle > 1023/2:
                    out = "Peace!"

                if hands[-1].accel[-1] - round(np.array(moving_avg)[:-2,0:3].mean(axis=0)[-1],2) > 0.03 and hands[-1].thumb > 1023/2 and hands[-1].middle > 1023/2:
                    out = "Wave!"
                    waveness = 10

                if waveness > 1:
                    out = "Wave!"


                yield(out)


        except Exception as e:
            print(e)
            pass
     

if __name__ == "__main__":
    for i in main():
        print(i)
