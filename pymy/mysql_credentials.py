import os


def credential(instance):
    alias = "MYSQLDM_" + instance
    connection_kwargs = {
        'db': os.environ[alias + "_DATABASE"],
        'user': os.environ[alias + "_USERNAME"],
        'host': os.environ[alias + "_HOST"],
        'password': os.environ[alias + "_PASSWORD"],
    }
    return connection_kwargs
