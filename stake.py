from ava import *
import time


#suppose you already have account on platform

HOST = '127.0.0.1:9650'
USER = 'stake'
PASS = 'stake12345!@#$%'
PADR = '79AJ64zSNGD8965qgcJ57A7skBgVuVHSb'

def show_account() :
    r =  platform_getAccount(HOST, PADR)
    return r

def pending() :
    return platform_getPendingValidators(HOST)

def check_validating() :
    for v in platform_getCurrentValidators(HOST):
        if v['address']==PADR:
            return v
    return False


def fund(amount, address, user, password) :
    avm_exportAVA(HOST, amount, address, user, password)
    r =  platform_getAccount(HOST, address)
    tx = platform_importAVA(HOST,user, password, address, int(r['nonce'])+1)
    return platform_issueTx(HOST,tx)['txID']
    #return platform_getAccount(HOST, address)

def validate(stake_amount, address, user, password, days ):
    r =  platform_getAccount(HOST, address)
    nonce = int(r['nonce'])+1
    starttime = int(time.time())+60*5
    endtime =  starttime + days*86400
    utx  = platform_addDefaultSubnetValidator(HOST, nonce, address, starttime, endtime, stake_amount, 10000)
    tx = platform_sign(HOST,user, password, utx, address)
    return tx


def check_node_validation_status(HOST):
    validators = platform_getCurrentValidators(HOST)
    print("Total validators: ", len(validators))
    for node in  sorted(validators, key=lambda v: v['id']):
        print(node)
        if node['id'] == info_getNodeID(HOST):
            pass





