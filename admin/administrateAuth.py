import sqlite3, getpass, hashlib, binascii, codecs

conn = sqlite3.connect('../vars/auth.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user TEXT, passhash TEXT)")

'''
  Kristina
'''
def userExists(username):
    # this function needs to take a username and check to see if the username exists. If so, return true. Otherwise, return false
    c.execute("SELECT * FROM users WHERE user={}".format(quote_identifier(username)))
    try:
        if username == c.fetchone()[0]:
            return True
        return False
    except:
        return False

def addUser(username, password):
    # this function needs to add a username and password to the database
    passhash = hashPassword(password)
    print("username: {} password: {} hash: {}".format(username, password, passhash))
    c.execute("INSERT INTO users VALUES (?, ?)", (username, passhash))
    conn.commit()

def deleteUser(username):
    # this function deletes a row with a username and the corresponding hash. The username will always be validated by userExists
    if userExists(username):
        c.execute("DELETE FROM users WHERE user={}".format(quote_identifier(username)))
        conn.commit()

def showUser(username):
    # this function prints the username and password hash for all users who's name is "like" the username.
    c.execute("SELECT * FROM users WHERE user={}".format(quote_identifier(username)))
    var = c.fetchone()
    print("Username: {} Passhash: {}".format(var[0], var[1]))

def changePassword(username):
    pswd = getpass.getpass("Enter your password: ")
    pswd2 = getpass.getpass("Confirm your password: ")
    if pswd == pswd2:
        deleteUser(username) # make sure to clear the username that may be there. This also works when creating accounts
        print(pswd)
        addUser(username, pswd) # add the user back and their new password
    else:
        print("The passwords do not match! Try again")
        changePassword(username)

def checkPassword(username):
    pswd = getpass.getpass("Enter your password: ")
    userhash = hashPassword(pswd)
    # this function takes the password from the database and compares it to the hash from the user entry
    c.execute("SELECT * FROM users WHERE user={}".format(quote_identifier(username)))
    passhash = c.fetchone()[1]
    if passhash == userhash:
        print("Passwords are the same!")
    else:
        print("Passwords are not the same!")

def printAll():
    longest = 0
    for row in c.execute('SELECT * FROM users'):
        if len(row[0]) > longest:
            longest = len(row[0])

    print()
    print(("| {:" + str(longest) + "s} | {:64s} |").format("Name", "Password Hash"))
    print(("|-{:" + str(longest) + "s}-|-{:64s}-|").format("-" * longest,"-" * 64))

    for row in c.execute('SELECT * FROM users'):
        print(("| {:" + str(longest) + "s} | {} |").format(row[0], row[1].decode('utf-8')))
    print()

def hashPassword(password):
    return binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'assault', 100000))

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

while 1:
    choice = input("a - add user\nd - delete user\ns - show user entry\nc - change password\nv - check (validate) password for user\np - print database\nq - quit\nChoice: ")
    if "a" in choice:
        # add user
        username = input("Enter new username: ")
        if not userExists(username):
            if username != "":
                changePassword(username)
                print("Created user {}".format(username))
            else:
                print("Username cannot be empty")
        else:
            print("User exits")

    elif "d" in choice:
        # delete user
        username = input("Enter username to delete: ")
        if userExists(username):
            deleteUser(username)
            print("Deleted user {}".format(username))
        else:
            print("User {} does not exist".format(username))

    elif "s" in choice:
        # show user info
        username = input("Enter username: ")
        if userExists(username):
            showUser(username)
        else:
            print("User {} does not exist".format(username))

    elif "c" in choice:
        # change passwod
        username = input("Enter username for password change: ")
        if userExists(username):
            # query for password
            changePassword(username)
            print("Password chaged for {}".format(username))
        else:
            print("User {} does not exist".format(username))

    elif "v" in choice:
        # check password against database
        username = input("Enter username: ")
        if userExists(username):
            # query for password
            checkPassword(username)
        else:
            print("User {} does not exist".format(username))

    elif "p" in choice:
        printAll()

    elif "q" in choice:
        # quit
        exit(0)
    else:
        # ???
        print("{} is not a valid commnad. Please try again.")
