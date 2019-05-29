from sklearn.cluster import KMeans
from queue import Queue

class Cluster():
    def __init__(self, epsilon, min_lns):
        self.epsilon = epsilon
        self.min_lns = min_lns
        self.lines = []
        pass

    def epsilon_neighbourhood(self, segment):
        return list(filter((lambda x: x["segment"].distance(segment) <= self.epsilon), self.lines))

    def segment_cluster(self, segments):
        cluster_id = 0
        print("clustering")
        self.lines = list(map((lambda x: {'segment': x, 'cluster': "unclassified"}), segments))
        for obj_segment in self.lines:
            if obj_segment["cluster"] == "unclassified":
                neighbourhood = self.epsilon_neighbourhood(obj_segment["segment"])
                if len(neighbourhood) >= self.min_lns:
                    queue = Queue()
                    for line in neighbourhood:
                        if line is not obj_segment:
                            queue.put_nowait(obj_segment)
                    print("expand now")
                    self.expand_cluster(queue, cluster_id)
                    print(cluster_id)
                    cluster_id += 1
                else:
                    obj_segment["cluster"] = "noise"
        clusters = []
        for i in range (0, cluster_id + 1):
            clusters.append([])
        for line in self.lines:
            if type(line["cluster"]) is int:
                clusters[line["cluster"]].append(line["segment"])
        self.lines = []
        return clusters
        pass

    def expand_cluster(self, queue, cluster_id):
        """Compute a density-connected set"""
        while not queue.empty():
            print(queue.qsize())
            line  = queue.get_nowait()
            neighbourhood = self.epsilon_neighbourhood(line["segment"])
            if len(neighbourhood) >= self.min_lns:
                for line in neighbourhood:
                    if line["cluster"] is "unclassified":
                        line["cluster"] = cluster_id
                        queue.put_nowait(line)
                    if line["cluster"] is "noise":
                        line["cluster"] = cluster_id
        pass
