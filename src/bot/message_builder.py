from io import StringIO


class MessageBuilder:
    def __init__(self):
        self.message = StringIO()

    def header(self, header):
        self.message.write(f'> **{header}**\n\n')
        return self

    def deals(self, deals: dict, format_func):
        for deal in deals:
            self.message.write(format_func(deal))
            self.message.write('\n')
        return self

    def tags(self, user_ids):
        for user_id in user_ids:
            self.message.write(f'<@{user_id}> ')
        return self

    def build(self):
        return self.message.getvalue()
