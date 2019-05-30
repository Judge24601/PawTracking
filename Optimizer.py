from simanneal import Annealer
from random import random
import numpy as np
from Cluster import Cluster
class Optimizer(Annealer):
    def move(self):
        adjustment = (random() - 0.5)
        self.state["epsilon"] += adjustment

    def energy(self):
        e = 0
        print("energy!")
        cluster = self.state["cluster"]
        cluster.epsilon = self.state["epsilon"]
        for line in cluster.lines:
            sum = 0.0
            print(sum)
            for line_n in cluster.lines:
                sum += len(cluster.epsilon_neighbourhood(line_n["segment"]))
            p = len(cluster.epsilon_neighbourhood(line["segment"]))/sum
            if p > 0:
                e += p*np.log2(1/p)
        print("epsilon", cluster.epsilon)
        print("energy", e)
        return e
