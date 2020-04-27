
import numpy as np
import random
import pygame
from math import atan2
from math import pi
from pygame.locals import *
import math

mp4 = False

vel = 2

BOID_NUM = 50

field = 50

BOID_SIZE = 8


VISION_ANGLE = 135.0

WINDOW_WIDTH = 600

WINDOW_HEIGHT = 400

MAX_SPEED = 8

CHANGE_SPEED = 4

alpha = 0.01

beta = 0.25

gamma = 0.125

dt = 0.1

# 初始化方向
def get_rand_vec(dims):
    x = np.random.standard_normal(dims)
    r = np.sqrt((x*x).sum())
    return x / r


def distance(bird1, bird2):
    dx = (bird1.pos-bird2.pos)[0]
    dy = (bird1.pos-bird2.pos)[1]
    return np.linalg.norm(np.array([dx,dy]))


def distance_barr(bird,pos):
    dx = bird.pos[0] - pos[0]
    dy = bird.pos[1] - pos[1]
    return np.linalg.norm(np.array([dx,dy]))

def get_triangle_points(pos,direction):

    normal = np.array([direction[1],-direction[0]])

    x1 = pos + direction * BOID_SIZE
    x2 = pos - normal * BOID_SIZE/4
    x3 = pos + normal * BOID_SIZE/4

    return [x1,x2,x3]

class Barrier:
    def __init__(self,pos,rc,rr):
        self.x,self.y = pos
        self.color = rc
        self.radius = rr

class Boid:
    def __init__(self):
        x = float(random.randrange(BOID_SIZE, WINDOW_WIDTH - BOID_SIZE))
        y = float(random.randrange(BOID_SIZE, WINDOW_HEIGHT - BOID_SIZE))
        self.pos = np.array([x,y])
        direction = get_rand_vec(2)
        self.velocity = vel*direction

    def angle(self):
        return atan2(self.velocity[0],self.velocity[1])*180/(pi)

    def direction(self):
        vec = np.array([self.velocity[0],self.velocity[1]])
        vel = np.linalg.norm(vec)
        return vec/vel

    def points(self):
        list_of_points = get_triangle_points(self.pos,self.direction())
        return list_of_points
    
    
    def vision(self,bird):
        x = bird.pos[0] - self.pos[0]
        y = bird.pos[1] - self.pos[1]
        length = np.linalg.norm(np.array([x,y]))
        x /= length
        y /= length
        return np.arccos(x * self.direction()[0] + y * self.direction()[1]) <= VISION_ANGLE/2
 


    def neighbours(self, list_of_boids):

        neighbours = []
        for brd in list_of_boids:
            if distance(self,brd)<field and brd!=self and self.vision(brd):
                neighbours.append(brd)
               
        return neighbours

    def same_vel(self, list_of_boids):
        count = 0
        for brd in list_of_boids:
            if np.abs((self.velocity[0]-brd.velocity[0])/self.velocity[0])<=1 and  np.abs((self.velocity[1]-brd.velocity[1])/self.velocity[1])<=1 :
                count+=1
        return count
    
    # same neighbours of a boid  (distance(self,brd)<4*field and brd!=self) and 
    def same_nei(self,list_of_boids):
        count = 0
        for brd in list_of_boids:
            # if (distance(self,brd)<6*field and brd!=self) and (np.abs((self.velocity[0]-brd.velocity[0])/self.velocity[0])<=1.5 and  np.abs((self.velocity[1]-brd.velocity[1])/self.velocity[1])<=1.5):
            if distance(self,brd)<5*field and brd!=self:
                count+=1
        return count 

    def update(self, list_of_boids):

        neighbours = self.neighbours(list_of_boids)

        N = len(neighbours)

        # Rule 1 : Cohesion
        if N==0:
            com = self.pos
        else:
            com = sum([x.pos for x in neighbours])/N
        vc = (com - self.pos)
       

        # Rule 2 : Separation
        vs_sum = np.array([0.0,0.0])
        vs_n = 0
        vs = np.array([0.0,0.0])
        for bird in neighbours:
            if distance(self,bird)<15 :
                # vs += (self.pos - bird.pos)
                vs_sum += bird.pos
                vs_n += 1
        if vs_n != 0:
            vs = self.pos - (vs_sum/vs_n) 

        # Rule 3 : Alignment
        if N==0:
            va_sum = self.velocity
        else:
            va_sum = sum([x.velocity for x in neighbours])/N
        va = (va_sum - self.velocity)

    

        # Changes
        self.velocity += alpha * vc
        self.velocity += beta * vs
        self.velocity += gamma * va


        # Beyond max speed
        if np.linalg.norm(self.velocity) > MAX_SPEED:
            # self.velocity = (1-dt) * self.velocity
            self.velocity = self.velocity/np.linalg.norm(self.velocity) * MAX_SPEED

        # Rule 5 : Stay within boundaries
        if self.pos[0] > WINDOW_WIDTH - 20 :
            self.velocity[0] -= CHANGE_SPEED
        if self.pos[1] > WINDOW_HEIGHT- 20:
            self.velocity[1] -= CHANGE_SPEED
        if self.pos[0] < 20:
            self.velocity[0] += CHANGE_SPEED
        if self.pos[1] < 20:
            self.velocity[1] += CHANGE_SPEED

        # change position
        self.pos += (1+dt)*self.velocity
       
        # Rule 6 : Stay within barrier
        pos_x,pos_y = pygame.mouse.get_pos()
        tem_v = self.direction()
        if distance_barr(self,(pos_x,pos_y))<=42:
            self.velocity[0] -= 1.8* self.velocity[0] 
            self.velocity[1] -= 1.8* self.velocity[1] 
            self.pos += tem_v*(30-distance_barr(self,(pos_x,pos_y)))
            


       
        



