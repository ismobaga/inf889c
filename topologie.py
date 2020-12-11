#!/usr/bin/python

import os, sys
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

from subprocess import call

def topologie():
	call(["mn", "-c"])

	net = Mininet(controller=RemoteController, link=TCLink)
	c0 = net.addController('c0', controller=RemoteController, ip="127.0.0.1", port=6633)

	h1 = net.addHost('h1', ip='10.0.0.1', mac="00:00:00:00:00:01")
	h2 = net.addHost('h2', ip='10.0.0.2', mac="00:00:00:00:00:02")
	h3 = net.addHost('h3', ip='10.0.0.3', mac="00:00:00:00:00:03")
	h4 = net.addHost('h4', ip='10.0.0.4', mac="00:00:00:00:00:04")
	h5 = net.addHost('h5', ip='10.0.0.5', mac="00:00:00:00:00:05")
	h6 = net.addHost('h6', ip='10.0.0.6', mac="00:00:00:00:00:06")
	h7 = net.addHost('h7', ip='10.0.0.7', mac="00:00:00:00:00:07")
	h8 = net.addHost('h8', ip='10.0.0.8', mac="00:00:00:00:00:08")
	h9 = net.addHost('h9', ip='10.0.0.9', mac="00:00:00:00:00:09")
	h10 = net.addHost('h10', ip='10.0.0.10', mac="00:00:00:00:00:10")

	s1=net.addSwitch('s1')
	s2=net.addSwitch('s2')
	s3=net.addSwitch('s3')
	s4=net.addSwitch('s4')
	s5=net.addSwitch('s5')
	s6=net.addSwitch('s6')
	s7=net.addSwitch('s7')

	net.addLink(h1, s2)
	net.addLink(h2, s2)
	net.addLink(h3, s3)
	net.addLink(h4, s3)
	net.addLink(h5, s4)
	net.addLink(h6, s4)
	net.addLink(h7, s6)
	net.addLink(h8, s6)
	net.addLink(h9, s7)
	net.addLink(h10, s7)
	net.addLink(s2, s3)
	net.addLink(s2, s1)
	net.addLink(s3, s1)
	net.addLink(s1, s4)
	net.addLink(s4, s5)
	net.addLink(s1, s5)
	net.addLink(s6, s7)
	net.addLink(s6, s5)
	net.addLink(s7, s5)

	net.start()

	net.pingAllFull()

	CLI(net)
	net.stop()

if __name__ = '__main__':
	setLogLevel('info')
	topologie()