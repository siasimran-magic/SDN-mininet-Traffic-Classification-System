# traffic_classifier.py
# SDN Traffic Classification System using Ryu Controller
# Classifies packets as TCP, UDP, or ICMP and maintains statistics

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, icmp
from ryu.lib import hub
import datetime

class TrafficClassifier(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]  # Use OpenFlow 1.3

    def __init__(self, *args, **kwargs):
        super(TrafficClassifier, self).__init__(*args, **kwargs)
        
        # MAC address table: remembers which port each device is on
        self.mac_to_port = {}
        
        # Traffic statistics: count packets per protocol
        self.stats = {
            'TCP': 0,
            'UDP': 0,
            'ICMP': 0,
            'OTHER': 0,
            'TOTAL': 0
        }
        
        # Start a background thread to print stats every 10 seconds
        self.monitor_thread = hub.spawn(self._monitor)
        
        self.logger.info("=== Traffic Classifier Controller Started ===")

    def _monitor(self):
        """Background thread: prints traffic stats every 10 seconds"""
        while True:
            hub.sleep(10)
            self._print_stats()

    def _print_stats(self):
        """Display traffic classification statistics"""
        total = self.stats['TOTAL']
        self.logger.info("\n" + "="*50)
        self.logger.info("  TRAFFIC CLASSIFICATION REPORT")
        self.logger.info("  Time: %s", datetime.datetime.now().strftime("%H:%M:%S"))
        self.logger.info("="*50)
        self.logger.info("  Total Packets : %d", total)
        self.logger.info("  TCP Packets   : %d (%.1f%%)", 
                        self.stats['TCP'], 
                        (self.stats['TCP']/total*100) if total > 0 else 0)
        self.logger.info("  UDP Packets   : %d (%.1f%%)", 
                        self.stats['UDP'],
                        (self.stats['UDP']/total*100) if total > 0 else 0)
        self.logger.info("  ICMP Packets  : %d (%.1f%%)", 
                        self.stats['ICMP'],
                        (self.stats['ICMP']/total*100) if total > 0 else 0)
        self.logger.info("  Other Packets : %d (%.1f%%)", 
                        self.stats['OTHER'],
                        (self.stats['OTHER']/total*100) if total > 0 else 0)
        self.logger.info("="*50 + "\n")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Called when a switch connects to the controller.
        Installs a default 'table-miss' flow rule:
        -> If no rule matches, send packet to controller (packet_in).
        """
        datapath = ev.msg.datapath          # the switch
        ofproto = datapath.ofproto          # OpenFlow protocol constants
        parser = datapath.ofproto_parser    # used to build OpenFlow messages

        # Match: everything (empty match = wildcard)
        match = parser.OFPMatch()
        
        # Action: send to controller
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        
        # Install this as a low-priority flow rule (priority=0)
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("Switch connected. Table-miss flow installed.")

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        """Helper: install a flow rule into the switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Instructions tell the switch what to do when rule matches
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        # Build the flow modification message
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout
        )
        datapath.send_msg(mod)  # Send to switch

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
        Called every time a packet arrives at the switch with no matching rule.
        This is the MAIN function — classify, learn, forward.
        """
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']      # which port did packet arrive on?

        # Parse the raw packet into layers
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)   # Ethernet layer (always present)

        if eth is None:
            return  # Not an ethernet frame, ignore

        dst_mac = eth.dst   # destination MAC address
        src_mac = eth.src   # source MAC address
        dpid = datapath.id  # switch ID (datapath ID)

        # === STEP 1: MAC LEARNING ===
        # Remember: this MAC address came from this port
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src_mac] = in_port

        # === STEP 2: CLASSIFY THE PACKET ===
        protocol_name = self._classify_packet(pkt)
        self.stats[protocol_name] += 1
        self.stats['TOTAL'] += 1
        
        self.logger.info("Packet: %s -> %s | Protocol: %s | Switch: %s | In-Port: %s",
                        src_mac, dst_mac, protocol_name, dpid, in_port)

        # === STEP 3: DECIDE WHERE TO FORWARD ===
        if dst_mac in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst_mac]  # we know the port!
        else:
            out_port = ofproto.OFPP_FLOOD  # we don't know — flood everywhere

        actions = [parser.OFPActionOutput(out_port)]

        # === STEP 4: INSTALL A FLOW RULE (so next packet doesn't come to controller) ===
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac, eth_src=src_mac)
            self.add_flow(datapath, priority=1, match=match, actions=actions,
                         idle_timeout=30, hard_timeout=60)

        # === STEP 5: FORWARD THIS CURRENT PACKET ===
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )
        datapath.send_msg(out)

    def _classify_packet(self, pkt):
        """
        Look at the IP layer of the packet and return protocol name.
        IP protocol numbers: 1=ICMP, 6=TCP, 17=UDP
        """
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        
        if ip_pkt is None:
            return 'OTHER'  # Not an IP packet (could be ARP, etc.)
        
        if ip_pkt.proto == 1:    # ICMP
            return 'ICMP'
        elif ip_pkt.proto == 6:  # TCP
            return 'TCP'
        elif ip_pkt.proto == 17: # UDP
            return 'UDP'
        else:
            return 'OTHER'