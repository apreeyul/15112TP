####################################################################################################################
'''
Student: April Wu 
AndrewID: aprilw
Game: 8 Ball Pool

Implemented Features: 

To-be implemented: 

lines 15-140: Original Code
lines 141-148: From https://github.com/jatinmandav/Gaming-in-Python/blob/master/8_Ball_Pool/8BallPool.py
lines 149- : Original Code
'''
####################################################################################################################
import pygame, random, math, sys, copy
from pygame.locals import *

pygame.init()
width = 1200 #88in. pool table + 60 margins x 2 = 1000 & 200 more for p1 & p2 standings
height = 560
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("8 Ball Pool")
background = pygame.draw.rect(screen, (255,255,240), (0,0,width,height))
pygame.display.update()
time = pygame.time.Clock()
solidBalls = pygame.sprite.Group()
stripeBalls = pygame.sprite.Group()
allBalls = pygame.sprite.Group()
#moves is a counter that counts how many moves have been made
moves = 0

#NOTE: blit fills the screen with an image the same way pygame.fill fills the screen with a color
class Pocket(object):
	def __init__(self, x, y): #x and y = location of pockets 
		self.length = 50
		self.width = 50
		self.r = self.width//2
		self.x = x
		self.y = y
		self.color = (59,39,19)

	def drawPockets(self):
		pygame.draw.circle(screen, self.color, (self.x,self.y), self.r)
		pygame.display.update()

	#detect if the ball is in the pocket --> if true disappear from surface and add to player's 
	def ballInPocket(self,ball):
		if self.x-self.r <= ball.rect.x + ball.r <= self.x + self.r:
			return True
		elif self.y-self.r <= ball.rect.y + ball.r <= self.y + self.r:
			return True
		return False