def make_boids(N):
    list_of_boids = []
    for i in range(N):
        boid = Boid()
        list_of_boids.append(boid)
    return list_of_boids

boid_list = make_boids(BOID_NUM)


def main():
    pygame.init()
    
    size = [WINDOW_WIDTH, WINDOW_HEIGHT]
    screen = pygame.display.set_mode(size,0,32)
    pygame.display.set_caption("Boids")
    done = False
    clock = pygame.time.Clock()
    same_v = []
    swarm_n = []
    index = 0
    while not done:
        index+=1
        if mp4 == True:
            filename = 'animation/'+'capture_'+str(index)+'.jpeg'
            pygame.image.save(screen, filename)

        if index >= 500:
            done = True
        # --- Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        
        screen.fill((0,0,0))

        vels = []
        neigs = []
        # Draw barrier
        barrier = Barrier(pygame.mouse.get_pos(),(255,255,255),33)
        pygame.draw.circle(screen,barrier.color,(barrier.x,barrier.y),barrier.radius)
        clock.tick()
        # --- Logic
        for boid in boid_list:
            boid.update(boid_list)
            vels.append(boid.same_vel(boid_list))
            neigs.append(boid.same_nei(boid_list))
            # print("pos = ",boid.pos)


        same_v.append(str(max(vels)))

        def validate(x,y):
            if x<0 or y<0:
                return False
            return True

        for i in range(len(neigs)-1):
            for j in range(i+1,len(neigs)):
                if np.abs(neigs[i]-neigs[j])<=4 and validate(neigs[i],neigs[j]) :
                    neigs[j] = -1
        count = 0
        for i in range(len(neigs)):
            if neigs[i]>0:
                count+=1
        swarm_n.append(str(count))
        # print("num = ",count)

        # print(len(dict_neigs.values()))
        # for i in dict_neigs :
        #     if dict_neigs[i] > 2:
        #         count+=1
        # print(count)

        # --- Drawing
        for boid in boid_list :
            list_of_points = boid.points()
            pygame.draw.polygon(screen, (0,206,209),list_of_points)

        
        # Limit to 60 frames per second
        # Go ahead and update the screen with what we've drawn.
        clock.tick(30)
        myfont = pygame.font.SysFont("arial",20)
        text_Group = myfont.render("Group = "+str(count), True, (0,255,0))
        text_Vel = myfont.render("Direction = "+str(max(vels))+"/50", True, (0,255,0))
        screen.blit(text_Group, (WINDOW_WIDTH-150, 0))
        screen.blit(text_Vel, (WINDOW_WIDTH-200, 20))
        pygame.display.flip()


    # Save file
    with open("velocity.txt","a+",encoding="utf-8") as f:
        for i in same_v:
            f.writelines(i+'\n')
  
    with open("swarm.txt","a+",encoding="utf-8") as f2:
        for i in swarm_n:
            f2.writelines(i+'\n')
    # Close everything down
    pygame.quit()
    f.close()
    f2.close()


if __name__ == "__main__":
    main()

















