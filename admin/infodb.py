import sqlite3, getpass, hashlib, binascii, codecs, pandas, os

'''

The infodb program is designed to be an administrator focused application.

It's purpose is to import and export data mostly, but also to have
functions which can be used to check on the database integrity by
doing debug printing on users as well as printing out the entire
database if one so desires. Many of these functions will also be
copied over to the fcgi.py code for the limited cases where some of
these functions are needed to fetch information from the information
database and get dumped to the webapp in order to be used for the
gane itself.


Also described in this file is all of the info.db formatting,
as well as the CSV format to be used for imports and exports.

The idea behind imports - if a field is empty, the SQL database
is not touched for that one field. If a field is not empty, then
we will go ahead and replace that value in the SQL database.

If we encounter new users in the CSV, we will also add them.
New users are identified by a username which is not already in
use in the info.db database. This database and the auth.db
database are slightly different in this respect, someone can be
in here but not in auth.db


Database Structure:

username is the key

General Data:

username (key)      # string
real name           # string
3 top scores        # string OR 3 strings
cumulative score    # string

Student Specific:

Year                # string OR number
Major               # string

Faculty Specific:

Department          # string
Title               # string
Office Location     # string


CSV format:

username, real-name, top1, top2, top3, cumulative, year, major, department, title, office;


Functions:

general:
    printUser (username) - print out a single user
    printUserTable (username) - print out a single user, in a table friendly format
    printAll () - get confirmation if database larger than 10 people
    deleteUser (username) - delete user completely from database (for debugging generally)
import/export:
    importCSV (filename)
    exportCSV (filename)
getters:
    getUsernameList ()
    getRealName() (username)
    getTopScores (username)
    getCumulativeScore (username)
    getYear (username)
    getMajor (username)
    getDepartment (username)
    getTitle (username)
    getOfficeLocation (username)
    getFacultyOrStudent (username) return 'f' or 's', 'e' if error
setters:
    incrementCumulative (username, score)
    setHighScore (username, newScore) This will put the new score and bump out the lowest score
booleans:
    isStudent (username)
    isFaculty (username)

'''

### GLOBAL VARIABLES

# A list of all possible users
users = []

# Terminal size
rows, columns = os.popen('stty size', 'r').read().split()

# Database connection
conn = sqlite3.connect('../vars/info.db')
c = conn.cursor()

# username, real-name, top1, top2, top3, cumulative, year, major, department, title, office
c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, realname TEXT, top1 TEXT, top2 TEXT, top3 TEXT, cumulative TEXT, year TEXT, major TEXT, department TEXT, title TEXT, office TEXT)")

def printUser(username):

    if not username in users:
        print("{} is not a valid user.".format(username))
        return

    real = getRealName(username)
    topScores = getTopScores(username)
    cumulative = getCumulativeScore(username)

    typ = getFacultyOrStudent(username)
    if typ == 's': # print student
        year = getYear(username)
        major = getMajor(username)
        print("Username: {}\nReal Name: {}\nYear: {}\nMajor: {}\nTopScores: {}, {}, {}\nCumulative Score: {}".format(username, real, year, major, topScores[0], topScores[1], topScores[2], cumulative))

    elif typ == 'f': # print facutly
        department = getDepartment(username)
        title = getTitle(username)
        office = getOfficeLocation(username)
        print("Username: {}\nReal Name: {}\nTitle: {}\nDepartment: {}\nOffice Location: {}\nTopScores: {}, {}, {}\nCumulative Score: {}".format(username, real, title, department, office, topScores[0], topScores[1], topScores[2], cumulative))

    else:
        print ("Warning - This user is not determined to be a student or faculty member. Check the database")
        year = getYear(username)
        major = getMajor(username)
        department = getDepartment(username)
        title = getTitle(username)
        office = getOfficeLocation(username)
        print("Username: {}\nReal Name: {}\nYear: {}\nMajor: {}\nTitle: {}\nDepartment: {}\nOffice Location: {}\nTopScores: {}, {}, {}\nCumulative Score: {}".format(username, real, year, major, title, department, office, topScores[0], topScores[1], topScores[2], cumulative))

