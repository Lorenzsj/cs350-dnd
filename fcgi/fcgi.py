#!/usr/bin/python3

from flask import Flask, session, redirect, url_for, escape, request, render_template, Response
import string, random, hashlib, binascii, sqlite3, os, smtplib, time

app = Flask(__name__)


# Global Variables

# auth and info database connections
conn = sqlite3.connect('/opt/drjimbo-game/vars/auth.db')
conn2 = sqlite3.connect('/opt/drjimbo-game/vars/info.db')

# users database from info.db
users = []
regTable = {}

# ------------------------------------------------------------------------------

#     Internal System Calls (Index page, Login Page, CSRF handlers)

# ------------------------------------------------------------------------------

@app.route('/')
def index():
    if 'username' in session:
        if 'csrf_token' in session:
            return render_template('index.html', name=escape(session['username']), csrf_token=session['csrf_token'])
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/debug')
def debug():
    if 'username' in session:
        if 'csrf_token' in session:
            return render_template('debug.html', name=escape(session['username']), csrf_token=session['csrf_token']) # Expected State while logged in
        else:
            return render_template('debug.html', name=escape(session['username'])) # Bad state (unless login page)
    else:
        if 'csrf_token' in session:
            return render_template('debug.html', csrf_token=session['csrf_token']) # Very bad state (defintely a security problem)
        else:
            return render_template('debug.html') # Expected state while logged out

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = request.form['username'].replace("\n", "")
            passwd = request.form['password'].replace("\n", "")
            print("Attempting auth with {}".format(user))
            if(auth(user, passwd)):
                session['username'] = user
                print("{} is logged in".format(user))
                # The user properly logged in. Give them a "cookie"
                if 'csrf_token' not in session:
                    # We need to generate a csrf key, and add it to the session
                    session['csrf_token'] = generateSecureKey(16)
                    print("{} now has a csrf key: {}".format(user, session['csrf_token']))
            else:
                print("User '{}' failed to auth".format(user))
                session.pop('username', None)
            return redirect('/')
        except Exception as e:
            # Someone is injecting stuff. Cut that out.
            print("invalid login: {}\n\n{}".format(request, e))
            return redirect('/')
    else: # GET request for webpage
        if 'username' in session:
            return redirect('/')
        else:
            return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        if 'csrf_token' in session:
            # remove the username from the session if it's there
            # Users are also unauthenticated client side if they don't visit pages within 15 minues, and need to relog
            session.pop('username', None)
            session.pop('csrf_token', None)
            return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ------------------------------------------------------------------------------

#     Registration and Passowrd Reset

# ------------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username'].replace("\n", "")
        email = getUserEmailFromUsername(user.strip())
        nkey = generateSecureKey(16)
        while isKeyCollision(nkey):
            nkey = generateSecureKey(16)
        regTable[user] = nkey
        print("Sending verification email. Username: {} Email: {} Registration Key: {}".format(user, email, nkey))
        sendVerificationEmail(email, regTable[user])
        return redirect('/check-mail')
    else:
        return render_template('register.html')

@app.route('/check-mail')
def checkMail():
    return render_template('check-mail.html')

@app.route('/password', methods=['GET', 'POST'])
def password():
    if request.method == 'POST':
        print("step1")
        if request.values['key'].strip() != "":
            p1 = request.form['password'].strip()
            p2 = request.form['password2'].strip()
            print("{} {}".format(p1, p2))
            if p1 != "" and p2 != "" and p1 != p2:
                print("step3")
                for name in regTable:
                    print("{}: {}".format(name, regTable[name]))
                    if regTable[name] == request.form['key'].strip():
                        if userExists(name):
                            deleteUser(name)
                        addUser(name, password)
                        return redirect('/registered')
            return redirect ('/debug') # redirect('/')
        else:
            return redirect('/')
    else:
        if 'username' in session:
            if 'csrf_token' in session:
                return redirect('/') # return render_template('create-pw.html', name=escape(session['username']), csrf_token=session['csrf_token'])
            else:
                return redirect('/')
        else:
            if 'csrf_token' in session:
                return redirect('/')
            else:
                try:
                    return render_template('create-pw.html', key=request.values['key'])
                except:
                    return render_template('create-pw.html', key="key")

