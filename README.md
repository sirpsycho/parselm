# parselm
Parse LM passwords from JTR output

# Description
Since LM passwords are broken up into two 7-character sections, it can be annoying to piece together passwords from a medium to large-size LM hash dump. This script parses John the Ripper output and concatenates cracked LM passwords.

```
./parselm.py -h
Usage: ./parselm.py <file>

This program takes string output from John the Ripper and
concatenates LM hashes. John output file should look like:

MYPASSW          (User1:1)
ORD123           (User1:2)
SHORT            (User2)
PARTIAL          (User3:1)


Options:
  -h, --help   show this help message and exit
  -u, --users  List usernames without passwords
```