def printUserTable(username):

    if not username in users:
        print("{} is not a valid user.".format(username))
        return

    real = getRealName(username)
    topScores = getTopScores(username)
    cumulative = getCumulativeScore(username)

    typ = getFacultyOrStudent(username)
    if typ == 's':
        year = getYear(username)
        major = getMajor(username)

        print("Type: Student\nUsername: {}\nReal Name: {}\nYear: {}\nMajor: {}\nTopScores: {}, {}, {}\nCumulative Score: {}".format(username, real, year, major, topScores[0], topScores[1], topScores[2], cumulative))

    elif typ == 'f':
        department = getDepartment(username)
        title = getTitle(username)
        office = getOfficeLocation(username)

        print("Type: Faculty\nUsername: {}\nReal Name: {}\nTitle: {}\nDepartment: {}\nOffice Location: {}\nTopScores: {}, {}, {}\nCumulative Score: {}".format(username, real, title, department, office, topScores[0], topScores[1], topScores[2], cumulative))

    else:
        print ("Warning - This user is not determined to be a student or faculty member. Check the database")
        year = getYear(username)
        major = getMajor(username)
        department = getDepartment(username)
        title = getTitle(username)
        office = getOfficeLocation(username)

        print("Type: Unknown\nUsername: {}\nReal Name: {}\nYear: {}\nMajor: {}\nTitle: {}\nDepartment: {}\nOffice Location: {}\nTopScores: {}, {}, {}\nCumulative Score: {}".format(username, real, year, major, title, department, office, topScores[0], topScores[1], topScores[2], cumulative))

def printAll():
    getUsernameList()

    choice = input("This will print {} entries. Are you sure? (y/N): ".format(len(users)))

    if choice == 'y':
        for username in users:
            print("=" * int(columns))
            printUserTable(username)

def deleteUser(username):
    if username in users:
        c.execute("DELETE FROM users WHERE username = {}".format(quote_identifier(username)))
        conn.commit()
    else:
        print("Username {} does not exist.".format(username))

def importCSV(filename):
    actual = os.path.abspath(os.path.expanduser(filename))

    if not os.path.isfile(actual):
        print("File {} does not exist.".format(actual))
        return

    with open(actual) as csv:
        for line in csv: # line is the string of the csv
            try:
                if len(line) > 1: # this line is effectively empty. screw it.
                    if line[0] != '#':
                        # This line must not be a comment.
                        # Read the line of the CSV
                        # let's break up the CSV into the fields.
                        fields = line.split(",")

                        if len(fields) != 11:
                            flen = len(fields)
                            if flen > 11:
                                print("{} is too many fields: {}".format(flen, fields))
                            else:
                                print("{} is too few fields: {}".format(flen, fields))
                            break
                        # get all of the fields broken out
                        username = fields[0].strip()
                        realname = fields[1].strip()
                        if fields[2].strip() == "":
                            top1 = -1
                        else:
                            top1 = int(fields[2].strip())
                        if fields[3].strip() == "":
                            top2 = -1
                        else:
                            top2 = int(fields[3].strip())
                        if fields[4].strip() == "":
                            top3 = -1
                        else:
                            top3 = int(fields[4].strip())
                        if fields[5].strip() == "":
                            cumulative = -1
                        else:
                            cumulative = int(fields[5].strip())
                        if fields[6].strip() == "":
                            year = -1
                        else:
                            year = int(fields[6].strip())
                        major = fields[7].strip()
                        department = fields[8].strip()
                        title = fields[9].strip()
                        office = fields[10].strip()

                        # SQL Field namess
                        # username TEXT, realname TEXT, top1 TEXT, top2 TEXT, top3 TEXT, cumulative TEXT, year TEXT, major TEXT, department TEXT, title TEXT, office TEXT

                        getUsernameList()
                        if not username in users:
                            print("{} not in {}".format(username, users))
                            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (username, "", "", "", "", "", "", "", "", "", ""))
                            conn.commit()
                            print(username)
                        if realname != "":
                            c.execute("UPDATE users SET realname = '{}' WHERE username = '{}'".format(realname, username))
                        if fields[2].strip() != "":
                            c.execute("UPDATE users SET top1 = '{}' WHERE username = '{}'".format(top1, username))
                        if fields[3].strip() != "":
                            c.execute("UPDATE users SET top2 = '{}' WHERE username = '{}'".format(top2, username))
                        if fields[4].strip() != "":
                            c.execute("UPDATE users SET top3 = '{}' WHERE username = '{}'".format(top3, username))
                        if fields[5].strip() != "":
                            c.execute("UPDATE users SET cumulative = '{}' WHERE username = '{}'".format(cumulative, username))
                        if fields[6].strip() != "":
                            c.execute("UPDATE users SET year = '{}' WHERE username = '{}'".format(year, username))
                        if major != "":
                            c.execute("UPDATE users SET major = '{}' WHERE username = '{}'".format(major, username))
                        if department != "":
                            c.execute("UPDATE users SET department = '{}' WHERE username = '{}'".format(department, username))
                        if title != "":
                            c.execute("UPDATE users SET title = '{}' WHERE username = '{}'".format(title, username))
                        if office != "":
                            c.execute("UPDATE users SET office = '{}' WHERE username = '{}'".format(office, username))
                        conn.commit()
            except Exception as e:
                print("Error on line: {}\n{}".format(line, e))

    # c.execute("UPDATE users SET {} WHERE username = {}".format(field))

# CSV format:
#
# username, real-name, top1, top2, top3, cumulative, year, major, department, title, office;

