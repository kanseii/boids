import numpy as np
# print(np.linalg.norm(np.array([14,-24])))
from math import atan2
from math import pi
import math
def angle():
    return atan2(-3,3)*180/(pi)
# help(np.linalg.norm)
print(angle())

def IsPointInCircularSector(
    self, float ux, float uy, float r, float theta,
    float px, float py)
{
 
 
    float dx = px - cx;
    float dy = py - cy;
 
    // |D| = (dx^2 + dy^2)^0.5
    float length = sqrt(dx * dx + dy * dy);
 
    // |D| > r
    if (length > r)
        return false;
 
    // Normalize D
    dx /= length;
    dy /= length;
 
    // acos(D dot U) < theta
    return acos(dx * ux + dy * uy) < theta;
}
