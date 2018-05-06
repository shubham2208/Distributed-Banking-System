from xmlrpclib import ServerProxy
import httplib
import sys

if __name__ == '__main__':
    try:
        if len(sys.argv) > 2:
            conn = sys.argv[1]
            name = sys.argv[2]
            coordinator = ServerProxy('http://'+conn)
            if not coordinator.clientHello(name):
                print 'Cant connect to coordinator'
            flag = True
            while flag:
                print 'what do you want to do [d:deposit w:withdraw c:balance check q:quit ?'
                res = raw_input()
                actions = {'d':'deposit','w':'withdraw','c':'inquire','q':'quit'}
                if res in actions:
                    if res == 'q':
                        sys.exit(0)
                    acc = raw_input('Account to check\n')
                    action = actions[res]
                    if action == 'deposit':
                        amount = raw_input('\nAmount for acc #%s\n'%acc)
                        if amount <= 0:
                            print("amount should be > 0")
                        elif str(coordinator.send(acc, amount,'credit')) != "False":
                            print("Added %s to account %s"%(amount, acc))
                        else:
                            print("Account not found, %s"%(acc))

                    if action == 'withdraw':
                        amount = raw_input('\nAmount for acc #%s\n'%acc)
                        if amount <= 0:
                            print("amount should be > 0")
                        elif str(coordinator.send(acc, amount,'debit')) != "False":
                            print("Removed %s from account %s"%(amount,acc))
                        else:
                            print("Account not found, %s"%(acc))

                    if action == 'inquire':
                        amount = coordinator.send(acc,0,'inquire')
                        if str(amount) != "False":
                            print("Account #%s has %s"%(acc, amount))
                        else:
                            print("Account not found, %s"%(acc))
                else:
                    print 'Invalid Option'
    except Exception as e:
        print 'error in main',e
        print 'Error'      
