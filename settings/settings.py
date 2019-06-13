import logging

config_data = {
    "development": {
        "log_level": logging.DEBUG,
        "log_filename": "/tmp/dqt.log",
        "host": "localhost",
        "user": "dqt",
        "password": "dqt",
        "port": "5432",
        "db": "dqt",
        "schema": "development, postgis, public",
        "exchange_name": "dqt_development",
        "rabbit_host": "localhost",
        "rabbit_port": "5672",
        "rabbit_username": "rabbit",
        "rabbit_password": "rabbit",
    },
}


def init(environment):
    global env
    env = environment


def get_param(param_name):
    return config_data[env][param_name]
