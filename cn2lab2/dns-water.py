
#
# This script simulates 6 nodes configured in a "dumb bell" network. See below:
#
# Network topology
#
#				 
#				        
#	BOTNET n0 ---+       +--- n2 DNS REAL
#              |      |
#             n4 -- n5 --- n6 SERVFAIL
#             |      
# REAL n1 ---+      
#				
#				
#
#
# - All links are point-to-point with data rate 500kb/s and propagation delay 2ms
#
# Two data flows (and their applications are created):
# - A TCP flow form n0 to n2
# - A TCP flow from n1 to n3

import sys
import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point
import ns.flow_monitor

#######################################################################################
# SEEDING THE RNG
#
# Enable this line to have random number being generated between runs.

#ns.core.RngSeedManager.SetSeed(int(time.time() * 1000 % (2**31-1)))


#######################################################################################
# LOGGING
#
# Here you may enable extra output logging. It will be printed to the stdout.
# This is mostly useful for debugging and investigating what is going on in the
# the simulator. You may use this output to generate your results as well, but
# you would have to write extra scripts for filtering and parsing the output.
# FlowMonitor may be a better choice of getting the information you want.

# Logging has changed in the latest ns3 version. Some of these only works in older
# versions and some only works in newer versions.

#ns.core.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_INFO)
#ns.core.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_INFO)
#ns.core.LogComponentEnable("PointToPointNetDevice", ns.core.LOG_LEVEL_ALL)
#ns.core.LogComponentEnable("DropTailQueue", ns.core.LOG_LEVEL_LOGIC)
#ns.core.LogComponentEnable("OnOffApplication", ns.core.LOG_LEVEL_INFO)
#ns.core.LogComponentEnable("TcpWestwood", ns.core.LOG_LEVEL_LOGIC)
#ns.core.LogComponentEnable("TcpNewReno", ns.core.LOG_LEVEL_LOGIC) # works only in older ns3 versions

#ns.core.LogComponentEnable("TcpCongestionOps", ns.core.LOG_LEVEL_INFO)


# To enable logging of timestamps and nodeIDs, you can run the simulation by setting the
# environmental variable NS_LOG as follows:
#
# bash$ NS_LOG="*=prefix_time:*=prefix_node" python sim-tcp.py



#######################################################################################
# COMMAND LINE PARSING
#
# Parse the command line arguments. Some simulation parameters can be set from the
# command line instead of in the script. You may start the simulation by:
#
# bash$ ./waf shell
# bash$ python sim-tcp.py --latency=10
#
# You can add your own parameters and there default values below. To access the values
# in the simulator, you use the variable cmd.something.

cmd = ns.core.CommandLine()

# Default values
cmd.latency = 5
cmd.rate = 300000
cmd.interval = 0.01
cmd.AddValue ("rate", "P2P data rate in bps")
cmd.AddValue ("latency", "P2P link Latency in miliseconds")
cmd.AddValue ("on_off_rate", "OnOffApplication data sending rate")
cmd.Parse(sys.argv)


#######################################################################################
# CREATE NODES

nodes = ns.network.NodeContainer()
nodes.Create(6)


#######################################################################################
# CONNECT NODES WITH POINT-TO-POINT CHANNEL
#
# We use a helper class to create the point-to-point channels. It helps us with creating
# the necessary objects on the two connected nodes as well, including creating the
# NetDevices (of type PointToPointNetDevice), etc.

# Set the default queue length to 5 packets (used by NetDevices)
# The first line is for older ns3 versions and the second for new versions.
#ns.core.Config.SetDefault("ns3::DropTailQueue::MaxPackets", ns.core.UintegerValue(5))
#ns.core.Config.SetDefault("ns3::Queue::MaxPackets", ns.core.UintegerValue(5))


# To connect the point-to-point channels, we need to define NodeContainers for all the
# point-to-point channels.
n0n4 = ns.network.NodeContainer()
n0n4.Add(nodes.Get(0))
n0n4.Add(nodes.Get(4))

n1n4 = ns.network.NodeContainer()
n1n4.Add(nodes.Get(1))
n1n4.Add(nodes.Get(4))

n2n5 = ns.network.NodeContainer()
n2n5.Add(nodes.Get(2))
n2n5.Add(nodes.Get(5))

n4n5 = ns.network.NodeContainer()
n4n5.Add(nodes.Get(4))
n4n5.Add(nodes.Get(5))

n3n5 = ns.network.NodeContainer()
n3n5.Add(nodes.Get(3))
n3n5.Add(nodes.Get(5))





