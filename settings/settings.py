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
        "kf_extractor_host": "scrape.kingfisher.open-contracting.org",
        "kf_extractor_user": "ocdskfpreadonly",
        "kf_extractor_password": "LJNBQvRT83QTi9og",
        "kf_extractor_port": "5432",
        "kf_extractor_db": "ocdskingfisherprocess",
    },
    "production": {
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
        "kf_extractor_host": "scrape.kingfisher.open-contracting.org",
        "kf_extractor_user": "ocdskfpreadonly",
        "kf_extractor_password": "LJNBQvRT83QTi9og",
        "kf_extractor_port": "5432",
        "kf_extractor_db": "ocdskingfisherprocess",
    },
}


def init(environment):
    global env
    env = environment


def get_param(param_name):
    return config_data[env][param_name]
