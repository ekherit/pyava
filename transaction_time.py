from ava import *
import time
import datetime
HOST ='127.0.0.1:9650'
#RHOST ='https://bootstrap.ava.network:21000' 

alisa='alisa'
alisa_pass = 'Alisa#12345_ALISA'
alisa_addr ='X-MrPGQFtvnW8UL8FDSgHueMwufQqL6RiJy' 

bob='bob'
bob_pass = 'Bob#12345_BOB'
bob_addr = 'X-2P7C5pCMX8L79bvPSpfdziB9FobMba9tW'

File = open('/tmp/ava-times.txt', 'a')

def print_balances(count, dt = 0, adt=0, sigma=0, txs=[]):
    bob_bal = avm_getBalance(HOST, bob_addr)
    alisa_bal = avm_getBalance(HOST, alisa_addr)
    tstr = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.gmtime())
    head_fmt = '#%29s %8s %10s %10s %10s %10s %10s   %-s' 
    fmt =      '%30s %8d %10d %10d %10.3f %10.3f %10.3f   %s'
    head = head_fmt % ('time', 'count', 'alisa', 'bob', 'dt,s', '<dt>,s', 'sigma, s', 'txids')  
    if count%10==0:
        print(head)
        #File.write(head+'\n')
    count+=1
    if len(txs) == 0:
        print(fmt % (tstr, count, int(alisa_bal), int(bob_bal), 0, 0, 0, 0))
        #File.write(fmt % (tstr, count, int(alisa_bal), int(bob_bal), 0, 0, 0, 0))
        #File.write('\n')
    else:
        if len(txs) > 1:
            txstr = str(txs[0])+', ...'
        else:
            txstr = str(txs[0])
        print(fmt % (tstr, count, int(alisa_bal), int(bob_bal), dt, adt,sigma, txstr))
        #File.write( % (tstr, count, int(alisa_bal), int(bob_bal), dt, adt,sigma, txstr))
        #File.write('\n')
        File.write( '%10d %10d %10d %10.3f %10.3f %10.3f #%30s\n' % (count, int(alisa_bal), int(bob_bal), dt, adt, sigma,  tstr))
    File.flush()
    

def check_tx_status(txIds):
    status = True
    for txId in txIds:
        s = avm_getTxStatus(HOST,txId)
        status = status and (s == 'Accepted')
    return status

def tx_status(txid):
    try :
        status = avm_getTxStatus(HOST,txid)
        return status == 'Accepted'
    except Exception:
        return False

def flush(username, password, to_address):
    balance = avm_getTotalBalance(HOST, username, password)
    bsend=balance
    success_send=False
    while  balance > 0:
        try:
            print("sending ",bsend) 
            txid = avm_send(HOST, 'AVA', bsend, to_address, username, password)
            print(txid)
            while not tx_status(txid):
                #print ('waiting')
                time.sleep(0.5)
            success_send = True
            balance-=bsend
            print("new balance ", balance)
        except RequestError as e:
            print (e.respond['message'])
            if e.respond['message'] == 'problem creating transaction: packer has insufficient length for input':
                bsend=bsend//2
                success_send = False
            if e.respond['message'] == 'insufficient funds':
                bsend=avm_getTotalBalance(HOST, username, password)
            if bsend == 0:
                print("Unable to send: ", e.respond['message'])
                raise RequestError(e.respond)
            

        print("cycle ")
        time.sleep(1)

    print("Final balance for user ", username,"  ",  avm_getTotalBalance(HOST, username, password))




def print_tx_status(txIds):
    stat = []
    for txId in txIds:
#        print(txId)
        stat.append(s)
        s = avm_getTxStatus(HOST,txId)
    print(stat)

def measure_trasaction_time(N=1):
    count=0
    print_balances(count)
    time_sum = 0.0
    time_sum2 = 0.0
    while True:
        t0  = time.time()
        txIds = [];
        for i in range(0,N):
            try:
                txId = avm_send(HOST,'AVA',1, bob_addr, alisa, alisa_pass)
                txIds.append(txId)
            except RequestError as e:
                if e.respond['message'] == 'insufficient funds':
                    flush(bob, bob_pass, alisa_addr)
        #print(txIds)
        while not check_tx_status(txIds) :
            #print_tx_status(txIds)
            time.sleep(0.001)
        #print_tx_status(txIds)
        t1 = time.time()
        dt = t1-t0
        time_sum+=dt
        time_sum2+=(dt*dt)
        count+=1
        average_time = time_sum/count
        sigma = (time_sum2/count - average_time*average_time)**0.5
        print_balances(count, dt,time_sum/count, sigma, txIds)