# create point-to-point helper with common attributes
pointToPoint = ns.point_to_point.PointToPointHelper()
pointToPoint.SetDeviceAttribute("Mtu", ns.core.UintegerValue(1500))
pointToPoint.SetDeviceAttribute("DataRate",
                            ns.network.DataRateValue(ns.network.DataRate(int(cmd.rate))))
pointToPoint.SetChannelAttribute("Delay",
                            ns.core.TimeValue(ns.core.MilliSeconds(int(cmd.latency))))

pointToPoint.SetQueue("ns3::DropTailQueue", "MaxPackets", ns.core.StringValue("5"))

#DNSp2p = pointToPoint

#DNSp2p.SetChannelAttribute("Delay",
#                           ns.core.TimeValue(ns.core.MilliSeconds(int(10))))
#DNSp2p.SetQueue("ns3::DropTailQueue", "MaxPackets", ns.core.StringValue("50"))

# install network devices for all nodes based on point-to-point links
d0d4 = pointToPoint.Install(n0n4)
d1d4 = pointToPoint.Install(n1n4)
d2d5 = pointToPoint.Install(n2n5)

d4d5 = pointToPoint.Install(n4n5)
d3d5 = pointToPoint.Install(n3n5)



# Here we can introduce an error model on the bottle-neck link (from node 4 to 5)
#em = ns.network.RateErrorModel()
#em.SetAttribute("ErrorUnit", ns.core.StringValue("ERROR_UNIT_PACKET"))
#em.SetAttribute("ErrorRate", ns.core.DoubleValue(0.02))
#d4d5.Get(1).SetReceiveErrorModel(em)


#######################################################################################
# CONFIGURE TCP
#
# Choose a TCP version and set some attributes.

# Set a TCP segment size (this should be inline with the channel MTU)
#ns.core.Config.SetDefault("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue(1448))

# If you want, you may set a default TCP version here. It will affect all TCP
# connections created in the simulator. If you want to simulate different TCP versions
# at the same time, see below for how to do that.
#ns.core.Config.SetDefault("ns3::TcpL4Protocol::SocketType",
#                          ns.core.StringValue("ns3::TcpNewReno"))
#                          ns.core.StringValue("ns3::TcpVegas"))
#                          ns.core.StringValue("ns3::TcpVeno"))
#                          ns.core.StringValue("ns3::TcpWestwood"))

# Some examples of attributes for some of the TCP versions.
#ns.core.Config.SetDefault("ns3::TcpWestwood::ProtocolType",
#                          ns.core.StringValue("WestwoodPlus"))
#ns.core.Config.SetDefault("ns3::TcpVegas::Beta", ns.core.UintegerValue(5))


#######################################################################################
# CREATE A PROTOCOL STACK
#
# This code creates an IPv4 protocol stack on all our nodes, including ARP, ICMP,
# pcap tracing, and routing if routing configurations are supplied. All links need
# different subnet addresses. Finally, we enable static routing, which is automatically
# setup by an oracle.

# Install networking stack for nodes
stack = ns.internet.InternetStackHelper()
stack.Install(nodes)

# Here, you may change the TCP version per node. A node can only support on version at
# a time, but different nodes can run different versions. The versions only affect the
# sending node. Note that this must called after stack.Install().
#
# The code below would tell node 0 to use TCP NewReno and node 1 to use TCP Westwood.
#ns.core.Config.Set("/NodeList/0/$ns3::TcpL4Protocol/SocketType",
#                   ns.core.TypeIdValue(ns.core.TypeId.LookupByName ("ns3::TcpNewReno")))
#ns.core.Config.Set("/NodeList/1/$ns3::TcpL4Protocol/SocketType",
#                   ns.core.TypeIdValue(ns.core.TypeId.LookupByName ("ns3::TcpWestwood")))


# Assign IP addresses for net devices
address = ns.internet.Ipv4AddressHelper()

address.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
if0if4 = address.Assign(d0d4)

address.SetBase(ns.network.Ipv4Address("10.1.2.0"), ns.network.Ipv4Mask("255.255.255.0"))
if1if4 = address.Assign(d1d4)

