#!/usr/bin/python


from __future__ import print_function
import optparse
import os
import sys
import itertools
import subprocess
from glob import glob

lmfile = ""
fullpass = []
partialpass = []
potfile = os.path.expanduser('~/.john/john.pot')

# Get Options
parser = optparse.OptionParser()

parser.add_option('-u', '--users',
                  dest="listusers",
                  default=False,
                  action="store_true",
                  help='List usernames without passwords',
                 )
parser.add_option('-f', '--full',
                  dest="listfull",
                  default=False,
                  action="store_true",
                  help='List full LM passwords',
                 )
parser.add_option('-p', '--partial',
                  dest="listpartial",
                  default=False,
                  action="store_true",
                  help='List partial LM passwords',
                 )
parser.add_option('-c', '--crack',
                  dest="ntfile",
                  default='',
                  help='To finish cracking, enter NT hash file',
                 )
parser.add_option('-d', '--debug',
                  dest="debug",
                  default=False,
                  action="store_true",
                  help='Show verbose debug info',
                 )
parser.set_usage("""Usage: ./parselm.py <file>

This script takes string output from John the Ripper and parses LM hashes.
Automatically concatenate LM passwords with the -f option. If you have an
accompanying NT hash file, you can finish cracking LM hashes by providing
the NT file via the -c option.

Examples:
./parselm.py LM.out -f
./parselm.py LM.out -c NT.out

John output file should look like:

MYPASSW          (User1:1)
ORD123           (User1:2)
SHORT            (User2)
PARTIAL          (User3:1)
""")
options, remainder = parser.parse_args()
listusers = options.listusers
listfull = options.listfull
listpartial = options.listpartial
ntfile = options.ntfile
debug = options.debug

if len(remainder) == 1:
    lmfile = remainder[0]
else:
    print("Usage: ./parselm.py <file>")
    sys.exit()

if not os.path.isfile(lmfile):
    print("[!] Error: could not find file '%s'" % lmfile)
    sys.exit()

def parseLMFile(file):
    lmlist = []
    with open(file) as f:
        for line in f:
            if "(" in line and ")" in line:
                passpart = line.split(" ")[0]
                if ":" in line:
                    passnum = line[line.find(":")+1:line.find(")")]
                    user = line[line.find("(")+1:line.find(":")]
                else:
                    passnum = "0"
                    user = line[line.find("(")+1:line.find(")")]
                lmlist.append([passnum, passpart, user])
    return lmlist

def createUserlist(lmlist):
    userlist = []
    for line in lmlist:
        if line[2] not in userlist:
            userlist.append(line[2])
    return userlist

def listUsers():
    print("""Users:
""")
    for user in userlist:
        print(user)
    print("\n")

def listFull():
    print("""Full Passwords:
""")
    for passuser in fullpass:
        print("%s:%s" % (passuser[1], passuser[0]))
    print("\n")

def listPart():
    print("""Partial Passwords:

Password       Username
---------------------------------""")
    for item in lmlist:
        if item[0] == "1":
            print('{:<15}'.format(item[1]), end='')
            print(item[2])
        elif item[0] == "2":
            print('{:<15}'.format("-------" + item[1]), end='')
            print(item[2])

def createWordlist(seed):
    newlist = []
    wordlist = []
    alpha = "abcdefghijklmnopqrstuvwxyz"
    for char in seed:
        if char.lower() in alpha:
            newlist.append(char.lower()+char.upper())
        else:
            newlist.append(char)
    wordlist = map(''.join, itertools.product(*((list(c)) for c in newlist)))
    return wordlist

def parseNTFile(ntfile):
    hashlist = []
    with open(ntfile) as f:
        for line in f:
            # check if there are 4 colons in the line (JTR format NT hashes)
            if line.count(':') == 4:
                username = line.split(':')[0]
                hashlist.append([username, line])
    if debug: print("[-] %s NT hashes loaded" % len(hashlist))
    return hashlist

def crackNT(lmfullpass, lmpartpass, nthashlist):
    ntlmhashes = []
    for i in lmfullpass:
        for j in nthashlist:
            # if LMuser matches NTuser
            if i[1] == j[0]:
                # append (username, LMpass, NThash)
                ntlmhashes.append([i[1], i[0], j[1]])
    if debug: print("[-] %s full LM passwords found with matching users in NT file" % len(ntlmhashes))
    try:
        proc = subprocess.Popen('mkdir cracktemp'.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.communicate()[0].split("\n")[0]
        if debug: print("[-] Created temp directory at ./cracktemp")
    except:
        print("[!] failed to create 'cracktemp' directory")
        if debug: raise
        sys.exit()
    for item in ntlmhashes:
        if debug: print('[-] Cracking %s for user %s' % (item[2].split(':')[1], item[0]))
        crackedpass = ""
        # if the NT hash has already been cracked by john, use that password
        if os.path.isfile(potfile) and item[2].split(':')[1] in open(potfile).read():
            if debug: print('[-] Cracked hash "%s" found in john.pot file' % item[2].split(':')[1])
            with open(potfile, 'rU') as f:
                for line in f:
                    if item[2].split(':')[1] in line:
                        crackedpass = line.split(':')[1].split('\n')[0]
        else:
            wordlist = createWordlist(item[1])
            wordlistfile = 'cracktemp/wordlist-%s' % item[0]
            singlehashfile = 'cracktemp/hash-%s' % item[0]
            # write wordlist to a temp file
            with open(wordlistfile, 'a') as f:
                for word in wordlist: f.write(word+'\n')
            with open(singlehashfile, 'a') as f:
                f.write(item[2])
            if debug: print("[-] Created wordlist with %s words for user '%s' from seed '%s'" % (len(wordlist), item[0], item[1]))
            try:
                proc = subprocess.Popen(('john --format=NT --wordlist=%s %s' % (wordlistfile, singlehashfile)).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                johnout = proc.communicate()[0]
                for line in johnout.split('\n'):
                    if item[0] in line:
                        crackedpass = line.split(" ")[0]
            except:
                print("[!] failed to run john command")
                if debug: raise
                sys.exit()
            os.remove(wordlistfile)
            os.remove(singlehashfile)
        print("%s:%s" % (item[0], crackedpass))
    os.rmdir('cracktemp')
    if debug: print("[-] Deleted temp directory at ./cracktemp")

lmlist = parseLMFile(lmfile)
userlist = createUserlist(lmlist)
for i in lmlist:
    # full password (<= 7 chars)
    if i[0] == "0":
        # append (password, user) to fullpass
        fullpass.append([i[1], i[2]])
        lmlist.remove(i)
    # first half of partial password (> 7 chars)
    elif i[0] == "1":
        for j in lmlist:
            if j[0] == "2" and j[2] == i[2]:
                # append (passpart1 + passpart2, username) to fullpass
                fullpass.append([i[1] + j[1], i[2]])
                lmlist.remove(i)
                lmlist.remove(j)

if listusers: listUsers()

if listfull: listFull()

if listpartial: listPart()

if not ntfile == '':
    if os.path.isfile(ntfile):
        ntlist = parseNTFile(ntfile)
        crackNT(fullpass, lmlist, ntlist)
    else:
        print("[!] Error: could not find NT hash file '%s'" % ntfile)
        sys.exit()

if not listusers and not listfull and not listpartial and ntfile == '':
    print("%s\tTotal users" % len(userlist))
    print("%s\tFull LM passwords" % len(fullpass))
    print("%s\tPartial LM passwords" % len(lmlist))









