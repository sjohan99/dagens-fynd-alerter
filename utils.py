
def get_command(message_content: str, prefix):
    contents = message_content.strip().split()
    if len(contents) < 2:
        return None
    if contents[0] != prefix.strip():
        return None
    return contents[1]

class CommandVerifier:

    def __init__(self, prefix: str, command: str):
        self.prefix = prefix.strip()
        self.command = command
        self.verified_result = None

    def verify_keyword(self, message_content: str):
        try:
            contents = message_content.strip().split()
            assert len(contents) == 3
            assert contents[0] == self.prefix
            assert contents[1] == self.command
        except AssertionError:
            return False
        self.verified_result = contents[2]
        return True

    def verify_sub(self, message_content: str):
        try:
            contents = message_content.strip().split()
            assert len(contents) == 2
            assert contents[0] == self.prefix
            assert contents[1] == self.command
        except AssertionError:
            return False
        self.verified_result = ''
        return True