class Ball(pygame.sprite.Sprite):
	def __init__(self, x, y, color): #x,y the location of the ball (center)
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((15,15)) #the ball is 15x15
		self.color = color
		self.image.fill(self.color)
		self.rect = self.image.get_rect() #update rect to update ball pos
		self.rect.center = (int(x), int(y))
		self.rect.x = x
		self.rect.y = y
		self.r = 15
		#default velocity is 0
		self.vx = 0
		self.vy = 0
		self.force = 0
		self.angle = 0
		self.isStripe = False

	def drawBall(self):
		pygame.draw.circle(screen, self.color, (self.rect.center), self.r)
		if self.isStripe: 
			pygame.draw.line(screen, (255,255,255), (self.rect.x-self.r//2,self.rect.y-self.r//2), \
									(self.rect.x+self.r//2,self.rect.y+self.r//2),3)
		pygame.display.update()
		#screen.blit(self.image, (self.rect.x,self.rect.y), area=None)
	def moveBall(self, other): #other is a ball or a stick
		self.rect.x += other.rect.x * math.cos(other.angle)
		self.rect.y += other.rect.y * math.sin(other.angle)
		other.rect.x -= self.rect.x * math.cos(other.angle)
		other.rect.y -= self.rect.y * math.sin(other.angle)

class Stick(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y 
		self.length = 200
		self.width = 50
		self.friction = 0.3  #max is 0.7
		#self.angle = 

	def moveStick(self):
		pass

class Table(object):
	def __init__(self):
		self.length = 880
		self.width = 440 
		self.margin = 60 
		self.friction = 0.005

	def borderDim(self):
		#returns left --> top --> right --> bottom
		return [(self.margin,self.margin),(self.margin,self.width+self.margin*0.8),\
				(self.margin,self.margin),(self.length+self.margin*0.8,self.margin)]

	def hitBoard(self,ball):
		pass

	def drawTable(self):
		#table
		pygame.draw.rect(screen, (10, 108, 3), (self.margin,self.margin,self.length,self.width))
		#strings
		stringGap = self.length//4
		for i in range(1,4):
			height = self.margin + self.width
			pygame.draw.rect(screen, (192,192,192),(self.margin+stringGap*i,self.margin,self.margin*0.05,self.width))
		#borders: left, top, right, bottom 
		pygame.draw.rect(screen, (54, 37, 20),(self.margin,self.margin,self.length,self.margin*0.2))
		pygame.draw.rect(screen, (54, 37, 20),(self.margin,self.width+self.margin*0.8,self.length,self.margin*0.2))
		pygame.draw.rect(screen, (54, 37, 20),(self.margin,self.margin,self.margin*0.2,self.width))
		pygame.draw.rect(screen, (54, 37, 20),(self.length+self.margin*0.8,self.margin,self.margin*0.2,self.width))
		pygame.display.update()

poolTable = Table()

#sample pocket object to help with coords
sPocket = Pocket(None,None)
#pocket coords from left corner and going clockwise
pocketCoords = [(poolTable.margin+sPocket.r,poolTable.margin+sPocket.r), (poolTable.margin+poolTable.length//2,poolTable.margin+sPocket.r),\
			 	(poolTable.margin+poolTable.length-sPocket.r,poolTable.margin+sPocket.r),(poolTable.margin+poolTable.length-sPocket.r,poolTable.margin+poolTable.width-sPocket.r),\
			 	(poolTable.margin+poolTable.length//2,poolTable.margin+poolTable.width-sPocket.r),(poolTable.margin+sPocket.r,poolTable.margin+poolTable.width-sPocket.r)]

pockets = []
for x in range(6): #the six pockets of the table
	x,y = pocketCoords[x]
	pockets.append(Pocket(x,y))


#colors are in the order red, orange, yellow, green, blue, purple, brown
colors = [(255,0,0),(255,166,33),(255, 219, 88),(156,255,8),(71,169,255), (204,204,255), (103,77,60)]
balls = []
#using sBall Dimensions for ball bRad (bRad)
sBall = Ball(10, 10, (0,0,0)) 

w = poolTable.width + poolTable.margin*2
start = int(poolTable.width*0.35)
bRad = sBall.r
ballLoc =[(start, w//2 - 4*bRad),(start + 2*bRad, w//2 - 3*bRad),(start, w//2 - 2*bRad),\
		  (start + 4*bRad, w//2 - 2*bRad),(start + 2*bRad, w//2 - 1*bRad),(start, w//2),\
		  (start + 6*bRad, w//2 - 1*bRad),(start + 8*bRad, w//2),\
		  (start + 6*bRad, w//2 + 1*bRad),(start + 2*bRad, w//2 + 1*bRad),(start, w//2 + 2*bRad),\
		  (start + 4*bRad, w//2 + 2*bRad),(start + 2*bRad, w//2 + 3*bRad),(start, w//2 + 4*bRad)]

eightBall = Ball(start + 4*bRad, w//2, (0,0,0))
cueBall = Ball(poolTable.length * (3/4) + poolTable.margin, poolTable.width*0.5 + poolTable.margin, (255,255,255))

bLocCopy = copy.copy(ballLoc)
for b in range(7):
	x,y = random.choice(bLocCopy)
	newBall = Ball(x,y, colors[b])
	bLocCopy.remove((x,y))
	solidBalls.add(newBall)
	balls.append(newBall)
for b in range(7):
	x,y = random.choice(bLocCopy)
	newBall = Ball(x,y, colors[b])
	bLocCopy.remove((x,y))
	newBall.isStripe = True
	stripeBalls.add(newBall)
	balls.append(newBall)

allBalls.add(eightBall)
allBalls.add(stripeBalls)
allBalls.add(solidBalls)

while len(bLocCopy) > 0:
	for b in range(len(balls)):
		ball = balls[b]
		location = random.choice(bLocCopy)
		ball.x, ball.y = location
		bLocCopy.remove(location)

#collision detection 
def distance(x1,y1,x2,y2):
	x1,y1 = ball1.x, ball1.y
	x2,y2 = ball2.x, ball2,y
	if distance(x1,y1,x2,y2) < ball1.r:
		return True
	return False

#collision algorithm between balls
def ballsCollide(ball1, ball2):
	dx = ball1.rect.x - ball2.rect.x
	dy = ball2.rect.y - ball2.rect.y
	tangent = atan2(dx,dy)

def hit(stick, ball):
	pass 

class PlayPool(object):
	#MAIN LOOP: --> exit loop ends the game
	gameOver = False
	while not gameOver:
		time.tick(60)
		#self.timerFired(time)
		for event in pygame.event.get(): #returns a list of all the events that have happened
			if event.type == pygame.QUIT:
				gameOver = True		
			if event.type == pygame.MOUSEBUTTONDOWN:
				x,y = pygame.mouse.get_pos()
				cueBall.rect.y = y
				if moves <= 0:
					if x < poolTable.length * (3/4):
						cueBall.rect.x = poolTable.length * (3/4) + poolTable.margin
					elif x > poolTable.length + poolTable.margin - cueBall.r:
						cueBall.rect.x = poolTable.length + poolTable.margin + cueBall.r
					else:
						cueBall.rect.x = x	
				else:
					cueBall.rect.x = x
			if event.type == pygame.KEYDOWN:
				if pygame.key.get_pressed()[pygame.K_LEFT]:
					cueBall.rect.x -=10
				elif pygame.key.get_pressed()[pygame.K_RIGHT]:
					cueBall.rect.x += 10

		poolTable.drawTable()
		for p in pockets:
			p.drawPockets()
		cueBall.drawBall()
		eightBall.drawBall()
		for b in stripeBalls:
			b.drawBall()
		for b in solidBalls:
			b.drawBall()
		for solid in solidBalls:
			for stripe in stripeBalls:
				collided = pygame.sprite.collide_circle(solid, stripe)
				if collided:
					ballsCollide(solid, stripe)

		pygame.display.update()

pygame.quit()
