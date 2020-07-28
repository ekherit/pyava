#!/usr/bin/python3
import urllib3
import json
import io
import time
http = urllib3.PoolManager()

class RequestError(Exception):
    def __init__(self, rspnd):
        self.respond = rspnd

#******************  UTILITY TO COMMUNICATE WITH NODE ************
request_id=0
def request(host,endpoint,method, params):
    global request_id
    request_id+=1
    respond = http.request(
            'POST',
            host+endpoint,
            headers={ 'Content-Type': 'application/json' },
            body=json.dumps({'jsonrpc' : '2.0', 'id': request_id, 'method' : method, 'params' : params })
            )
    j = json.loads(respond.data.decode('utf-8'))
    #print(j)
    if 'result' in j:
        return j['result']
    elif 'error' in j:
        #raise Exception('error',j['error'])
        raise RequestError(j['error'])
    else:
        raise Exception('Unknown error')

## *********** ADMIN API *****************************
#
#def admin_getNodeID(host):
#    respond = request(host,'/ext/admin', 'admin.getNodeID', {})
#    return respond['nodeID']
#
#def admin_getNetworkName(host):
#    respond = request(host,'/ext/admin', 'admin.getNetworkName', {})
#    return respond['networkName']
#
#def admin_getNetworkID(host):
#    respond = request(host,'/ext/admin', 'admin.getNetworkID', {})
#    return respond['networkID']
#
# **************** INFO API ************************************ 

def info_eval(host, command, params = {}):
    respond = request(host,'/ext/info','info.'+command, params)
    return respond

def info_getBlockchainID(host, alias):
    return info_eval(host,'getBlockchainID', {'alias' : alias})['blockchainID']

def info_getNetworkID(host):
    return info_eval(host,'getNetworkID')['networkID']

def info_getNetworkName(host):
    return info_eval(host,'getNetworkName')['networkName']

def info_getNodeID(host):
    return info_eval(host,'getNodeID')['nodeID']

def info_getNodeVersion(host):
    return info_eval(host,'getNodeVersion')['version']


def info_getPeers(host):
    return info_eval(host,'peers')['peers']


# ******************* Platform API *************************

def platform_eval(host,command, params = {}):
    respond = request(host,'/ext/P','platform.'+command,params)
    return respond

def platform_createAccount(host, username, password):
    return platform_eval(host, 'createAccount',{'username' : username, 'password' : password})['address']

def platform_getAccount(host,account_address):
    respond = request(host,'/ext/P','platform.getAccount',{'address': account_address})
    return respond

def platform_importAVA(host, username, password, address, nonce):
    respond = platform_eval(host,'importAVA',{'username':username, 'password' : password, 'to': address, 'payerNonce' : nonce})
    return respond['tx']

def platform_exportAVA(host, username, password, address, nonce):
    respond = platform_eval(host,'exportAVA',{'username':username, 'password' : password, 'to': address, 'payerNonce' : nonce})
    return respond['tx']

def platform_issueTx(host, tx):
    respond = platform_eval(host,'issueTx',{'tx':tx})
    return respond


def platform_getCurrentValidators(host):
    return platform_eval(host,'getCurrentValidators')['validators']
    #respond = request(host,'/ext/P','platform.getCurrentValidators',{})
    #return respond

def platform_exportKey(host, username, password, address):
    return platform_eval(host,'exportKey', {'username':username, 'password':password, 'address':address})['privateKey']

def platform_addDefaultSubnetValidator(host, payerNonce, destination, starttime, endtime, stake_amount, delegationFeeRate):
    #a = platform_getAccount(host, platform_address)
    #nonce = int(a['nonce'])
    #balance = 
    node_id = info_getNodeID(host)
    respond = platform_eval(host,'addDefaultSubnetValidator', { \
            'id': node_id, \
            'payerNonce' : payerNonce, \
            'destination' : destination, \
            'startTime' : starttime, \
            'endTime' : endtime, \
            'stakeAmount' : stake_amount, \
            'delegationFeeRate' : delegationFeeRate \
                    })
    return respond['unsignedTx']

def platform_sign(host, username, password, tx, signer):
    respond = platform_eval(host,'sign', { \
            'username' : username, \
            'password' : password, \
            'tx'       : tx,       \
            'signer'   : signer })
    return respond['tx']



def platform_getPendingValidators(host):
    r = platform_eval(host, 'getPendingValidators')
    return r['validators']

