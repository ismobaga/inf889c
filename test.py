
import sys
import os
import time
import pox
import itertools
import re
from copy import deepcopy

import pox.lib.packet as pkt
import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.host_tracker

from pprint import pprint as pp

from pox.core import core
from pox.lib.recoco import Timer
from pox.lib.revent import *
from pox.lib.util import dpid_to_str


VERIFICATION_PERIODIQUE = 3 # Secondes

# credit to https://www.python.org/doc/essays/graphs/
def find_all_paths(graph, start, end, path=[]):

    path = path + [start]
    if start == end:
        return [path]
    if not graph.has_key(start):
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def trouver_chemins_hotes(hote_source, hote_destination, liste_chemins, lien_hotes_switch):

    switch_source = -1
    switch_destination = -1

    chemins = []

    for lien in lien_hotes_switch:
        if lien.get('ip_hote') ==  hote_source:
            switch_source = lien.get('switch')

        if lien.get('ip_hote') == hote_destination:
            switch_destination = lien.get('switch')

    for chemin in liste_chemins:
        if chemin[0] == switch_source and chemin[-1] == switch_destination:
            chemins.append(chemin)

    # dans le cas ou, les deux hotes sont connectes par le meme switch 
    if not chemins:
        chemins.append(switch_source)

    return chemins


class ModuleProjet889C(EventMixin):

    def __init__(self):
        super(EventMixin, self).__init__()

        self.adjs = {}
        self.switches = {}

        self.PathsCollection = []
        self.FlowsCollection = []
        self.lien_hotes_switch = []


        core.listen_to_dependencies(self, 'openflow_discovery')
        core.listen_to_dependencies(self, 'host_tracker')
        self.listenTo(core.openflow)

        core.openflow.addListenerByName("PacketIn", self._handle_PacketIn)
        core.openflow.addListenerByName("ConnectionUp", self._handle_ConnectionUp)
        core.openflow_discovery.addListenerByName("LinkEvent", self._handle_LinkEvent)  # listen to openflow_discovery
        core.host_tracker.addListenerByName("HostEvent", self._handle_HostEvent)  # listen to host_tracker

    def _handle_LinkEvent(self, event):
        '''
        Est appele
         lorsque on a un openflow_discovery_LinkEvent.
        openflow.discovery est le module qui decouvre le reseau.
        '''
        temp_liste_chemins = []
        link = event.link
        dpid1 = link.dpid1
        port1 = link.port1
        dpid2 = link.dpid2
        port2 = link.port2

        if dpid1 not in self.adjs:
            self.adjs[dpid1] = set([])
        if dpid2 not in self.adjs:
            self.adjs[dpid2] = set([])

        if event.added:
            self.adjs[dpid1].add(dpid2)
            self.adjs[dpid2].add(dpid1) 
        else:
            if dpid2 in self.adjs[dpid1]:
                self.adjs[dpid1].remove(dpid2)
            if dpid1 in self.adjs[dpid2]:
                self.adjs[dpid2].remove(dpid1)

        print "Liste d'adjacence:"
        pp(self.adjs)

        print("Recherche de chemins possibles")

        for pair in itertools.product(self.adjs, repeat=2):
            if not pair[0] == pair[1]:
                chemin = find_all_paths(self.adjs, pair[0], pair[1])

                for c in chemin:
                    if c not in temp_liste_chemins:
                        temp_liste_chemins.append(c)

        self.PathsCollection = deepcopy(temp_liste_chemins)
        # print(liste_chemins)
        # for chemin in liste_chemins:
        #     print(chemin)

    def _handle_HostEvent(self, event):

        '''
            Dans event, on aura :
                l'adresse mac (event.entry.macaddr.toStr()) de l'hote connecte
                l'id du switch qui est connecte a l'hote
                le port entrant du switch

            On peut obtenir la correspondance MAC/IP en envoyant une requete ARP et
            decoder la reponse.
            Mais pour simplifier le code, on va tricher un peu pour ce projet.
            On va reconstruire l'adresse IP.
        '''
        mac_hote = event.entry.macaddr.toStr()

        ip_hote = "10.0.0."+re.sub("^0+(?!$)", "", mac_hote.split(':')[-1])

        dict_hote_switch = {
            "hote_mac": mac_hote,
            "ip_hote" : ip_hote,
            "switch" : event.entry.dpid,
            "port_switch": event.entry.port
        }

        self.lien_hotes_switch.append(dict_hote_switch)

        # for lien in lien_hotes_switch:
        #     print(lien)

    def _handle_PacketIn(self, event):
        # pass

        packet = event.parsed
        if not packet.parsed:
            return

        ip = packet.find('ipv4')
        if ip is None:
            return

        print("\n")
        print(''+ip.srcip.toStr() +' - '+ ''+ip.dstip.toStr())

        chemins = trouver_chemins_hotes(ip.srcip.toStr(), ip.dstip.toStr(), self.PathsCollection, self.lien_hotes_switch)

        for chemin in chemins:
            print(chemin)

        print("Fin des chemins disponibles")

        # Reste a faire 
            # calculer la capacite de chaque path dans chemins
            # routeSelected = path avec la plus haute capacite
            # Pour chaque noeud dans routeSelected, installer les regles

    def _handle_ConnectionUp(self, event):
        print("Connection up")

        if not event.dpid in self.switches:
            switch = SuiviSwitch(self)
            switch.dpid = event.dpid
            self.switches[event.dpid] = switch
            switch.suivre_switch(event.connection)
     def _handle_PortStatsReceived(self, event):
        if event.connection.dpid in self.switches:
            self.switches[event.connection.dpid].traiter_stats_ports(event.stats, time.time())

class SuiviSwitch(EventMixin):
    def __init__(self, flow_tracker):
        self.connection = None
        self.is_connected = False
        self.dpid = None
        self._listeners = None
        self._connection_time = None

    def __repr__(self):
        return dpid_to_str(self.dpid)


    def suivre_switch(self, connection):
        if self.dpid is None:
            self.dpid = connection.dpid
        assert self.dpid == connection.dpid

        self.connection = connection
        self.is_connected = True
        self._listeners = self.listenTo(connection)
        self._connection_time = time.time()
        self._timer_verification_periodique = Timer(VERIFICATION_PERIODIQUE, self.lancer_verification_stats,
            recurring=True)

    def lancer_verification_stats(self):

        if self.is_connected:
            self.connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
            self._last_port_stats_query_send_time = time.time()
            print("Envoi d'une requete de stats port au switch: " + dpid_to_str(self.dpid))

    def traiter_stats_ports(self, stats, reception_time):

        print("Reception de stats a"+str(reception_time))
        print(stats)

        if not self.is_connected:
            return

        # A finir


def launch ():

    core.register(ModuleProjet889C())