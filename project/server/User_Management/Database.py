# Python code to demonstrate table creation and
# insertions with SQL 

# importing module
import sqlite3
import datetime

class UserDB():
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.crsr = self.connection.cursor()

    def create_table(self):
        sql_command = """CREATE TABLE users (  
         email VARCHAR(100) PRIMARY KEY,
         pass  VARCHAR(100),   
         fname VARCHAR(20),  
         lname VARCHAR(30),
         joining DATE);"""

        self.crsr.execute(sql_command)


    def insert(self, email, password, first_name, last_name, joinDate=datetime.datetime.now()):
        try:
            cmd = """INSERT INTO users VALUES ("{}", "{}", "{}", "{}", "{}");""".format(email, password, first_name, last_name, joinDate)
            self.crsr.execute(cmd)
            return 1

        except:
            return 0

    def fetch_userPASS(self, email):
        self.crsr.execute('SELECT pass FROM users WHERE email = "{}"'.format(email))
        return self.crsr.fetchall()

    def fetchall(self):
        self.crsr.execute('SELECT * FROM users')
        return self.crsr.fetchall()

    def checkAvail(self, email):
        self.crsr.execute('SELECT email FROM users WHERE email = "{}"'.format(email))
        row = self.crsr.fetchall()
        if len(row) > 0:
            return 0
        return 1


    def exit(self):
        # To save the changes in the files.
        self.connection.commit()

        # close the connection
        self.connection.close()