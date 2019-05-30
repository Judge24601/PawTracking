from queue import Queue
from LineSegment import LineSegment
from sortedcontainers import SortedKeyList
import matplotlib.pyplot as plt
import numpy as np

class Cluster():
    def __init__(self, epsilon, min_lns, gamma = 0.0):
        self.epsilon = epsilon
        self.min_lns = min_lns
        self.gamma = gamma
        self.lines = set()
        self.cluster_info = []
        pass

    def epsilon_neighbourhood(self, segment):
        return set(filter((lambda x: x.distance(segment) <= self.epsilon), self.lines))

    def segment_cluster(self, segments):
        cluster_id = 0
        # print("clustering")
        self.lines = segments
        for obj_segment in self.lines:
            if obj_segment.cluster == "unclassified":
                neighbourhood = self.epsilon_neighbourhood(obj_segment)
                if len(neighbourhood) >= self.min_lns:
                    queue = Queue()
                    for line in neighbourhood:
                        if line is not obj_segment:
                            queue.put_nowait(obj_segment)
                    # print("expand now")
                    self.expand_cluster(queue, cluster_id)
                    print(cluster_id)
                    cluster_id += 1
                else:
                    obj_segment.cluster = "noise"
        clusters = []
        for i in range (0, cluster_id):
            clusters.append([])
        # print("done")
        for line in self.lines:
            if type(line.cluster) is int:
                clusters[line.cluster].append(line)
        return clusters
        pass

    def expand_cluster(self, queue, cluster_id):
        """Compute a density-connected set"""
        while not queue.empty():
            line  = queue.get_nowait()
            neighbourhood = self.epsilon_neighbourhood(line)
            if len(neighbourhood) >= self.min_lns:
                for line in neighbourhood:
                    if line.cluster is "unclassified":
                        line.cluster = cluster_id
                        queue.put_nowait(line)
                    if line.cluster is "noise":
                        line.cluster = cluster_id
        pass

    def average_segments(self, clusters):
        for cluster in clusters:
            av_vector = np.array([0.0, 0.0])
            av_start = np.array([0.0, 0.0])
            for line in cluster:
                av_vector += line.vector
                av_start += line.a
            av_vector /= len(cluster)
            av_start /= len(cluster)
        self.cluster_info.append({"average": LineSegment(av_start, av_start + av_vector), "num": len(cluster)})

    def classify_segment(self, clusters, segment):
        for i in range(0, len(clusters)):
            if self.cluster_info[i]["average"].distance(segment) <= self.epsilon:
                clusters[i].append(segment)
                av_vector = self.cluster_info[i]["average"].vector + segment.vector/self.cluster_info[i]["num"]
                av_start = self.cluster_info[i]["average"].a + segment.a/self.cluster_info[i]["num"]
                self.cluster_info[i] = {"average": LineSegment(av_start, av_start + av_vector), "num": len(clusters[i])}
                return i
            i+=1
            return -1

    def representative_trajectory(self, cluster):
        # TODO: Fix this :/
        rep_trajectory = []
        #Average direction vector:
        av_vector = np.array([0.0, 0.0])
        for line in cluster:
            av_vector += line.vector
        av_vector /= len(cluster)
        print(av_vector)
        unit_av = av_vector/np.linalg.norm(av_vector)
        print(unit_av)
        x = np.array([1.0, 0.0])
        theta = np.arccos(x.dot(unit_av))
        if unit_av[1] > 0.0:
            theta = -theta
        rotation_mat = np.array([[np.cos(theta), -np.sin(theta)],
                                 [np.sin(theta), np.cos(theta)]])
        back_rotation_mat = np.array([[np.cos(-theta), np.sin(-theta)],
                              [-np.sin(-theta), np.cos(-theta)]])
        rotated_points = []
        rotated_lines = []
        for line in cluster:
            rot_v = rotation_mat.dot(line.vector)
            rot_b = line.a + line.length*rot_v
            rotated_points.append({"end": False, "point":line.a})
            rotated_points.append({"end": True, "point": rot_b})
            rotated_lines.append(LineSegment(line.a, rot_b))

        rotated_points = sorted(rotated_points, key=lambda x: x["point"][0])
        #Sort lines by starting x value
        line_start_lookup = SortedKeyList(rotated_lines, key=lambda x: x.a[0])
        #Sort lines the sweep line crosses by ending x value
        intersecting_lines = SortedKeyList([], key=lambda x:x.b[0])
        last_x = 0.0
        for point_dict in rotated_points:
            if point_dict["end"]:
                try:
                    intersecting_lines.pop(0)
                except Exception as e:
                    print("Could not generate a representative trajectory. Examine your clustering parameters")
                    break;
            else:
                intersecting_lines.add(line_start_lookup.pop(0))
            if len(intersecting_lines) >= self.min_lns:
                # diff = point_dict["point"][0] - last_x
                # if diff >= self.gamma:
                average_y = 0.0
                for line in intersecting_lines:
                    slope = line.vector[1]/line.vector[0]
                    average_y += (point_dict["point"][0]-line.a[0])*slope
                average_y /= len(intersecting_lines)
                rep_trajectory.append(np.array([point_dict["point"][0], average_y]))
        return rep_trajectory