# Todo: write my own CSV exporter which does not output random garble.
def exportCSV(filename):
    if filename == "":
        actual = os.path.abspath(os.path.expanduser("~/output.csv"))
    else:
        actual = os.path.abspath(os.path.expanduser(filename))
    table = pandas.read_sql('select * from users', conn)
    table.to_csv(actual, encoding='utf-8')
    print("File written to {}".format(actual))

# CSV format:
#
# username, real-name, top1, top2, top3, cumulative, year, major, department, title, office;

def getUsernameList():
    global users
    users = []
    c.execute("SELECT username FROM users")
    for entity in c.fetchall():
        users.append(entity[0])
    print("[::] Current Username List: {}".format(users))

def getRealName (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT realname FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getTopScores (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return (-1, -1, -1)
    c.execute("SELECT top1, top2, top3 FROM users WHERE username = '{}'".format(username))
    return list(c.fetchone())

def getCumulativeScore (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return -1
    c.execute("SELECT cumulative FROM users WHERE username = '{}'".format(username))
    try:
        return int(c.fetchone()[0])
    except:
        return -1

def getYear (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return -1
    c.execute("SELECT year FROM users WHERE username = '{}'".format(username))
    try:
        return int(c.fetchone()[0])
    except:
        return -1

def getMajor (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT major FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getDepartment (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT department FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getTitle (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT title FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getOfficeLocation (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT office FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

# This won't work until getYear() returns an int
def getFacultyOrStudent (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return 'e'
    year = getYear(username)
    major = getMajor(username)
    department = getDepartment(username)
    title = getTitle(username)

    if (year == -1) and (major == "") and (department != "") and (title != ""):
        return 'f'
    elif (year >= 0) and (major != "") and (department == "") and (title == ""):
        return 's'
    else:
        print ("Unable to determine if user {} is faculty or student.\nUsername: {} Year: {} Major: {} Department: {} Title: {}".format(username, username, year, major, department, title))
        return 'e'

def incrementCumulative (username, score): # score must be int
    if not username in users:
        print("{} is not a valid user.".format(username))
        return
    c.execute("SELECT cumulative FROM users WHERE username = '{}'".format(username))
    old_cum = c.fetchone()[0]
    try:
        new_cum = score + int(old_cum)
    except:
        new_cum = score
    c.execute("UPDATE users SET cumulative = {} WHERE username = '{}'".format(str(new_cum), username))
    conn.commit()

def setHighScore (username, highScore): # highScore must be int
    if not username in users:
        print("{} is not a valid user.".format(username))
        return
    s1, s2, s3 = getTopScores(username)
    if highScore > s3:
        c.execute("UPDATE users SET top3 = {} WHERE username = '{}'".format(highScore, username))
        c.execute("UPDATE users SET top2 = {} and top1 = {} WHERE username = '{}'".format(s3, s2, username)) # shift scores down
    elif highScore > s2:
        c.execute("UPDATE users SET top2 = {} WHERE username = '{}'".format(highScore, username))
        c.execute("UPDATE users SET top1 = {} WHERE username = '{}'".format(s2, username)) # shift scores down
    elif highScore > s1:
        c.execute("UPDATE users SET top1 = {} WHERE username = '{}'".format(highScore, username))
    conn.commit()

# This will not work until getYear() returns ints
def isStudent (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return False
    if getFacultyOrStudent(username) == 's':
        return True
    else:
        return False

# This will not work until getYear() returns ints
def isFaculty (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return False
    if getFacultyOrStudent(username) == 'f':
        return True
    else:
        return False

# ------------------------------------------------------------------------------

# Thank you stack-overflow: https://stackoverflow.com/a/6701665
def quote_identifier(s, errors="strict"):
    encodable = s.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    return "\"" + encodable.replace("\"", "\"\"") + "\""

# ------------------------------------------------------------------------------

#    MAIN CODE BEGINS HERE

# Protip:   You can open this file using 'python3 -i infodb.py', and if you
#           press 'q' at the prompt, you can just outright make function
#           calls wherever you would like to, to test the code in this file.

# ------------------------------------------------------------------------------

while 1:
    choice = input("i - import\ne - export\nl - list\np - print\nr - delete\nd - dump\nq - quit\nChoice: ")
    if "i" in choice:
        f = input("Import Filename: ")
        importCSV(f)

    elif "e" in choice:
        f = input("Export Filename: ")
        exportCSV(f)

    elif "p" in choice:
        u = input("Username: ")
        printUser(u)

    elif "l" in choice:
        getUsernameList()

    elif "r" in choice:
        u = input("Username to delete: ")
        deleteUser(u)

    elif "d" in choice:
        printAll()

    elif "q" in choice:
        # quit
        exit(0)
    else:
        # ???
        print("{} is not a valid commnad. Please try again.")
