# parselm
Parse and finish cracking LM passwords from JTR output

# Description
Since LM passwords are broken up into two 7-character sections, it can be annoying to piece together passwords from a medium to large-size LM hash dump. This script parses John the Ripper output and concatenates cracked LM passwords.

If you have an accompanying NT hash file, you can also finish cracking your "cracked" LM passwords. Since LM stores passwords in all caps, a cracked LM password may look like "MYPASSWORD123" while the user actually inputs something like "MyPassword123".  If you provide an accompanying NT hash file, the script will look for any matching users, create a small custom wordlist, and finish cracking any passwords it can find.

# Help Menu
```
parselm.py -h
Usage: ./parselm.py <file>

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


Options:
  -h, --help            show this help message and exit
  -u, --users           List usernames without passwords
  -f, --full            List full LM passwords
  -p, --partial         List partial LM passwords
  -c NTFILE, --crack=NTFILE
                        To finish cracking, enter NT hash file
  -d, --debug           Show verbose debug info
```
