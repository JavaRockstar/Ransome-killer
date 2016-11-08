""" Capture all packets in malware_pcap and retrieve the malicious parts """

import os
import dpkt


from settings import *
from util import *


def getPayload(filename, outputName):
    """Get payload according to some constrains.
    @parameter   filename: The pcap file you want to extract
               outputName: Write to this file

    @returns: None
    """


    ipcounter = 0

    outputFile = open(outputName, "a")
    pcapfile = dpkt.pcap.Reader(open(filename, "rb"))

    print 30 * '=' + "\n"
    print "Processing {}\n".format(filename)
    
    for ts, pkt in pcapfile:
        ipcounter += 1
        eth = dpkt.ethernet.Ethernet(pkt)
        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            continue

        """ Include only TCP/IP protocol, 
        however not sure for whether capturing ICMP protocol or not. 
        """
        ip = eth.data
        if ip.p not in (dpkt.ip.IP_PROTO_TCP, dpkt.ip.IP_PROTO_UDP):
            continue
        tcp = ip.data
        
        
        """ Get normal TCP payload """
        # if len(tcp.data) > 0 and tcp.dport != 80:
        #     outputFilep.write(' '.join(format(ord(x), 'b') for x in tcp.data) + '\n')

        
        """ Get http header """
        if tcp.dport == 80 and len(tcp.data) > 0:
            try:
                http = dpkt.http.Request(tcp.data)
            except dpkt.NeedData:
                extraction = handleErrorPacket(tcp.data)
                print "packet {}: Missing Data {}".format(ipcounter, extraction)
                outputFile.write(",".join(format(ord(x)) for x in extraction) + '\n')
            except dpkt.UnpackError:
                ''' Invalid request such as some HTML fragments, not for use now '''
                
                print "packet " + str(ipcounter) + ": Invalid Request " + tcp.data
                # outputFilep.write(' '.join(format(ord(x), 'b') for x in tcp.data) + '\n')
            else:
                print "packet " + str(ipcounter) + ": " + http.method + http.uri
                outputFile.write(",".join(format(ord(x)) for x in tcp.data) + '\n')

        # print "packet " + str(ipcounter) + " = " + str(len(tcp.data))

    outputFile.close()
    print  "Total number of packets in the pcap file: ", ipcounter


if __name__ == '__main__':
    
    """ First we handle the malware pcap """
    trainFile = open(inputMalName[0], "w")
    testFile = open(inputMalName[1], "w")

    
    # Traverse pcap files in malware_pcap 
    for catagory in range(2):
        for file in os.listdir(dirMalName[catagory]):
            filepath = os.path.join(dirMalName[catagory], file)
            if ".pcap" in file:
                getPayload(filepath, inputMalName[catagory])


    trainFile.close()
    testFile.close()
    

    """ Second we handle the normal pcap """
    trainFile = open(inputNorName[0], "w")
    testFile = open(inputNorName[1], "w")


    # Traverse pcap files in normal_pcap 
    for catagory in range(2):
        for file in os.listdir(dirNorName[catagory]):
            filepath = os.path.join(dirNorName[catagory], file)
            if ".pcap" in file:
                getPayload(filepath, inputNorName[catagory])


    trainFile.close()
    testFile.close()