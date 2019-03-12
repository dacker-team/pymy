import os
import pymysql
import sshtunnel
from sshtunnel import SSHTunnelForwarder
from . import mysql_credentials


def execute_query(instance, query):
    connection_kwargs = mysql_credentials.credential(instance)
    connection_kwargs["cursorclass"] = pymysql.cursors.DictCursor

    # Create an SSH tunnel
    ssh_host = os.environ.get("SSH_%s_HOST" % instance)
    ssh_user = os.environ.get("SSH_%s_USER" % instance)
    ssh_path_private_key = os.environ.get("SSH_%s_PATH_PRIVATE_KEY" % instance)
    if ssh_host:
        print("SSH")
        tunnel = SSHTunnelForwarder(
            (ssh_host, 22),
            ssh_username=ssh_user,
            ssh_private_key=ssh_path_private_key,
            remote_bind_address=(os.environ.get("MYSQLDM_%s_HOST" % instance), 3306),
            local_bind_address=('localhost', 6543),  # could be any available port
        )
        # Start the tunnel
        try:
            tunnel.start()
            print("Tunnel opened!")
        except sshtunnel.HandlerSSHTunnelForwarderError:
            pass

        connection_kwargs["host"] = "localhost"
        connection_kwargs["port"] = 6543

    connection = pymysql.connect(**connection_kwargs)

    cursor = connection.cursor()
    try:
        cursor.execute(query)
    except Exception as e:
        if ssh_host:
            tunnel.close()
        print("Error:" + str(e))
        raise
    connection.commit()
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    if ssh_host:
        tunnel.close()
        print("Tunnel closed!")

    return result
