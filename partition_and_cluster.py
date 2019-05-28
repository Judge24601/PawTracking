"""
From existing data, cluster the trajectories seen thus far into n clusters
Then, in real time, classify the current trajectory as one of the n clusters.
Uses K-means clustering.
"""

from sklearn.cluster import KMeans
import csv
import numpy as np
from queue import Queue
"""
How to split trajectories meaningfully? TRACLUS!
"""

likelihood_threshold = 0.1
left_trajectories = []
right_trajectories = []
min_velocity = 30 #To be determined
left_queue = Queue(15)
right_queue = Queue(15)
templ_trajectory = []
tempr_trajectory = []
left_moving = False
right_moving = False
with open("eight_points.csv") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        try:
            row = list(map(float, row))
        except Exception as e:
            continue
        #Processing data now
        i = 1
        average_x = 0.0
        average_y = 0.0
        n = 0
        #Left Paw
        while i < 12:
            x_coord = row[i]
            y_coord = row[i+1]
            likelihood = row[i+2]
            if likelihood > likelihood_threshold:
                average_x += x_coord
                average_y += y_coord
                n+=1
            i+=3
        if n is not 0:
            average_x /= n
            average_y /= n
            curr_point = [average_x, average_y]
            if left_queue.full():
                last_point = left_queue.get_nowait()
                delta = np.array([curr_point[0] - last_point[0], curr_point[1] - last_point[1]])
                if np.sqrt(delta.dot(delta)) > min_velocity:
                    if not left_moving:
                        left_moving = True
                        temp_queue = Queue()
                        while not left_queue.empty():
                            next_point = left_queue.get_nowait()
                            templ_trajectory.append(next_point)
                            temp_queue.put_nowait(next_point)
                        while not temp_queue.empty():
                            left_queue.put_nowait(temp_queue.get_nowait())
                    templ_trajectory.append(curr_point)
                else:
                    if left_moving:
                        left_trajectories.append(templ_trajectory)
                        templ_trajectory = []
                        left_moving = False
            left_queue.put_nowait(curr_point)

        average_x = 0.0
        average_y = 0.0
        n = 0
        #Right Paw
        while i < 24:
            x_coord = row[i]
            y_coord = row[i+1]
            likelihood = row[i+2]
            if likelihood > likelihood_threshold:
                average_x += x_coord
                average_y += y_coord
                n+=1
            i+=3
        if n is not 0:
            average_x /= n
            average_y /= n
            curr_point = [average_x, average_y]
            if right_queue.full():
                last_point = right_queue.get_nowait()
                delta = np.array([curr_point[0] - last_point[0], curr_point[1] - last_point[1]])
                if np.sqrt(delta.dot(delta)) > min_velocity:
                    if not right_moving:
                        temp_queue = Queue()
                        while not right_queue.empty():
                            next_point = right_queue.get_nowait()
                            tempr_trajectory.append(next_point)
                            temp_queue.put_nowait(next_point)
                        while not temp_queue.empty():
                            right_queue.put_nowait(temp_queue.get_nowait())
                        right_moving = True
                        tempr_trajectory.append(curr_point)
                else:
                    if right_moving:
                        right_trajectories.append(tempr_trajectory)
                        tempr_trajectory = []
                        right_moving = False
            right_queue.put_nowait((average_x, average_y))
left_trajectories = np.array(left_trajectories)
right_trajectories = np.array(right_trajectories)
print(len(left_trajectories))
print(len(right_trajectories))
