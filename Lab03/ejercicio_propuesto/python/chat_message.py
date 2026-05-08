class ChatMessage:

    WHOISIN = 0
    MESSAGE = 1
    LOGOUT = 2

    PRIVATE = 3
    FUNCTION = 4
    FILE = 5

    def __init__(self, msg_type, message, extra=None):
        self.type = msg_type
        self.message = message
        self.extra = extra

    def get_type(self):
        return self.type

    def get_message(self):
        return self.message

    def get_extra(self):
        return self.extra