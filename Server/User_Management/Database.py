import sqlite3
import datetime

class UserDB():
    def __init__(self, filename):
        # Opens connection to database file
        self.connection = sqlite3.connect(filename)
        self.crsr = self.connection.cursor()

    # Creates fresh table.  Currently only creates one with specific user keys.
    def create_table(self):
        sql_command = """CREATE TABLE users (  
         email VARCHAR(100) PRIMARY KEY,
         pass  VARCHAR(100),   
         fname VARCHAR(20),  
         lname VARCHAR(30),
         joining DATE);"""

        self.crsr.execute(sql_command)

    def drop_table(self):
        sql_command = """DROP TABLE users"""

        self.crsr.execute(sql_command)

    # Adds new user to database.
    # Fails if primary key already exists inside database
    def insert(self, email, password, first_name, last_name, joinDate=datetime.datetime.now()):
        try:
            cmd = """INSERT INTO users VALUES ("{}", "{}", "{}", "{}", "{}");""".format(email, password, first_name, last_name, joinDate)
            self.crsr.execute(cmd)
            return 1

        except:
            return 0

    # Gets password associated with email
    def fetch_userPASS(self, email):
        self.crsr.execute('SELECT pass FROM users WHERE email = "{}"'.format(email))
        return self.crsr.fetchall()

    # Returns data on all users
    def fetchall(self):
        self.crsr.execute('SELECT * FROM users')
        return self.crsr.fetchall()

    # Checks to see if email is available to add as primary key
    def checkAvail(self, email):
        self.crsr.execute('SELECT email FROM users WHERE email = "{}"'.format(email))
        row = self.crsr.fetchall()
        if len(row) > 0:
            return 0
        return 1

    # Closes database
    def exit(self):
        # To save the changes in the files.
        self.connection.commit()

        # close the connection
        self.connection.close()

