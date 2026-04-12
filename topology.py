# topology.py
# Creates a simple Mininet topology: 4 hosts, 1 switch
# Connect to external Ryu controller

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def create_topology():
    setLogLevel('info')
    
    # Create network with remote controller (our Ryu app)
    net = Mininet(
        controller=RemoteController,
        switch=OVSSwitch,
        link=TCLink          # TCLink allows us to set bandwidth/delay
    )
    
    print("=== Creating Traffic Classification Topology ===")
    
    # Add controller (Ryu running on localhost port 6633)
    c0 = net.addController('c0', controller=RemoteController,
                            ip='127.0.0.1', port=6633)
    
    # Add a switch
    s1 = net.addSwitch('s1', protocols='OpenFlow13')  # Use OpenFlow 1.3
    
    # Add 4 hosts
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    
    # Connect hosts to switch
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    
    print("Topology: h1, h2, h3, h4 all connected to switch s1")
    print("h1=10.0.0.1, h2=10.0.0.2, h3=10.0.0.3, h4=10.0.0.4")
    
    # Start everything
    net.build()
    c0.start()
    s1.start([c0])
    
    print("\n=== Network Started! Run tests in the CLI ===")
    print("Try: h1 ping h2")
    print("Try: h1 iperf -s &  then  h2 iperf -c 10.0.0.1 -u")
    print("="*50)
    
    # Open interactive CLI
    CLI(net)
    
    # Cleanup when you exit CLI
    net.stop()

if __name__ == '__main__':
    create_topology()