from Database import UserDB

database = UserDB("user_info.db")
database.drop_table()
database.create_table()