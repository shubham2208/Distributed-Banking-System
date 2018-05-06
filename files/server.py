from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import httplib
from xmlrpclib import ServerProxy
from sys import argv
from socket import gethostname
import socket
import traceback
import threading

def write(operation_num,acc,amount,f):
    f.write(str(operation_num)+" "+str(acc)+" "+str(amount)+"\n")
    f.flush()

def send(acc,amount,function):
    global accounts_dict
    global f
    global operation_num
    if function == 'credit':
        try:
            if accounts_dict.keys().count(acc) == 0:
                accounts_dict[acc] = 0
            accounts_dict[acc] += int(amount)
            write(operation_num,acc,amount,f)
            operation_num += 1
            return accounts_dict[acc]
        except Exception as e:
            print 'error crediting',e
            return False

    elif function == 'debit':
        try:
            if accounts_dict.keys().count(acc) == 0:
                accounts_dict[acc] = 0
            accounts_dict[acc] -= int(amount)
            amount = accounts_dict[acc]
            write(operation_num,acc,amount,f)
            operation_num += 1
            return accounts_dict[acc]
        except Exception as e:
            print 'error debiting',e
            return False

    elif function == 'inquire':
        try:
            if accounts_dict.keys().count(acc) == 0:
                accounts_dict[acc] = 0
            amount = accounts_dict[acc]
            write(operation_num,acc,amount,f)
            operation_num += 1
            return accounts_dict[acc]
        except Exception as e:
            print 'error inquiring',e
            return False

def resynch(other_server_data):
    global coordinator_conn
    global serverName
    global operation_num
    flag = True
    f.seek(-1,2)
    try:
        if len(other_server_data) == 0:
            return 'RESYNCH-DONE'
        for i in range(len(other_server_data[0])):
            flag = True
            elem = other_server_data[0][i]
            for j in range(len(other_server_data)):
                if other_server_data[j][i] != elem:
                    flag = False
            if flag:
                f.write(" ".join(other_server_data[0][i])+"\n")
                f.flush()
                op_id,acc,amount = other_server_data[0][i]
                accounts_dict[acc] = int(amount)
                operation_num += 1
            else:
                flag = False

        if flag:
            return 'RESYNCH-DONE'
        else:
            return False
    except Exception as e:
            print 'error resynching',e

def get_logs(op_id):
    print 'called for',op_id
    global log_name
    temp_log_handler = open(log_name,'r')
    log_tuples = []
    for log in temp_log_handler.read().split("\n"):
        if log != "":
            log_tuples.append(log.split())
    return log_tuples[(op_id-1):]

def ping():
    return True

if __name__ == "__main__":
    global f
    global accounts_dict
    global operation_num
    global serverName
    global serverIp
    global coordinator_conn
    global log_name

    
    try:
        if len(argv) < 5:
            raise IndexError()
        connection = argv[1]
        port_num = int(argv[2])
        serverName = argv[3]
        log_name = argv[4]
        alive = ''
        if len(argv) > 5:
            alive = 'ALIVE'
    except:
        print "use: python server.py <coordinator_ip:port_num> <server_port_num> <serverName> <log_name> <alive(optional)>"
        exit()

    while True:
        operation_num = 1
        accounts_dict = {}
        
        try:
            f = open(log_name,'r+')
            for lines in f.read().split("\n"):
                if len(lines.split(" ")) == 3:
                    op_id,acc,amount = lines.split(" ")
                    accounts_dict[acc] = int(amount)
                    operation_num += 1
            f.seek(0,2)
        except:
            print 'unable to use log file create file and try again'
            exit(0)


        try:
            coordinator_conn = ServerProxy('http://'+connection)
            if alive == 'ALIVE':
                alive += " " + str(operation_num)
            serverIp = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
            result = coordinator_conn.serverHello(serverName,serverIp,port_num,alive)
            if 'ALIVE' in alive:
                if not resynch(result):
                    raise Exception('Error resynching')
                else:
                    coordinator_conn.resynch(serverName,serverIp,port_num)
                    alive = ''
        except Exception as e:
            print e
            print 'unable to connect to coordinator_conn'
            exit(0)

        try:    
            server = SimpleXMLRPCServer(
                ('', port_num),
                allow_none=True)
            server.register_introspection_functions()
            server.register_function(send)
            server.register_function(resynch)
            server.register_function(get_logs)
            server.register_function(ping)
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
            alive = 'ALIVE'
        except Exception as e:
            print e
            exit(0)