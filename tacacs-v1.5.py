#!/usr/bin/python
import readline
import logging
import os
import subprocess
import sys
import getpass
import pickle
import crypt
import string
from termcolor import colored

LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    )

# whole_xc_structure = []
# whole_xc_structure.append(xc_service_structure)
# pickle.dump(whole_xc_structure, open(filename.replace(".conf","-xc.pcl"), "wb" ) )
version = "tacacs management console version 0.9 Atanas Yankov (c)"
use = "Only for r00t cr3w Internal Use"
print colored(version,'yellow')
#print(figlet_format("Xnet focker ",font="bulbhead"))
tmpl_admin = open( '/home/google/admin.conf' )
tmpl_user = open( '/home/google/user.conf' )
src_admin = string.Template( tmpl_admin.read() )
src_user = string.Template( tmpl_user.read() )
ntt_account_list = []
new_account_list = []
ntt_account_dict = {
           'account_id' : "",
           'account_username' : "",
           'account_password' : "",
           'account_rights' : "",
           'account_exipire' : "",
     }


try:
    if not os.path.exists("/home/google/ntt_accounts.pickle"):
        ntt_accounts_store = open("/home/google/ntt_accounts.pickle", "wb")
    else:
        try:
            ntt_accounts_store = open("/home/google/ntt_accounts.pickle", "rb")
            ntt_account_list = pickle.load(ntt_accounts_store)
        except ValueError:
            print ( " file exist but its empty" )

except ValueError:
    print("Cannot load account file")

class SimpleCompleter(object):
    
    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s 
                                for s in self.options
                                if s and s.startswith(text)]
                logging.debug('%s matches: %s', repr(text), self.matches)
            else:
                self.matches = self.options[:]
                logging.debug('(empty input) matches: %s', self.matches)
        
        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug('tac>(%s, %s) => %s', 
                      repr(text), state, repr(response))
        return response


def find_user(check_user,check_list):

     try:
         for i in range(len(check_list)):
             if check_list[i]['account_username'] == check_user:
                return 1
         return 0
     except ValueError:
         print("Failed to find user.")                     


def add_user():
 

     current_account_dict = {} 
     # Ask for the input
     addedname = raw_input("Enter Username>")   
     if ( addedname == "xdsgrrr" or addedname == "root" or addedname == "google"):
        print("Please use another user")
        return 0 
     print("Adding " + addedname )  
     acctrights = raw_input("rw or ro>")   
     print("Activate " + acctrights )  
     if ( acctrights == "ro"):
         right = "user" 
     elif ( acctrights == "rw"):
         right = "admin" 
     else:
         right = "user" 
     # Asking for users password
     match = False
     while not match:
        print("Enter Password") 
        password = getpass.getpass()
        print("Enter Password again") 
        second_pass = getpass.getpass()
        if password != second_pass:
           match = False
        else:
           match = True
         
     try:
         if not find_user(addedname,ntt_account_list):
             current_account_dict["account_username"] = addedname 
             current_account_dict["account_password"] = password 
             current_account_dict["account_rights"] = right 
             current_account_dict["account_state"] = "new" 
             return current_account_dict
         else:
             print("User Already exist please use another name or action")
             return None 
     except ValueError:
         print("Failed to add user.")                     

def del_user():
  
     current_account_dict = {} 
     # Ask for the input
     deletedname = raw_input("Enter Username ")   
     print("Removing " + deletedname )  
     if ( deletedname == "xdsgrrr" or deletedname == "root" or deletedname == "google"):
        print("Please select another user")
        return 0 
     # Asking for users password
     try:
         #os.system("userdel -r " + deletedname)
         #ntt_account_list.remove(current_account_dict[deletedname]) 
         for ntt_user in ntt_account_list:
             if ntt_user['account_username'] == deletedname:
                ntt_user["account_state"] = "deleted"
                break 
     except ValueError:
         print("Failed to delete user.")                     

def chg_user_pass():

     # Ask for the input
     changename = raw_input("Enter Username >")
     print("changing " + changename )
     changepass = raw_input("Enter New Password >")
     if ( changename == "xdsgrrr" or changename == "root"):
        print("Please select another user")
        return 0
     # Asking for users password
     try:
         for ntt_user in ntt_account_list:
             if ntt_user['account_username'] == changename:
                ntt_user["account_state"] = "updated"
                ntt_user["account_password"] = changepass
                break
     except ValueError:
         print("Failed to update user password.")

