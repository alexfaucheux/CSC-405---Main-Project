from app.user_management.Database import UserDB

# Opens existing database


class User():
    def __init__(self):
        self.database = UserDB("user_info.db")

    # Creates User
    def create(self, fname, lname, email, password):
        avail = self.database.checkAvail(email)

        # Email not valid
        if avail == 0:
            return "ERROR: 0" #Invalid address

        self.database.insert(email, password, fname, lname)

        self.database.exit()
        return "SUCCESS"

    # Login for user
    def login(self, email, entered_password):
        avail = self.database.checkAvail(email)
        real_password = 0

        if avail == 0:
            real_password = self.database.fetch_userPASS(email)[0][0]

        else:
            return "ERROR: 1" #No account with address

        # Username or password are invalid
        if entered_password != real_password:
            return "ERROR: 2" #Login error, wrong password

        self.database.exit()
        return "SUCCESS"