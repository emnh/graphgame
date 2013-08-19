#!/usr/bin/env python

# ideas:
# animated alpha masks
# animated colors
# (looped animation)
#
# two systems: one painting from a parallel system in another image
#
# 3d box: z-value affects color/mass/radius etc
#
# matlab for performance
#
# directed edges

from graph import *
from pygame import *
from time import sleep
import copy
import math
import operator
import os
import pygame
import random
import re
import sys

class Clr(object):
    def __getattr__(self, name):
        return colordict.THECOLORS[name]
clr = Clr()

class NumList(list):

    def foreach(self, fun):
        return NumList([fun(a) for a in self])

    def __neg__(x):
        return NumList([-a for a in x])

    def elength(x):
        'Euclidean length'
        return sum(x**2)**0.5

    pass

for f in 'add', 'sub', 'mul', 'div', 'pow':
    fn = '__' + f + '__'
    fn2 = '__i' + f + '__'
    fun = getattr(operator, f)
    def fbody(x, y, fun=fun):
        if isinstance(y, list):
            l = [fun(a, b) for (a, b) in zip(x, y)]
        else:
            l = [fun(a, y) for a in x]
        return NumList(l)
    setattr(NumList, fn, fbody)
    setattr(NumList, fn2, fbody)

imgfname = 'image.jpg'
if os.path.exists(imgfname):
    theimg = image.load(imgfname)

def createmask(s, r):
    mask = Surface(s.get_size(), 0, s)
    pa = surfarray.pixels_alpha(mask)
    centre = NumList((r, r))
    maxd = r
    for i in range(0, 2*r):
        for j in range(0, 2*r):
            pos = NumList((i, j))
            d = (pos - centre).elength()
            if d >= maxd:
                sc = 0
            else:
                #sc = 1
                sc = (1 - d / float(maxd))
                #sc =  d / float(maxd)
            sc_alpha =  sc ** Options.alphaspeed
            pa[i][j] = int(sc_alpha * 255)
    return mask

def drawimgpart(n, s, r, mask):
    iw, ih = theimg.get_size()
    ix = random.randint(0, iw - r)
    iy = random.randint(0, ih - r)
    #ix, iy = n.cpos
    #k = 50
    #ix = (ix + random.randint(-k, k)) % iw
    #iy = (iy + random.randint(-k, k)) % ih
    s.blit(theimg, (0, 0), (ix, iy, ix + r, iy + r))
    pa = surfarray.pixels_alpha(mask)
    psa = surfarray.pixels_alpha(s)
    psa[:] = pa[:]
    del pa, psa
    #s.blit(s2, (0, 0))
    return s 
            

def drawgradientcircle(s, r, nclr, mask):
    DEBUGALPHA = False

    clr1 = NumList(nclr)
    del clr1[3]
    clr2 = NumList([0, 0, 0])

    p = surfarray.pixels3d(s)
    centre = NumList((r, r))
    maxd = r
    for i in range(0, 2*r):
        for j in range(0, 2*r):
            pos = NumList((i, j))
            d = (pos - centre).elength()
            if d >= maxd:
                sc = 0
            else:
                sc = (1 - d / float(maxd))
                #sc = d / float(maxd)
                sc = sc ** Options.gradspeed
            rgb = clr2 + (clr1 - clr2) * sc
            rgb = rgb.foreach(int)
            p[i][j] = rgb
    pa = surfarray.pixels_alpha(mask)
    psa = surfarray.pixels_alpha(s)
    psa[:] = pa[:]
    del p, pa, psa
    return s

def drawoldgradientcircle(s, r, nclr, mask):
    clr1 = NumList(nclr)
    clr2 = NumList((0, 0, 0, 0))
    for i in range(r, 0, -1):
        def cutclr(c):
            return max(min(c, 255), 0)
        color = clr1 + (clr2 - clr1) * (i/float(r)) #** Options.gradspeed
        color = color.foreach(cutclr)
        draw.circle(s, color, [r, r], i)
    return s

T_PIC = 0
T_CIRC = 1

