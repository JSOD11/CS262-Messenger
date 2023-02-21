import curses
import fnmatch
import sys
import chat_pb2
from chat_pb2_grpc import ChatServiceStub
from client import Client
from menu import menu

def load_user_menu(this_client: Client, stub: ChatServiceStub):

  # user menu, lets users pick from a set of actions

  actions = ["Send messages", "View my messages", "Logout", "Delete account"]
  message = "\n" + this_client.SESSION_INFO["username"] + "'s Account\n\n"
  user_choice = wrap_menu(menu, actions, message)

  if user_choice == "Send messages":

    decoded_data = this_client.list_accounts(stub)
    accounts = decoded_data.info.split("\n")
    message = "\nWho would you like to send messages to?\n\n"

    receiver = wrap_menu(menu, accounts, message)

    print("\nInput a message and press enter to share with " + receiver + " or EXIT to end the chat.\n")
    while True:
      message = wrap_input("")
      processed_message = "<" + this_client.SESSION_INFO["username"] + ">" + message 
      if message == "EXIT":
        print(f"\n[ENDING CHAT] Ending chat with {receiver}\n")
        break
      this_client.send_message(this_client.SESSION_INFO["username"], receiver, processed_message, stub)
    load_user_menu(this_client, stub)
    return

  elif user_choice == "View my messages":
    this_client.view_msgs(this_client.SESSION_INFO["username"], stub)
    wrap_input("\nPress enter to return to the main menu.\n\n")
    load_user_menu(this_client, stub)
  elif user_choice == "Logout":
    this_client.logout(this_client.SESSION_INFO["username"], stub)
    start(this_client, stub)

  elif user_choice == "Delete account":

    actions = ["Go back", "Delete forever"]
    message = "\nAre you sure you would like to delete this account? Any unread messages will be permanently lost.\n\n"
    choice = wrap_menu(menu, actions, message)

    if choice == "Delete forever":
      this_client.delete_account(this_client.SESSION_INFO["username"], stub)
      return start(this_client, stub)
    else:
      load_user_menu(this_client, stub)

def start(this_client: Client, stub: ChatServiceStub):
  # start menu, lets user pick their first action
  actions = ["Login", "Create account", "List accounts", "Quit Messenger"]
  message = "\nWelcome to Messenger! What would you like to do?\n\n"
  try:
    name = wrap_menu(menu, actions, message)
  except KeyboardInterrupt:
    return this_client.quit_messenger()


  if name == "Quit Messenger" or name == 0:
    return this_client.quit_messenger()

  elif name == "Create account":
    print("\nWelcome to messenger! Please input a username to join or EXIT to exit.\n")
    status = 1
    while status == 1:
      account_name = wrap_input("Username: ")

      if account_name == "EXIT":
        return start(stub)

      if len(account_name) > 10:
        print("\nUsernames must be at most 10 characters.\n")
      else:
        status = this_client.create_account(account_name, stub)
    
    load_user_menu(this_client, stub)

  elif name == "Login":
    try:
        if this_client.get_login_input(stub) == 0:
            load_user_menu(this_client, stub)
        else:
            return start(this_client, stub)
    except KeyboardInterrupt:
        return this_client.quit_messenger()

  elif name == "List accounts":
    decoded_data = this_client.list_accounts(stub)
    if decoded_data != 1:
      accounts = decoded_data.info.split("\n")
      print("\nPlease input a text wildcard. * matches everything, ? matches any single character, [seq] matches any character in seq, and [!seq] matches any character not in seq.\n")
      wildcard = wrap_input("Text wildcard: ")
      print("\nList of accounts currently on the server matching " + wildcard + ":\n")
      for account in accounts:
        if fnmatch.fnmatch(account, wildcard):
          print(str(account))
      wrap_input("\nPress enter to return to the main menu.\n\n")
    else:
      print("\nThere are currently no accounts on the server.\n")
      wrap_input("Press enter to return to the main menu.\n\n")
    
    return start(this_client, stub)

def wrap_menu(menu, actions, message):
    try:
        return curses.wrapper(menu, actions, message)
    except KeyboardInterrupt:
        return this_client.quit_messenger()

def wrap_input(string):
    try:
        return input(string)
    except KeyboardInterrupt:
        return this_client.quit_messenger()


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("please specify running client or server")
    # todo: fix this for gRPC
#   elif sys.argv[1] == "client":
#     this_client = WireClient()
#     this_client.CLIENT.connect(this_client.ADDR)
#     start(this_client)
#   elif sys.argv[1] == "server":
#     this_server = WireServer()
#     this_server.bind(this_server.ADDR)
#     this_server.start()
  else:
    print("please specify running client or server")