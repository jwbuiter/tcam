import time

import tcam


t_array = []


def run(config):
    while True:
        t1 = time.monotonic()  # for determining frame rate
        try:
            tcam.update()
        except:
            continue

        time.sleep(0.5)
        # approximating frame rate
        t_array.append(time.monotonic()-t1)
        if len(t_array) > 10:
            t_array = t_array[1:]  # recent times for frame rate approx
        print('Frame Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))
