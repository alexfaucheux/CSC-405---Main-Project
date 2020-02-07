from socket import *
from User import User

# Creates Socket for Server
def create_socket(server_port):
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(1)
    return server_socket


# Receives message from client
def recv_message(server_socket, buffer_size):
    connection_socket, address = server_socket.accept()
    incoming_message = connection_socket.recv(buffer_size)
    return connection_socket, incoming_message, address


# Sends message to client
def send_message(connection_socket, message):
    connection_socket.send(message)
    connection_socket.close()
    return


server_port = "8000"
server_socket = create_socket(int(server_port))
print("Server started and is using port " + server_port)
print("Ready to receive requests...\n")

# Waits for request and responds appropriately.
# Always running until script is terminated
while True:
    connection_socket, incoming_message, address = recv_message(server_socket, 1024)
    incoming_message = incoming_message.decode(encoding='utf-8', errors='strict')
    if(len(incoming_message) > 3):
        message_parse = incoming_message.split()
        form_data = message_parse[len(message_parse)-1].split('&')
        if len(form_data) == 2:
            username = form_data[0][9:]
            password = form_data[1][9:]
            print("Logging in as: \nUsername: {} \nPassword: {}\n".format(username, password))
            user = User()
            response = user.login(username, password)
            print(response)
            print

        elif len(form_data) == 4:
            fname = form_data[0][6:]
            lname = form_data[1][6:]
            username = form_data[2][9:]
            password = form_data[3][9:]
            print("Creating user: \nFirst Name: {} \nLast Name: {} \nUsername: {} \nPassword: {}\n".format(
                fname, lname, username, password))
            user = User()
            response = user.create(fname, lname, username, password)
            print(response)
            print