def sync_user():

    try:
        print colored("Syncing with remote","yellow")
        os.system("/usr/bin/rsync -qavz --exclude=\".*\" /home/google/  google@10.240.36.5:/home/google/candidate/") 
        os.system("ssh google@10.240.36.5 \"sudo cp /home/google/candidate/tac_plus.conf /etc/tacacs+/tac_plus.conf\"")
        os.system("ssh google@10.240.36.5 \"sudo cp /home/google/candidate/ntt_accounts.pickle /home/google/\"")
        for ntt_user in ntt_account_list:
           if ( ntt_user['account_username'] != "root" or ntt_user['account_username'] != "xdsgrrr" or ntt_user['account_username'] != "google" ):  
               if ntt_user["account_rights"] is not None and ntt_user["account_rights"] == "admin":
                   os.system("sudo /usr/bin/rsync -qavz /home/" + ntt_user['account_username'] + "/.google_authenticator google@10.240.36.5:/home/google/candidate/" +  ntt_user['account_username'] + "/") 
                   os.system(" ssh google@10.240.36.5 \"sudo cp /home/google/candidate/" + ntt_user['account_username'] + "/.google_authenticator /home/"+ ntt_user['account_username'] + "/ \"")
                   os.system(" ssh google@10.240.36.5 \"sudo chown " + ntt_user['account_username'] + ":" + ntt_user['account_username'] +   " /home/" + ntt_user['account_username'] + "/.google_authenticator\"")
                   if ntt_user["account_state"] == "old":
                       chgPass = crypt.crypt(ntt_user["account_password"],"22")
                       os.system("ssh google@10.240.36.5 \"sudo usermod --password " + chgPass + " " + ntt_user["account_username"]+ "\"")

    except ValueError:
        print("Failed to sync users")

def peer_reload():

    try:
        print colored("Peer reload","yellow")
        os.system("ssh google@10.240.36.5 \"sudo systemctl restart tacacs_plus\"")
    except ValueError:
        print("Failed to reload peer service")

def peer_status():

    try:
        print("Peer status")
        os.system("ssh google@10.240.36.5 \"sudo systemctl status tacacs_plus\"")
    except ValueError:
        print("Failed to reload peer service")

def list_user():

    try:
       for ntt_user in ntt_account_list:
          print colored("Username ","red"),colored(ntt_user["account_username"] + " {","yellow")
          print colored("         ","grey"),colored("account state     :","grey"),colored(ntt_user["account_state"],"yellow")
          print colored("         ","grey"),colored("account password  :","grey"),colored(ntt_user["account_password"],"yellow")
          print colored("         ","grey"),colored("account permition :","grey"),colored(ntt_user["account_rights"],"yellow")
          print colored("         ","grey"),colored("} ","yellow")
    except ValueError:
         print("Failed to list users.")                     


