#!/usr/bin/python


from __future__ import print_function
import optparse
import os
import sys

lmfile = ""
fullpass = []
partialpass = []

# Get Options
parser = optparse.OptionParser()

parser.add_option('-u', '--users',
                  dest="listusers",
                  default=False,
                  action="store_true",
                  help='List usernames without passwords',
                 )
parser.set_usage("""Usage: ./parselm.py <file>

This program takes string output from John the Ripper and
concatenates LM hashes. John output file should look like:

MYPASSW          (User1:1)
ORD123           (User1:2)
SHORT            (User2)
PARTIAL          (User3:1)
""")
options, remainder = parser.parse_args()
listusers = options.listusers

if len(remainder) == 1:
    lmfile = remainder[0]
else:
    print("Usage: ./parselm.py <file>")
    sys.exit()

if not os.path.isfile(lmfile):
    print("[!] Error: could not find file '%s'" % lmfile)
    sys.exit()

def parseFile(file):
    userlist = []
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
                userlist.append([passnum, passpart, user])
    return userlist

userlist = parseFile(lmfile)
for i in userlist:
    # full password (<= 7 chars)
    if i[0] == "0":
        fullpass.append([i[1], i[2]])
        userlist.remove(i)
    # first half of partial password (> 7 chars)
    elif i[0] == "1":
        for j in userlist:
            if j[0] == "2" and j[2] == i[2]:
                fullpass.append([i[1] + j[1], i[2]])
                userlist.remove(i)
                userlist.remove(j)

if listusers:
    for item in userlist:
        print(item[2])
else:
    print("""
FULL PASSWORDS:

Password       Username
---------------------------------""")

    for passuser in fullpass:
        print('{:<15}'.format(passuser[0]), end='')
        print(passuser[1])


    print("""

PARTIAL PASSWORDS:

Password       Username
---------------------------------""")
    for item in userlist:
        if item[0] == "1":
            print('{:<15}'.format(item[1]), end='')
            print(item[2])
        elif item[0] == "2":
            print('{:<15}'.format("*******" + item[1]), end='')
            print(item[2])

