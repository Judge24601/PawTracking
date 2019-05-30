from Cluster import Cluster
from Partition import Partition
from LineSegment import LineSegment
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import matplotlib.cm as cmx
import matplotlib.image as mpimg
import time
from threading import Thread

LIKELIHOOD_THRES = 0.1
MIN_VELOCITY = 40
FILE_NAME = "second.csv"
EPSILON = 1.7
MIN_LINES = 15
class ClusterUpdater(Thread):

    def __init__(self, partitioner, clusterer, clusters):
        Thread.__init__(self, daemon=True)
        self.partitioner = partitioner
        self.clusterer = clusterer
        self.clusters = clusters
        pass
    def run(self):
        self.partitioner.pre_process(FILE_NAME, 0, 99999)
        temp_trajl = []
        temp_trajr = []
        for trajectory in partitioner.left_trajectories:
            lines = partitioner.trajectory_partition(trajectory)[1]
            for line in lines:
                temp_trajl.append(line)
        for trajectory in partitioner.right_trajectories:
            lines = partitioner.trajectory_partition(trajectory)[1]
            for line in lines:
                temp_trajr.append(line)
        self.clusters = clusterer.segment_cluster(temp_trajl)
        for cluster in clusterer.segment_cluster(temp_trajr):
             self.clusters.append(cluster)
        pass

def partition(partitioner):
    temp_trajl = []
    temp_trajr = []
    for trajectory in partitioner.left_trajectories:
        lines = partitioner.trajectory_partition(trajectory)[1]
        for line in lines:
            temp_trajl.append(line)
    for trajectory in partitioner.right_trajectories:
        lines = partitioner.trajectory_partition(trajectory)[1]
        for line in lines:
            temp_trajr.append(line)

    return (temp_trajl, temp_trajr)
"""
clusters = clusterer.segment_cluster(temp_trajl)
for cluster in clusterer.segment_cluster(temp_trajr):
     clusters.append(cluster)
 """
def plot_clusters(clusters):
    c_norm = colours.Normalize(vmin=0, vmax = len(clusters))
    scalar_map = cmx.ScalarMappable(norm= c_norm, cmap=cmap)
    for i in range(0, len(clusters)):
        cluster= clusters[i]
        if len(cluster) == 0:
            continue
        color_val = scalar_map.to_rgba(i)
        for line in cluster:
            plt.arrow(line.a[0], line.a[1], line.vector[0],line.vector[1],color=color_val)
"""
Setup! Processes the first n lines of the csv to begin the clustering.
"""
partitioner = Partition(LIKELIHOOD_THRES, MIN_VELOCITY)
clusterer = Cluster(EPSILON, MIN_LINES)
partitioner.pre_process(FILE_NAME, 0, 7000)
partitions = partition(partitioner)
clusters = clusterer.segment_cluster(partitions[0])
for cluster in clusterer.segment_cluster(partitions[1]):
     clusters.append(cluster)
print("done clustering")
fig = plt.figure()
cmap = plt.cm.jet
# plt.ion()
img = mpimg.imread("ref.png")
plt.imshow(img)
plot_clusters(clusters)
# plt.draw()
"""
Real time!
"""
cycle_time = 0.0
last_time = time.time()
n = 4000
# update_clusterer = Cluster(EPSILON, MIN_LINES)
# updater = ClusterUpdater(partitioner, update_clusterer, clusters.copy())
# updater.start()
clusterer.average_segments(clusters)
partitioner.clear_trajectories()
while (partitioner.pre_process(FILE_NAME, n, 100) > n):
    temp_cycle_time = time.time() - last_time
    if temp_cycle_time > cycle_time:
        cycle_time = temp_cycle_time
    last_time = time.time()
    partitions = partition(partitioner)
    for paw in partitions:
        for line in paw:
            m = clusterer.classify_segment(clusters, line)
            if m > -1:
                print ("Motion clustered to ", m)
    # if not updater.is_alive():
    #     print("updater complete")
    #     clusters = updater.clusters
    #     updater.join()
    #     updater = ClusterUpdater(partitioner, update_clusterer, clusters.copy())
    #     updater.start()
    partitioner.clear_trajectories()
    print(n)
    n+= 1
print("Highest Cycle Time:", cycle_time)
plot_clusters(clusters)
plt.show()