@app.route('/registered')
def registered():
    return render_template('registered.html')

# DEBUG ONLY

@app.route('/printRegTable')
def printReg():
    out = ""
    if len(regTable > 0):
        for user in regTable:
            out += "Username: {} Registration Key: {}<br\>".format(user, regTable[user])
    else:
        out += "RegTable is Empty"
    return out;

# ------------------------------------------------------------------------------

#     Registration Mailer and Helpers

# ------------------------------------------------------------------------------

def isKeyCollision(nkey):
    for user in regTable:
        if regTable[user] == nkey:
            return True
    return False


def getEmailFromFile(filename):
    global gmail_user, gmail_password
    actual = os.path.abspath(os.path.expanduser(filename))

    with open(actual) as f:
        lines = f.readlines()
        try:
            gmail_user = lines[0].strip()
            gmail_password = lines[1].strip()
        except:
            print("Password file badly formatted")

def getUserEmailFromUsername(username):
    return "{}@clarkson.edu".format(username)

def sendVerificationEmail(email, secureKey):
    subject = "Email Verification for Drjimbo-Game"
    body = "Hello,\n\nHere is your verification url for Drjimbo-Game:\n\ndrjimbo.cslabs.clarkson.edu/password?key={}\n\nHave a nice day!".format(secureKey)

    message = """\
From: {}
To: {}
Subject: {}

{}
""".format(gmail_user, email, subject, body)

    print(message)


    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, email, message)
        server.close()

        print ('Email sent!')
    except Exception as e:
        print ("Something went wrong.\n{}".format(e))


# ------------------------------------------------------------------------------

#     Live pages (Game, Stats page, user profile)

# ------------------------------------------------------------------------------

@app.route('/play')
def play():
    if 'username' in session:
        if 'csrf_token' in session:
            return render_template('game.html', name=escape(session['username']), csrf_token=session['csrf_token'])
        else:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/live-game')
def game():
    if 'username' in session:
        if 'csrf_token' in session:
            return redirect('/game')
        else:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/dev-game')
def debug_game():
    if 'username' in session:
        if 'csrf_token' in session:
            return render_template('template-game.html', name=escape(session['username']), csrf_token=session['csrf_token'])
        else:
            return redirect('/')
    else:
        return redirect('/')

# ------------------------------------------------------------------------------

#     Database Function Calls (scoring, directory info, etc)

# ------------------------------------------------------------------------------

@app.route('/score', methods=['GET','POST'])
def database():
    if request.method == 'POST':
        if 'csrf_token' in session:
            username = session['username']
            csrf_token = request.values.get("csrf_token")
            score = request.values.get("score")
            if session['csrf_token'] == csrf_token:
                print("{} scored {} points".format(username, score))
                if username in users: # Check to see that the username in the auth.db is also in the info.db
                    incrementCumulative(username, score)
                    setHighScore(username, score)
            else:
                print("Unverified score - Server CSRF: {} Client CSRF: {} Server Username: {} Score: {}".format(session['csrf_token'], csrf_token, session['username'], score))
                return(score)
        else:
            csrf_token = request.values.get("token")
            score = request.values.get("score")
            print(score)
            return(score)
    else:
        output = "<html><head><title>debug output</title></head><body>\n"
        for entry in request.values:
            output += str(entry) + ": " + str(request.values.get(entry)) + "<br/>\n"
        output += "</body></html>"
        return output

@app.route('/users.list')
def getusernames():
    getUsernameList()
    return "{}".format(users)

@app.route('/r5.list')
def getRandomFiveUsers():
    getUsernameList()
    ln = len(users)
    ru = []
    for i in range(1,5):
        ru.append(users[int(random.random() * ln)])
    return "{}".format(ru)