def platform_getCurrentValidators(host):
    r = platform_eval(host, 'getCurrentValidators')
    return r['validators']

#************** KEYSTORE API *********************************************

def keystore_createUser(host, username, password):
    return request(host,'/ext/keystore',  'keystore.createUser', { 'username':username, 'password' : password })

def keystore_deleteUser(host, username,password):
    return request(host,'/ext/keystore',  'keystore.deleteUser', { 'username':username, 'password' : password })['success']

def keystore_exportUser(host, username, password):
    return request(host,'/ext/keystore',  'keystore.exportUser', { 'username':username, 'password' : password })['user']

def keystore_importUser(host, username, password, user):
    return request(host,'/ext/keystore',  'keystore.importUser', { 'username':username, 'password' : password, 'user': user })['success']


def keystore_listUsers(host):
    return request(host,'/ext/keystore',  'keystore.listUsers', {})['users']


#************** AVM API *********************************************

def avm_createAddress(host, username, password): 
    return request(host,'/ext/bc/X', 'avm.createAddress',{'username' : username, 'password' : password})['address']

def avm_listAddresses(host, username, password): 
    return request(host,'/ext/bc/X', 'avm.listAddresses',{'username' : username, 'password' : password})['addresses']

def avm_getBalance(host, address):
    respond = request(host,'/ext/bc/X','avm.getBalance',{'address': address, 'assetID' : 'AVA'})
    return respond['balance']

def avm_getAssetBalance(host, assetId, address):
    respond = request(host,'/ext/bc/X','avm.getBalance',{'address': address, 'assetID' : assetId})
    return respond['balance']

def avm_getBalances(host, user, password):
    adr_list = avm_listAddresses(host, user, password)
    result = []
    total_balance=0
    for a in adr_list:
        balance = int(avm_getBalance(host,a))
        item = {'address' : a, 'balance' : balance}
        total_balance+=balance
        result.append(item)
        print(item)
    #print("total: ", total_balance)
    return result

def avm_getTotalBalance(host, user, password):
    lst = avm_getBalances(host, user, password)
    total = 0
    for a in lst:
        total+=a['balance']
    return total

def avm_getUTXOIDs(host, address):
    respond = request(host,'/ext/bc/X','avm.getBalance',{'address': address, 'assetID' : 'AVA'})
    return respond['utxoIDs']

def avm_getUTXO(host, address):
    respond = request(host,'/ext/bc/X','avm.getUTXOs',{'address': address})
    return respond['utxos']

def avm_issueTx(host, tx):
    respond = request(host,'/ext/bc/X','avm.issueTx',{'tx': tx})
    return respond['txID']

def avm_signMintTx(host, tx, minter, username, password):
    respond = request(host,'/ext/bc/X','avm.signMintTx',{'tx': tx, 'minter':minter, 'username' : username, 'password' : password})
    return respond['tx']

def avm_getTxStatus(host, txID):
    respond = request(host,'/ext/bc/X','avm.getTxStatus',{'txID': txID})
    return respond['status']

def avm_getTx(host, txID):
    respond = request(host,'/ext/bc/X','avm.getTx',{'txID': txID})
    return respond

def avm_exportAVA(host,  ammount, address, username, password):
    return request(host,'/ext/bc/X', 'avm.exportAVA',{'to' : address, 'amount' : ammount, 'username' : username, 'password' : password} )['txID']

def avm_importAVA(host,  address, username, password):
    return request(host,'/ext/bc/X', 'avm.exportAVA',{'to' : address, 'username' : username, 'password' : password} )['txID']


def avm_send(host, assetID, amount, to_address,  username, password):
    return request(host,'/ext/bc/X', 'avm.send',{'assetID' : assetID, 'amount' : amount, 'to' : to_address,  'username' : username, 'password' : password} )['txID']


def avm_exportKey (host, username, password, address):
    return request(host,'/ext/bc/X', 'avm.exportKey',{'username' : username, 'password' : password,  'address' : address  } )['privateKey']

def avm_importKey (host, username, password, privKey):
    return request(host,'/ext/bc/X', 'avm.importKey',{'username' : username, 'password' : password,  'privateKey' : privKey  } )['address']

#*************** HELTH IP *************************

def health_getLiveness(host): 
    return request(host,'/ext/health', 'health.getLiveness',{})




