#!/usr/bin/python3

from ava import *

#host = '127.0.0.1:9650'
#rhost ='https://bootstrap.avax.network:21000' 
host ='https://testapi.avax.network:443'

print( "info_getNetworkID: ", info_getNetworkID(host) )
print( "info_getNetworkName: ", info_getNetworkName(host) )
print( "info_getBlockchainID: ", info_getBlockchainID(host,'X') )
print( "info_getNodeID: ", info_getNodeID(host) )
print( "info_getNodeVersion: ", info_getNodeVersion(host) )
print( "info_getPeers: ", info_getPeers(host) )