@app.route('/stats.json')
def statsJson():
    getUsernameList()
    begin = "{\n"

    hscore = "  \"hscores\": {\n"
    for user in users:
        scr = ""
        if str(getCumulativeScore(user) == ""):
            scr = "0"
        else:
            scr = str(getCumulativeScore(user))
        hscore += "    \"{}\": {},\n".format(user, scr)
    hscore = hscore[:-2] + "\n"
    hscore += "  },\n"

    uscore = "  \"uscores\": {\n"
    for user in users:
        scr = ""
        if str(getTopScore(user)) == "":
            scr = "0"
        else:
            scr = str(getTopScore(user))
        uscore += "    \"{}\": {},\n".format(user, scr)
    uscore = uscore[:-2] + "\n"
    uscore += "  }\n"

    end = "}"
    return Response(begin + hscore + uscore + end, mimetype="application/json")

# ------------------------------------------------------------------------------

#     INFO DATABASE FUNCTIONS

# ------------------------------------------------------------------------------

def getUsernameList():
    c = conn2.cursor()
    global users
    users = []
    c.execute("SELECT username FROM users")
    for entity in c.fetchall():
        users.append(entity[0])

def getRealName (username):
    c = conn2.cursor()
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT realname FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getTopScores (username):
    c = conn2.cursor()
    if not username in users:
        print("{} is not a valid user.".format(username))
        return (-1, -1, -1)
    c.execute("SELECT top1, top2, top3 FROM users WHERE username = '{}'".format(username))
    return list(c.fetchone())

def getTopScore (username):
    scores = getTopScores(username)
    scr = max(max(scores[0], scores[1]), scores[2])
    return scr

def getCumulativeScore (username):
    c = conn2.cursor()
    if not username in users:
        print("{} is not a valid user.".format(username))
        return -1
    c.execute("SELECT cumulative FROM users WHERE username = '{}'".format(username))
    try:
        return int(c.fetchone()[0])
    except:
        return -1

def getYear (username):
    c = conn2.cursor()
    if not username in users:
        print("{} is not a valid user.".format(username))
        return -1
    c.execute("SELECT year FROM users WHERE username = '{}'".format(username))
    try:
        return int(c.fetchone()[0])
    except:
        return -1

def getMajor (username):
    c = conn2.cursor()
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT major FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getDepartment (username):
    c = conn2.cursor()
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT department FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getTitle (username):
    c = conn2.cursor()
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT title FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getOfficeLocation (username):
    c = conn2.cursor()
    if not username in users:
        print("{} is not a valid user.".format(username))
        return ""
    c.execute("SELECT office FROM users WHERE username = '{}'".format(username))
    return c.fetchone()[0]

def getFacultyOrStudent (username):
    c = conn2.cursor()
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
    c = conn2.cursor()
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
    c = conn2.cursor()
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

def isStudent (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return False
    if getFacultyOrStudent(username) == 's':
        return True
    else:
        return False

def isFaculty (username):
    if not username in users:
        print("{} is not a valid user.".format(username))
        return False
    if getFacultyOrStudent(username) == 'f':
        return True
    else:
        return False

# ------------------------------------------------------------------------------

#     AUTH DATABASE FUNCTIONS

# ------------------------------------------------------------------------------

def auth(user, password):
    passhash = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'assault', 100000))
    userhash = getUserFromDatabase(user)
    print("Username: {} Userhash: {} Passhash: {}".format(user, userhash, passhash))
    if userhash != "":
        if userhash == passhash:
            return True
    return False

def getUserFromDatabase(username):
    # add database code
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (user TEXT, passhash TEXT)")
    conn.commit()
    c.execute("SELECT * FROM users WHERE user={}".format(quote_identifier(username)))
    try:
        return c.fetchone()[1]
    except:
        return ""

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

def userExists(username):
    # this function needs to take a username and check to see if the username exists. If so, return true. Otherwise, return false
    c.execute("SELECT * FROM users WHERE user={}".format(quote_identifier(username)))
    try:
        if username == c.fetchone()[0]:
            return True
        return False
    except:
        return False

# ------------------------------------------------------------------------------

#     GENERAL FLASK FUNCTIONS AND SQL SANITIZERS

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

def generateSecureKey(size):
    # print("creating secure key of size " + str(size))
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))

app.secret_key = generateSecureKey(64)
getEmailFromFile("/etc/dr.pass")

if __name__ == "__main__":
    app.run()