def commit_user():
    changed=0
    current=0
    try:
       for ntt_user in ntt_account_list:
          if ntt_user["account_state"] is not None and ntt_user["account_state"] == "updated":
             chgPass = crypt.crypt(ntt_user["account_password"],"22")
             os.system("sudo usermod --password " + chgPass + " " + ntt_user["account_username"])
             print("usermod --password " + chgPass + " " + ntt_user["account_username"])
             ntt_user["account_state"] = "old"
          if ntt_user["account_state"] is not None and ntt_user["account_state"] == "new":
             print ("commiting  "+  ntt_user["account_username"])
             encPass = crypt.crypt(ntt_user["account_password"],"22")
             print ("useradd -p "+encPass+ " -s "+ "/bin/false "+ "-d "+ "/home/" + ntt_user["account_username"]+ " -m "+ " -c \""+ ntt_user["account_username"]+"\" " + ntt_user["account_username"])
             os.system("sudo useradd -p "+encPass+ " -s "+ "/bin/false "+ "-d "+ "/home/" + ntt_user["account_username"]+ " -m "+ " -c \""+ ntt_user["account_username"]+"\" " + ntt_user["account_username"])
             os.system(" ssh google@10.240.36.5 \"sudo useradd -p " + encPass + " -s "+ "/bin/false "+ "-d "+ "/home/" + ntt_user["account_username"]+ " -m "+ " -c \""+ ntt_user["account_username"]+"\" " + ntt_user["account_username"] + "\"")
             if ntt_user["account_rights"] == "admin":
                 print("sudo -i -u " + ntt_user["account_username"] +" google-authenticator -t -r 3 -R 60 -d -w 15")
                 os.system("sudo usermod --shell /bin/bash " +  ntt_user["account_username"] ) 
                 os.system("sudo -i -u " + ntt_user["account_username"] +" google-authenticator -t -r 3 -R 60 -d -w 15")
                 os.system("sudo usermod --shell /bin/false " +  ntt_user["account_username"] ) 
             ntt_user["account_state"] = "old"
             changed +=1
          if ntt_user["account_state"] is not None and ntt_user["account_state"] == "deleted":
             del ntt_account_list[current]
             os.system("sudo userdel -r " + ntt_user["account_username"])
             os.system("ssh google@10.240.36.5 \"sudo userdel -r " + ntt_user["account_username"]+ "\"")
             changed +=1
          current += 1
    except ValueError:
         print("Failed to commit users.")                     
    if os.path.exists("/home/google/tac_conf_ntt"):
       fileout = open( '/home/google/tac_conf_ntt', 'w' )
       fileout.close()
    if changed == 0:
       print("nothing to commit")
       for ntt_user in ntt_account_list:
          d={ 'account_username': ntt_user["account_username"] }
          c={ 'account_username': ntt_user["account_username"], 'account_des': crypt.crypt(ntt_user["account_password"],"33") }
          if ntt_user["account_rights"] == "admin":
              result_head = src_admin.substitute(d)
          else:
              result_head = src_user.substitute(c)
          fileout = open( '/home/google/tac_conf_ntt', 'a' )
          fileout.write(result_head)
          fileout.close()
    else:
        for ntt_user in ntt_account_list:
           d={ 'account_username': ntt_user["account_username"] }
           c={ 'account_username': ntt_user["account_username"], 'account_des': crypt.crypt(ntt_user["account_password"],"33") }
           if ntt_user["account_rights"] == "admin":
               result_head = src_admin.substitute(d)
           else:
               result_head = src_user.substitute(c)
           fileout = open( '/home/google/tac_conf_ntt', 'a' )
           fileout.write(result_head)
           fileout.close()
    #tac_plus.conf
    if os.path.exists("/home/google/tac_conf_ntt") and os.path.exists("/home/google/tac_plus.head"):
        tacplus_conf = open("/home/google/tac_plus.conf", 'w')
        tacplus_header = open("/home/google/tac_plus.head", 'r')
        tacplus_ntt = open("/home/google/tac_conf_ntt", 'r')
        tacplus_conf.write(tacplus_header.read())
        tacplus_conf.write(tacplus_ntt.read())
        tacplus_conf.close()
        tacplus_header.close()
        tacplus_ntt.close()
        os.system("sudo cp /home/google/tac_plus.conf /etc/tacacs+/tac_plus.conf")
def input_loop():
    line = ''
    while line != 'quit':
        line = raw_input('gtacli>')
        print colored('cmd %s' % line,'red')
        #print colored(version,'yellow')
        if line == "adduser":
            ntt_account_dict = add_user() 
            if ntt_account_dict is not None:
                ntt_account_list.append(ntt_account_dict)
        if line == "deluser":
            del_user()
        if line == "version":
            print colored("Version  :",'red'), colored(version,'yellow')
        if line == "chgpass":
            chg_user_pass()
        if line == "listuser":
           list_user()
        if line == "sync":
           sync_user()
        if line == "peerreload":
           peer_reload()
        if line == "peerstatus":
           peer_status()
        if line == "reload":
           os.system("sudo systemctl restart tacacs_plus")
        if line == "status":
           os.system("sudo systemctl status tacacs_plus")
        if line == "saveuser":
           try:
              ntt_accounts_store = open("/home/google/ntt_accounts.pickle", "wb")
              pickle.dump(ntt_account_list, ntt_accounts_store)
              ntt_accounts_store.close()
           except ValueError:
              print("Failed to save users.")
        if line == "commit":
           print 'commit changes'
           try:
              commit_user()
              ntt_accounts_store = open("/home/google/ntt_accounts.pickle", "wb")
              pickle.dump(ntt_account_list, ntt_accounts_store)
              ntt_accounts_store.close()
           except ValueError:
              print("Failed to commit users")
# Register our completer function
# Register our completer function
readline.set_completer(SimpleCompleter(['adduser', 'deluser', 'chgpass','listuser','saveuser','version','reload','status','commit','sync','peerreload','peerstatus', 'quit']).complete)

# Use the tab key for completion
readline.parse_and_bind('tab: complete')

# Prompt the user for text
input_loop()

