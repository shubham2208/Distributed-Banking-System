from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from threading import Thread
import httplib
from xmlrpclib import ServerProxy
from sys import argv
from socket import gethostname
from time import sleep
import traceback

def clientHello(name):
    global clients_array
    try:
        if clients_array.count() == 0:
            clients_array.append(name)
        return True
    except:
        return False

def resynch(sname,sip,pnum):
    global mode
    conns[sname] =  ServerProxy('http://'+str(sip)+":"+str(pnum))
    mode = 'NORMAL'


def check_servers():
    global conns
    while True:
        for sname in conns:
            try:
                if conns[sname].ping() == False:
                    del conns[sname]
                    if len(conns.keys() > 0):
                        mode = 'NORMAL'
                    else:
                        mode = 'ABNORMAL'
            except httplib.CannotSendRequest:
                del conns[sname]
        sleep(10)

def unique(return_list):
    flag = True
    elem = return_list[0]
    for i in range(1,len(return_list)):
        if return_list[i] != elem:
            flag = False
            break
    return flag

def send(acc,amount,function):
    global conns
    global accounts_gettingused_array
    return_list = []
    while acc in accounts_gettingused_array or mode != 'NORMAL':
        sleep(5)
    accounts_gettingused_array.append(acc)
    for server in conns:
        try:
            return_list.append(conns[server].send(acc,amount,function))
        except httplib.CannotSendRequest:
            del conns[server]
    accounts_gettingused_array.remove(acc)
    if unique(return_list) and str(return_list[0]) != "False":
        return return_list[0]
    else:
        return False

def serverHello(sname,sip,pnum,msg = ''):
    global conns
    global mode
    try:
        if 'ALIVE' in msg:
            mode = 'RESYNCH'
            last_number = int(msg.split()[1])
            log_data = []
            for name in conns:
                if name != sname:
                    log_data.append(conns[name].get_logs(last_number))
            return log_data
        else:
            conns[sname] =  ServerProxy('http://'+str(sip)+":"+str(pnum))
            if len(conns) >= 1:
                mode = 'NORMAL'
            return 'DONE'
    except Exception as e:
        print 'error serverHello',e
        return 'FAILURE'

       
if __name__ == "__main__":
    global clients_array
    global mode
    global accounts_gettingused_array
    global conns

    clients_array = []
    servers = {}
    mode = 'NORMAL'
    accounts_gettingused_array = []
    conns = {}
    try:
        if len(argv) != 2:
            raise IndexError()
        pnum = int(argv[1])
    except IndexError:
        print "use: python server.py <pnum>"
        exit(0)
        
    try:    
        server = SimpleXMLRPCServer(
            ('', pnum),
            allow_none=True)
    except Exception as e:
        print e
        print "unable to create server"
        exit(0)

    thread = Thread(target=check_servers, args=())
    thread.daemon = True
    thread.start() 
    server.register_introspection_functions()
    server.register_function(clientHello)
    server.register_function(serverHello)
    server.register_function(resynch)
    server.register_function(send)
    server.serve_forever()