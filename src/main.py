import os
import logging
import sys
from bot.bot import DealAlerterBot
from dotenv import load_dotenv

def initialize_logging(log_path):
    logFormatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    logging_handlers = [
        logging.FileHandler(filename=log_path, encoding='utf-8', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
    for handler in logging_handlers:
        handler.setFormatter(logFormatter)
    logging.basicConfig(level=logging.INFO, handlers=logging_handlers)

if __name__ == '__main__':
    load_dotenv()
    token = os.environ['BOTTOKEN']
    db_path = os.environ['DFA_DB_PATH']
    log_file_path = os.path.join(db_path, 'bot.log')
    initialize_logging(log_file_path)
    bot = DealAlerterBot()
    bot.run(token)