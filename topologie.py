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

	s1=net.addSwitch('s1')
	s2=net.addSwitch('s2')
	s3=net.addSwitch('s3')
	s4=net.addSwitch('s4')
	s5=net.addSwitch('s5')
	s6=net.addSwitch('s6')
	s7=net.addSwitch('s7')
	s8=net.addSwitch('s8')
	s9=net.addSwitch('s9')
	s10=net.addSwitch('s10')
	s11=net.addSwitch('s11')
	s12=net.addSwitch('s12')

	net.addLink(h1, s1)
	net.addLink(h2, s2)
	net.addLink(h3, s3)
	net.addLink(h4, s10)
	net.addLink(h5, s11)
	net.addLink(h6, s12)

	net.addLink(s1, s4, bw=10)
	net.addLink(s2, s4, bw=10)
	net.addLink(s3, s4, bw=10)

	net.addLink(s4, s5, bw=3)
	net.addLink(s4, s6, bw=4)
	net.addLink(s4, s7)

	net.addLink(s5, s6, bw=3)

	net.addLink(s6, s9)
	net.addLink(s6, s10, bw=10)
	net.addLink(s6, s11, bw=10)
	net.addLink(s6, s12, bw=10)

	net.addLink(s7, s8, bw=2)
	net.addLink(s8, s9, bw=2)

	
	net.start()

	net.pingAllFull()

	CLI(net)
	net.stop()

if __name__ == '__main__':
	setLogLevel('info')
	topologie()