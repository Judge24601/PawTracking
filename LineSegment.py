import numpy as np
import math

class LineSegment():
     def __init__(self, a, b):
         self.a = a
         self.b = b
         self.vector = b - a
         self.length = np.linalg.norm(self.vector)
         if self.length == 0.0:
             self.unit = self.vector
         else:
             self.unit = self.vector/self.length

     def longer_than(self, other):
         return self.vector.dot(self.vector) > other.vector.dot(other.vector)

     def perpendicular_distance(self, other):
         if self.longer_than(other):
             d1 = np.linalg.norm(np.cross(self.vector, self.a - other.a))/self.length
             d2 = np.linalg.norm(np.cross(self.vector, self.a - other.b))/self.length
         else:
             d1 = np.linalg.norm(np.cross(other.vector, other.a - self.a))/other.length
             d2 = np.linalg.norm(np.cross(other.vector, other.a - self.b))/other.length
         if d1 + d2 >0.0:
             return (d1*d1 + d2*d2)/(d1 + d2)
         return 0.0

     def angle_distance(self, other):
         angle = np.arccos(np.clip(np.dot(self.unit, other.unit), -1.0, 1.0))
         if self.longer_than(other):
             if angle > math.pi/2:
                 return self.length
             return other.length * np.sin(angle)
         else:
             if angle > math.pi/2:
                 return other.length
             return self.length * np.sin(angle)
             pass

     def distance(self, other):
         return min(self.length, other.length) + self.perpendicular_distance(other) + self.angle_distance(other)

if __name__ =="__main__":
    #Example
    l1 = LineSegment(np.array([2, 2]), np.array([3, 3]))
    l2 = LineSegment(np.array([1, 0]), np.array([7, 0]))
    print(l1.perpendicular_distance(l2))
    print(l2.perpendicular_distance(l1))
    print(13/5, '\n')
    print(l2.angle_distance(l1))