def makenewnodeclass(nodetype):
    class NewNode(Node):

        ntype = nodetype

        def __init__(self, name):
            super(NewNode, self).__init__(name)
            self.clr = random.choice(colordict.THECOLORS.values())
            x, y = random.randint(0, w), random.randint(0, h)
            self.cpos = NumList([x, y])
            #self.speed = NumList([random.randint(0, 10), random.randint(0, 10)])
            self.speed = NumList([0, 0])
            self.mass = Options.maxmass # random.randint(Options.minmass, Options.maxmass)
            self.radius = random.randint(Options.minmass, Options.maxmass)

        def _getimg(self):
            #self.redraw()
            return self._img
        
        def _setimg(self, img):
            self._img = img

        def redraw(n):
            n._img = Surface([2*n.radius, 2*n.radius], HWSURFACE | SRCALPHA, 32)
            n._img.fill([0, 0, 0, 0])
            try:
                mask = n.mask
            except:
                n.mask = None
            if n.mask == None or n.mask.get_size()[0] != 2*n.radius:
                print "new mask for", n.name
                n.mask = createmask(n._img, n.radius)
            if n.ntype == T_PIC:
                n._img = drawimgpart(n, n._img, n.radius, n.mask)
            elif n.ntype == T_CIRC:
                n.img = drawgradientcircle(n._img, n.radius, n.clr, n.mask)

        def dup(self, newname):
            new = copy.copy(self)
            new.name = newname
            new.edges = []
            new.speed = NumList([0, 0])
            x, y = random.randint(0, w), random.randint(0, h)
            new.cpos = NumList([x, y])
            new._getimg = lambda: self.img
            return new

        img = property(_getimg, _setimg)
    return NewNode

PicNode = makenewnodeclass(T_PIC)
CircNode = makenewnodeclass(T_CIRC)

class PlanetGraph(Graph):

    def createSystem(g, (w, h)):
        for i in range(0, Options.nodes):
            g.newNode(i)
            
    def newNode(g, name):
        i = 1 #random.randint(0, 1)    
        if i == 0:
            n = PicNode(name)
        else:
            n = CircNode(name)
        
        g.add(n)
        n.redraw()

        for j in range(len(g.nodes)):
            n2 = g.nodes[j]
            if n2 == n: continue
            e = Edge(n, n2)
            e.clr = random.choice(colordict.THECOLORS.values())
            e.gravforce = 2 #random.uniform(1, 2)
            #if not random.randint(0, 2):
            g.add(e)


class Options(object):
    lines = False
    fill = False
    gradspeed = 5 / 2 
    alphaspeed = 15 / 2
    usefriction = False
    minmass = 10
    maxmass = 20
    nodes = 5
    speedlimit = 10 # for dups
    driftlimit = 100 # for dups
    friction = 0.90 # new speed pr step
    collision = 'none'
    collisiontypes = ['bounce', 'merge', 'none']
    speedinc = 0.1

