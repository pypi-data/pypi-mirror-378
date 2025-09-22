from . import core

class GlobChatConsole:
    def connect(self):
        username = input("Enter your username: ")
        core.chat_loop(username)

globchat = GlobChatConsole()