address.SetBase(ns.network.Ipv4Address("10.1.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
if2if5 = address.Assign(d2d5)

address.SetBase(ns.network.Ipv4Address("10.1.5.0"), ns.network.Ipv4Mask("255.255.255.0"))
if4if5 = address.Assign(d4d5)

address.SetBase(ns.network.Ipv4Address("10.1.4.0"), ns.network.Ipv4Mask("255.255.255.0"))
if3if5 = address.Assign(d3d5)



# Turn on global static routing so we can actually be routed across the network.
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()


def SetupUdpConnection(srcNode, dstNode, dstAddr, startTime, stopTime, INTERVAL, PACKET_SIZE, MAXPACKETS):

	echoServer = ns.applications.UdpEchoServerHelper(9)
	serverApps = echoServer.Install(dstNode)

	serverApps.Start(ns.core.Seconds(startTime))
	serverApps.Stop(ns.core.Seconds(stopTime))

	echoClient = ns.applications.UdpEchoClientHelper(dstAddr, 9)
	echoClient.SetAttribute("MaxPackets", ns.core.UintegerValue(MAXPACKETS))
	echoClient.SetAttribute("Interval",
                        ns.core.TimeValue(ns.core.Seconds (float(INTERVAL))))
	echoClient.SetAttribute("PacketSize", ns.core.UintegerValue(PACKET_SIZE))

	
	clientApps = echoClient.Install(srcNode)
	#clientApps.Start(ns.core.Seconds(startTime))
	#clientApps.Stop(ns.core.Seconds(stopTime))


#SET UP BOTNET REQUEST CONNECTION
SetupUdpConnection(nodes.Get(0), nodes.Get(3), if3if5.GetAddress(0),
                   ns.core.Seconds(0.0), ns.core.Seconds(10.0), 0.00001, 51, 100000)


# SET UP NORMAL DNS REQUEST CONNECTION
SetupUdpConnection(nodes.Get(1), nodes.Get(2), if2if5.GetAddress(0),
                   ns.core.Seconds(0.0), ns.core.Seconds(10.0), cmd.interval, 269, 10000)



#######################################################################################
# CREATE A PCAP PACKET TRACE FILE
#
# This line creates two trace files based on the pcap file format. It is a packet
# trace dump in a binary file format. You can use Wireshark to open these files and
# inspect every transmitted packets. Wireshark can also draw simple graphs based on
# these files.
#
# You will get two files, one for node 0 and one for node 1

pointToPoint.EnablePcap("All-traffic", d4d5.Get(0), True)
pointToPoint.EnablePcap("Botnet-traffic", d0d4.Get(0), True)
pointToPoint.EnablePcap("Dns-ReqAndResp-traffic", d1d4.Get(0), True)
pointToPoint.EnablePcap("Dns-Req-traffic", d2d5.Get(0), True)


#######################################################################################
# FLOW MONITOR
#
# Here is a better way of extracting information from the simulation. It is based on
# a class called FlowMonitor. This piece of code will enable monitoring all the flows
# created in the simulator. There are four flows in our example, one from the client to
# server and one from the server to the client for both TCP connections.

flowmon_helper = ns.flow_monitor.FlowMonitorHelper()
monitor = flowmon_helper.InstallAll()


#######################################################################################
# RUN THE SIMULATION
#
# We have to set stop time, otherwise the flowmonitor causes simulation to run forever

ns.core.Simulator.Stop(ns.core.Seconds(180.0))
ns.core.Simulator.Run()


#######################################################################################
# FLOW MONITOR ANALYSIS
#
# Simulation is finished. Let's extract the useful information from the FlowMonitor and
# print it on the screen.

# check for lost packets
monitor.CheckForLostPackets()

classifier = flowmon_helper.GetClassifier()

for flow_id, flow_stats in monitor.GetFlowStats():
  t = classifier.FindFlow(flow_id)
  proto = {6: 'TCP', 17: 'UDP'} [t.protocol]
  print ("FlowID: %i (%s %s/%s --> %s/%i)" % 
          (flow_id, proto, t.sourceAddress, t.sourcePort, t.destinationAddress, t.destinationPort))
          
  print ("  Tx Bytes: %i" % flow_stats.txBytes)
  print ("  Rx Bytes: %i" % flow_stats.rxBytes)
  print ("  Lost Pkt: %i" % flow_stats.lostPackets)
  print ("  Flow active: %fs - %fs" % (flow_stats.timeFirstTxPacket.GetSeconds(),
                                       flow_stats.timeLastRxPacket.GetSeconds()))
  print ("  Throughput: %f Mbps" % (flow_stats.rxBytes * 
                                     8.0 / 
                                     (flow_stats.timeLastRxPacket.GetSeconds() 
                                       - flow_stats.timeFirstTxPacket.GetSeconds())/
                                     1024/
                                     1024))


# This is what we want to do last
ns.core.Simulator.Destroy()
