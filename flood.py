#!/bin/python3

from ava import *
import pickle
import time

host = '127.0.0.1:9650'

name_prefix='flood'
pass_prefix='flood1234#^FLOOD'

bob2 = 'bob2'
bob2_pass = 'bob21234#^BOB2'
bob2_addr = 'X-5zXZy89W15tVoz2hLmnAD8ebqXbV5aMhb'

userlist_file  = 'userlist.pickle'

def make_user_list(N):
    lst = []
    for i in range(0,N):
        name = "%s%d" % (name_prefix, i)
        password = "%s%d" % (pass_prefix, i)
        lst.append({ 'name' : name, 'password' : password, 'address' : 'none', 'txid' : 'none'})
    return lst

#user_list = make_user_list(10)


def create_users(us):
    for u in us:
        keystore_createUser(host, u['name'] ,u['password']) 
        u['address']=avm_createAddress(host, u['name'] ,u['password']) 
    return us

def create_address(us):
    for u in us:
      us['address']=keystore_createAddress(host, u['name'] ,u['password']) 
    return us


def delete_user_n(i):
    name = "%s%d" % (name_prefix, i)
    password = "%s%d" % (pass_prefix, i)
    keystore_deleteUser(host, name, password)

def delete_user(u):
    keystore_deleteUser(host,u['name'], u['password'])

def delete_users(us):
    for u in us:
        delete_user(u)

#def  fill(us, amount, username, password):
#    lst = []
#    for u in us:
#        txid = avm_send(host,'AVA',amount, u['address'], username, password)
#        status = avm_getTxStatus(host,txid)
#        while status != 'Accepted':
#            time.sleep(1)
#    return lst

def check_tx_status(txIds):
    status = True
    for txId in txIds:
        s = avm_getTxStatus(host,txId)
        status = status and (s == 'Accepted')
    return status


def save(us):
    with open(userlist_file, 'wb') as f:
        pickle.dump(us, f)

def load():
    with open(userlist_file, 'rb') as f:
        us = pickle.load(f)
    return us


def status(txid):
    try :
        status = avm_getTxStatus(host,txid)
        return status == 'Accepted'
    except Exception:
        return False




def print_balances(us):
    for u in us:
        print("%20s %30s %10d" % (u['name'], u['address'], int(avm_getBalance(host, u['address']))))

def wait(txid, sleeptime = 1):
    while not status(txid):
        time.sleep(sleeptime)

def  fill_n(us, N):
    s = 1
    idx = 0
    max_N = min(len(us), N)
    while True:
        txids = []
        for i in range(0, s):
            idx+=1
            if idx >= max_N: break;
            b = int(avm_getBalance(host, us[i]['address']))
            transfer = b//2
            if transfer > 0:
                txid = avm_send(host,'AVA',transfer, us[idx]['address'], us[i]['name'], us[i]['password'])
                print(" %s -> %s  %10d 20%s" % (us[i]['name'], us[idx]['name'], b//2, txid))
            else:
                print(" %s -> %s  %10d 20%s" % (us[i]['name'], us[idx]['name'], 0, 'none'))
            txids.append(txid)
        if idx >= max_N: break;
        s=idx+1
        while not check_tx_status(txids): time.sleep(1)
        print("**********   next round ****************************** ")

def fill(us):
    fill_n(us, len(us))

def fill_half(us):
    fill_n(us, len(us)//2)

def refill(us):
    txs = []
    for i in range(1, len(us)):
        b = int(avm_getBalance(host, us[i]['address']))
        txid = avm_send(host,'AVA',b, us[0]['address'], us[i]['name'], us[i]['password'])
        txs.append(txid)
    while not check_tx_status(txs): time.sleep(1)
    #Drop many utxo
    b = int(avm_getBalance(host, us[0]['address']))
    txid = avm_send(host,'AVA',b, us[1]['address'], us[0]['name'], us[0]['password'])
    wait(txid)
    #send back
    txid = avm_send(host,'AVA',b, us[0]['address'], us[1]['name'], us[1]['password'])
    wait(txid)
    fill_half(us)

def fill_half_from(us, amount, username, password):
    txid = avm_send(host,'AVA', amount, us[0]['address'], username, password)
    wait(txid)
    fill_n(us, len(us)//2)


def flush(us, address, Nmax=0):
    txs = []
    if Nmax==0 or Nmax > len(us): Nmax = len(us)
    for i in range(0, Nmax):
        b = int(avm_getBalance(host, us[i]['address']))
        if b > 0:
            txid = avm_send(host,'AVA',b, address, us[i]['name'], us[i]['password'])
            print(" %s -> %s  %10d %20s" % (us[i]['name'], address, b, txid))
            txs.append(txid)
    print("Waiting for confirmation")
    while not check_tx_status(txs): 
        naccepted=0
        nprocessing=0
        for txid in txs:
            status = avm_getTxStatus(host, txid)
            #print(status)
            if status == 'Accepted': 
                naccepted+=1
            if status == 'Processing': 
                nprocessing+=1
        print("Status accepted/processing = %d / %d" % (naccepted, nprocessing))
        time.sleep(1)
    print_balances(us)
    b = int(avm_getBalance(host, address))
    print('Balance for: %s is %s nAVA' % (address, b) )


def make_flood_users(N, amount, username, password):
    print("Making user list")
    us = make_user_list(N)
    print("Creating users")
    create_users(us)
    print("Saving userlist to ", userlist_file)
    save(us)
    print("Filling balances for half of users")
    fill_half_from(us, amount, username, password)
    return us

def stress_send(us):
    pivot = len(us)//2
    txs = []
    for i in range(0, pivot-1):  txs.append('none')
    dt = 1
    tps = 0  #round tps
    average_tps = 0 #total average tps
    begin_time = time.time()
    t1 = begin_time
    count = 0
    total_count=0
    fmt1 = "%10s (%10d) -- %d -> %10s (%10d)  txID = %-55s %10.2f TPS  %10.2f TPS"
    fmt2 = "%10s (%10d) <- %d -- %10s (%10d)  txID = %-55s %10.2f TPS  %10.2f TPS"
    while True:
        for i in range(0, pivot-1):
            if status(txs[i]) or txs[i] == 'none': 
                b1 = int(avm_getBalance(host, us[i]['address']))
                b2 = int(avm_getBalance(host, us[pivot+i]['address']))
                if b1 > 0:
                    txid = avm_send(host,'AVA',1, us[pivot+i]['address'], us[i]['name'], us[i]['password'])
                    print(fmt1 % (us[i]['name'], b1,1,us[pivot+i]['name'], b2,  txid, tps, average_tps))
                else:
                    #b = int(avm_getBalance(host, us[pivot+i]['address']))
                    if b2>0:
                        txid = avm_send(host,'AVA',b2, us[i]['address'], us[pivot+i]['name'], us[pivot+i]['password'])
                        print(fmt2 % (us[i]['name'], b1, b2, us[pivot+i]['name'], b2, txid, tps, average_tps))
                txs[i] = txid
                count+=1
                total_count+=1
                average_tps = total_count/(time.time()-begin_time)
        if count>0:
            t2 = time.time()
            dt = t2-t1
            tps = count/dt
            t1 = t2
            count=0
        #while not check_tx_status(txs): time.sleep(1)
        time.sleep(0.1)
