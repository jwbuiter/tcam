import numpy as np

import tcam


def run():
    while True:
        filename = input("Enter filename, or x to quit: ")
        if filename == '':
            continue
        if filename == 'x':
            break

        frame = np.round(tcam.get_frame())
        print(frame)
        np.savetxt('/home/pi/Documents/' + filename +
                   '.csv', frame, delimiter=';')