if __name__ == "__main__":
    #w, h = 1600, 1200
    w, h = 1440,900
    size = NumList([w,h])
    maxsize = sum(size ** 2) ** 0.5

    g = PlanetGraph()
    g.createSystem((w,h))
    
    display.init()
    a = display.set_mode(size, HWSURFACE | FULLSCREEN | SRCALPHA)
    s = display.get_surface()
    s.fill((0, 0, 0, 0))
    #g.nodes[0].mass = 1000
    step = 0
    while True:
        step += 1
        if Options.fill:
            s.fill((0, 0, 0, 0))
        #for node in g.nodes:
        #    node.speed = NumList([0, 0])
        for edge in g.edges:
            n1, n2 = edge.nodes
            if Options.lines:
                draw.line(s, edge.clr, n1.cpos, n2.cpos)
            dv = n2.cpos - n1.cpos
            dvl = sum(dv**2)**0.5
            if dvl > 0:
                #dv = dv / (dvl ** e.gravforce)
                # normalize force direction vector: dv / dvl
                # normalize force magnitude: dvl / maxsize
                # force is strong when distance is small: 1 - dvl / maxsize
                # gravity type: ** gforce
                gforce = edge.gravforce
                dv = dv / dvl * ((1 - dvl / maxsize) ** gforce)
                # dv / dvl - dv / maxsize
                dv = dv * Options.speedinc

            # collision detection
            if dvl < (n1.radius + n2.radius) / 2:
                if Options.collision == 'merge':
                    nmin = n2
                    name = nmin.name
                    g.remove(nmin)
                    g.newNode(nmin.name)
                    n1.mass += n2.mass
                    n1.redraw()
                if Options.collision == 'bounce':
                    # TODO: take mass and hit point into account
                    a1 = math.atan2(*n1.speed)
                    a2 = math.atan2(*n2.speed)
                    a1new = a1 + math.pi - (a2 - a1)
                    a2new = a2 + math.pi - (a1 - a2)
                    e1 = n1.speed.elength()
                    e2 = n2.speed.elength()
                    n1.speed = NumList([math.cos(a1new), math.sin(a1new)]) * e1
                    n2.speed = NumList([math.cos(a2new), math.sin(a2new)]) * e2
                    #n1.speed = -n1.speed
                    #n2.speed = -n2.speed

            # alter speed by gravitational forces
            n1.speed += dv * n2.mass / Options.maxmass / n1.mass
            if not isinstance(edge, DirectedEdge):
                n2.speed += -dv * n1.mass / Options.maxmass / n2.mass
            else: # assume n1 dupnode
                if dvl > Options.driftlimit:
                    print 'removing drifter', n1.name
                    g.remove(n1)
        #g.nodes[0].speed = NumList([0, 0])

        def shoot(old):
            new = old.dup(len(g.nodes))
            #new.cpos = NumList([w/2, h])
            new.cpos = old.cpos
            new.mass = (old.mass / float(Options.maxmass))**2
            #old.mass += 5
            #new.speed = NumList([random.uniform(-5, 5), -4])
            e = DirectedEdge(new, old)
            #e = Edge(new, g.nodes[-2])
            #e2 = Edge(new, g.nodes[-1])
            e.clr = clr.blue
            e.clr2 = clr.yellow
            e.gravforce = 2 #random.uniform(1, 2)
            #e2.gravforce = random.uniform(1, 2)
            g.add(new)
            g.add(e)
            #g.add(e2)

        if len(g.nodes) < 200 and step % 20 == 0:
            #idx = random.randint(0, len(g.nodes)-1)
            #old = g.nodes[idx]
            for old in g.nodes[0:Options.nodes-1]:
                shoot(old)

        for n in g.nodes:
            #n.speed[1] += 0.05
            # friction
            if Options.usefriction:
                n.speed = n.speed * Options.friction
            cpos = (n.cpos - NumList(n.img.get_size()) / 2).foreach(int)
            #if step % 5 == 0:
            #    print 'redraw', n.name
            if n.ntype == T_PIC:
                n.redraw()
            s.blit(n.img, cpos)
            #draw.circle(s, n.clr, n.cpos.foreach(int), 1)
            if n.speed.elength() > Options.speedlimit:
                    print 'removing speeder', n.name
                    g.remove(n)
            n.cpos += n.speed
            for i in range(len(n.cpos)):
                if n.cpos[i] >= size[i] or n.cpos[i] <= 0:
                    n.speed[i] = -n.speed[i]
                    # edge bounce speed loss
                    n.speed[i] *= 0.5
                    
                    # edge reshoot
                    #n.cpos = NumList([w/2, h])
                    #n.speed = NumList([random.uniform(-7, 7), -8])
                    
                    # edge removal
                    #shoot(n)
                    #try:
                    #    g.remove(n)
                    #except:
                    #    pass
        display.update()
        ev = pygame.event.get([KEYDOWN,KEYUP])
        if ev:
            if ev[0].type == KEYDOWN:
                u = ev[0].unicode
                if u == 'q':
                    #news = s.copy()
                    #alpha = surfarray.array_alpha(s)
                    #p = surfarray.pixels3d(news)
                    #for i in range(0, w):
                    #    for j in range(0, h):
                    #        p[i][j] = [alpha[i][j]]*3
                    #del p, alpha
                    #image.save(news, 'alphs.tga')
                    sys.exit()
                elif u == 'f':
                    Options.fill = not Options.fill
                elif u == 'F':
                    Options.usefriction = not Options.usefriction
                elif u == 'l':
                    Options.lines = not Options.lines
                elif u == '+':
                    Options.gradspeed += 1
                    for n in g.nodes: n.redraw()
                elif u == '-':
                    Options.gradspeed -= 1
                    for n in g.nodes: n.redraw()
                elif u == 'c':
                    idx = Options.collisiontypes.index(Options.collision)
                    tlen = len(Options.collisiontypes)
                    idx = (idx + 1) % tlen
                    Options.collision = Options.collisiontypes[idx]
                elif u == 's':
                    fnames = os.listdir('dumps')
                    seqs = []
                    for nm in fnames:
                        match = re.search('^dump([0-9]+).jpg$', nm)
                        if match:
                            seq = int(match.group(1))
                            seqs.append(seq)
                    seq = max(seqs) + 1
                    fname = 'dumps/dump' + str(seq).rjust(3, '0') + '.jpg'
                    fname2 = 'dumps/dump' + str(seq).rjust(3, '0') + '.tga'
                    if os.path.exists(fname):
                        print 'should not happen:save file exists'
                        sys.exit()
                    print 'saving', fname
                    image.save(s, fname2)
                    os.system('convert %s %s' % (fname2, fname))
                    os.unlink(fname2)
        sleep(0.01)
