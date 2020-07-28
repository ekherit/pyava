# pyava

Simple python API bindings to AVA network Gecko client ( https://github.com/ava-labs/gecko )
This is not full implementation. 

## Dependencies
 - python3 and modules urllib3, json, io
 - Gecko node with version > 0.5.7

## Stress test for Denali testnet
 - You need a user with some AVAs on it's address in keystore of Gecko node
 - Load flood.py in interactive mode
 ```sh
    python3 -i flood.py
 ```
 - Create flood users. It will automaticly save list of users and their passwords into file userlist.pickle in current directory
   ```python
    us = make_flood_users(N,amount,username, password)
   ```
   N is a number of flood users. I tested up to 10k,
   amount  is a nAVA filled users balances. Amount somehow spreaded on accounts with around ~log_2(N) transactions. It is becase
   I don't know how to create transactions with multiple UTXO.
 - Run stress test
   ```python
   stress_send(us)
   ```
   
 - You can interrupt stress sending by Cntrl-C
 
 - If flood user list already created from previous steps you can load list from file userlist.pickle
 ```python
    us = load()
   ```
 - Return funds from flood users to a address:
 ```python
  flush(us, address)
   ```
   It could take some time. And doesn't work well.

 - In order to remove users:
 ```python
   delete_users(us)
   ```
 
