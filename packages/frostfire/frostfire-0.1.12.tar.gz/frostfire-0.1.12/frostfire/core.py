from logging.handlers import TimedRotatingFileHandler
import yaml
import requests
import logging
import datetime
import os

def get_file_timestamp():
    x=3
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def monitron_heartbeat(monitron_url,script_id,logger):
    logger.info("Starting monitor heartbeat...")

    if not monitron_url.endswith('/'):
        monitron_url = f'{monitron_url}/'

    url = f"{monitron_url}{script_id}"
    try:
        response = requests.get(url=url,timeout=3)
        logger.info(f'Pinged monitron:{response.status_code}')
    except Exception as e:
        logger.error(f'Monitron heartbeat failed. {e}')

def send_telegram_message(message,logger,chat_id=None,bot_token=None):
    logger.info(fr'Starting send_telegram_message function...')

    if chat_id is None and bot_token is None:
        logger.info(fr'Loading parallax...')
        parallax = load_parallax()
        chat_id = parallax['monitron']['telegram_chat_id']
        bot_token = parallax['monitron']['telegram_bot_token']

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    payload = {
        'chat_id': chat_id,
        'text': message
    }
    logger.info(fr'Sending message:{message}')
    response = requests.post(url, data=payload)
    logger.info(fr'Message sent:{response.status_code}')


def get_logger(log_file_dir_path,log_file_prefix,logger_name='frostfire',when='midnight',print_to_console=False):

    log = logging.getLogger(logger_name)
    log.setLevel(logging.INFO)

    if not log.handlers:
        os.makedirs(log_file_dir_path, exist_ok=True)
        log_file_path = os.path.join(log_file_dir_path, f"{log_file_prefix}.log")

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s'
        )

        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when=when,
            interval=1,
            backupCount=0,
            encoding="utf-8",
            utc=False
        )
        file_handler.setFormatter(formatter)

        log.addHandler(file_handler)

        if print_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            log.addHandler(console_handler)
    return log

def load_parallax():
    with open(os.getenv('PARALLAX')) as f:
        parallax = yaml.safe_load(f)
    return parallax
