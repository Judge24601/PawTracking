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

class Partition():

    def __init__(self, likelihood_threshold, min_velocity):
        self.likelihood_threshold = likelihood_threshold
        self.left_trajectories = []
        self.right_trajectories = []
        self.min_velocity = min_velocity

    def pre_process(self):
        """
        Separate the historical data of the mouse into specific trajectories.
        We define a specific trajectory as any set of fifteen or more frames where
        the mouse's paw movement exceeds the minimum velocity. Any portions where
        the mouse is not moving are discarded, along with any points with low
        likelihood of correctness from DeepLabCut.
        """
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
                    if likelihood > self.likelihood_threshold:
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
                        if np.sqrt(delta.dot(delta)) > self.min_velocity:
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
                                self.left_trajectories.append(np.array(templ_trajectory))
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
                    if likelihood > self.likelihood_threshold:
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
                        if np.sqrt(delta.dot(delta)) > self.min_velocity:
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
                                self.right_trajectories.append(np.array(tempr_trajectory))
                                tempr_trajectory = []
                                right_moving = False
                    right_queue.put_nowait((average_x, average_y))


    def trajectory_partition(trajectory):
        """
        Input: A trajectory T Ri = p1p2p3 · · · pj · · · pleni
        Output: A set CPi of characteristic points
        Algorithm:
        01: Add p1 into the set CPi; /* the starting point */
        02: startIndex := 1, length := 1;
        03: while (startIndex + length ≤ leni) do
        04: currIndex := startIndex + length;
        05: costpar := MDLpar(pstartIndex, pcurrIndex);
        06: costnopar := MDLnopar(pstartIndex, pcurrIndex);
        /* check if partitioning at the current point makes
        the MDL cost larger than not partitioning */
        07: if (costpar > costnopar) then
        /* partition at the previous point */
        08: Add pcurrIndex−1 into the set CPi;
        09: startIndex := currIndex − 1, length := 1;
        10: else
        11: length := length + 1;
        12: Add pleni
        into the set CPi; /* the ending point */
        (Lee, Han, & Whang, 2007)
        """
        startIndex = 1
        length = 1
        characteristic_points = []
        characteristic_points.append(trajectory[0])
        while startIndex + length < len(trajectory):
            currIndex = startIndex + length

        pass

if __name__=="__main__":
    p = Partition(0.1, 30)
    p.pre_process()
    print(p.left_trajectories)
