"""
From existing data, cluster the trajectories seen thus far into n clusters
Then, in real time, classify the current trajectory as one of the n clusters.
Uses K-means clustering.
"""

import csv
import numpy as np
from functools import reduce
from queue import Queue
from LineSegment import LineSegment
from Cluster import Cluster
from Optimizer import Optimizer
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import matplotlib.cm as cmx
import matplotlib.image as mpimg
"""
How to split trajectories meaningfully? TRACLUS!
"""

class Partition():

    def __init__(self, likelihood_threshold, min_velocity):
        self.likelihood_threshold = likelihood_threshold
        self.left_trajectories = []
        self.right_trajectories = []
        self.min_velocity = min_velocity

    def pre_process(self, file, start=0, length = 2000):
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
        with open(file) as csvfile:
            reader = csv.reader(csvfile)
            count = 0
            for row in reader:
                if count < start:
                    count += 1
                    continue
                if count > start+length:
                    break
                count += 1
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
        return count

    def clear_trajectories(self):
        """
        Clears the trajectories from memory. To be done after they have been clustered.
        """
        self.left_trajectories = []
        self.right_trajectories = []

    def trajectory_partition(self, trajectory):
        """
        Input: A trajectory T Ri = p1p2p3 · · · pj · · · pleni
        Output: A set CPi of characteristic points
        Algorithm:
        01: Add p1 into the set CPi; /* the starting point */
        02: startIndex := 1, length := 1;
        03: while (startIndex + length ≤ leni) do
        04: currIndex := startIndex + length;
        05: cost_par := MDL_par(pstartIndex, pcurrIndex);
        06: cost_nopar := MDL_nopar(pstartIndex, pcurrIndex);
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
        start_index = 0
        length = 1
        characteristic_points = []
        segments = []
        last_point = None
        for point in trajectory:
            if last_point is not None:
                segments.append(LineSegment(last_point, point))
            last_point = point
        segments = np.array(segments)
        characteristic_points.append(trajectory[0])
        while start_index + length < len(trajectory):
            curr_index = start_index + length
            """
            MDL_par denotes the MDL Cost of a trajectory between p_i and p_j,
            when assuming that p_i and p_j are the only characteristic points.
            MDL_nopar denotes the MDL cost when assuming there is no characteristic
            point between the two, i.e preserving the original trajectory.
            """
            cost_par = self.MDL_cost(segments[start_index:curr_index], [trajectory[start_index], trajectory[curr_index]])
            cost_nopar = self.MDL_cost(segments[start_index:curr_index])
            if cost_par > cost_nopar + 10:
                characteristic_points.append(trajectory[curr_index -1])
                start_index = curr_index - 1
                length = 1
            else:
                length += 1
        characteristic_points.append(trajectory[len(trajectory) -1])
        char_segments = []
        last_point = None
        for point in characteristic_points:
            if last_point is not None:
                char_segments.append(LineSegment(last_point, point))
            last_point = point
        char_segments = np.array(char_segments)
        return (characteristic_points, char_segments)

    def MDL_cost(self, segments, characteristic_points = []):
        if len(characteristic_points) is 0:
            #MDLnopar
            LH = 0.0
            for segment in segments:
                LH += segment.length
            return np.log2(LH)
        characteristic_segment = LineSegment(characteristic_points[0], characteristic_points[1])
        LH = np.log2(characteristic_segment.length)
        perp_d = 0.0
        ang_d = 0.0
        for segment in segments:
            perp_d += segment.perpendicular_distance(characteristic_segment)
            ang_d += segment.angle_distance(characteristic_segment)
        if perp_d != 0.0:
            perp_d = np.log2(perp_d)
        if ang_d != 0.0:
            ang_d = np.log2(ang_d)
        return LH + perp_d + ang_d




if __name__=="__main__":
    p = Partition(0.1, 40)
    p.pre_process("second.csv")
    fig = plt.figure()
    img = mpimg.imread("ref.png")
    c = Cluster(1.7, 15)
    plt.imshow(img)
    temp_trajl = []
    temp_trajr = []
    for trajectory in p.left_trajectories:
        lines = p.trajectory_partition(trajectory)[1]
        for line in lines:
            temp_trajl.append(line)
    for trajectory in p.right_trajectories:
        lines = p.trajectory_partition(trajectory)[1]
        for line in lines:
            temp_trajr.append(line)
    c.lines = list(map((lambda x: {'segment': x, 'cluster': "unclassified"}), temp_trajl))
    # opt = Optimizer({"epsilon": 2, "cluster": c})
    # out, e = opt.anneal()
    # print(out["epsilon"])
    cmap = plt.cm.jet
    clusters = c.segment_cluster(temp_trajl)
    for cluster in c.segment_cluster(temp_trajr):
         clusters.append(cluster)
    c_norm = colours.Normalize(vmin=0, vmax = len(clusters))
    scalar_map = cmx.ScalarMappable(norm= c_norm, cmap=cmap)
    print("clusters", len(clusters))
    for i in range(0, len(clusters)):
        cluster= clusters[i]
        if len(cluster) == 0:
            continue
        color_val = scalar_map.to_rgba(i)
        for line in cluster:
            plt.arrow(line.a[0], line.a[1], line.vector[0],line.vector[1],color=color_val)

    plt.show()
