import docker
import secrets
from pymysql import connect as db_connect
import pymysql.cursors
import os
from distutils.dir_util import copy_tree

class DBConnection():
    hostname = "10.66.66.27"
    username = "babirusa"
    password = "babirusa"
    db = 'babirusa'

    def __enter__(self):
        self.connection = db_connect(host=self.hostname,
                                     user=self.username,
                                     password=self.password,
                                     database=self.db,
                                     cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        return self

    def read_once(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def read_all(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def write_query(self, query, params):
        self.cursor.execute(query, params)
        self.connection.commit()

    def __exit__(self, type, value, traceback):
        self.connection.close()

client = docker.from_env()
babirusaaa_home = "/Users/skifry/babirusaaaa/"

def launchCodespace(id, code):
    if not os.path.exists(babirusaaa_home + f"user{id}-config"):
        copy_tree(babirusaaa_home + "baseconfig", babirusaaa_home + f"user{id}-config")
        copy_tree(babirusaaa_home + "baseprj", babirusaaa_home + f"user{id}-prj")
        

    new_container = client.containers.run(
        'skfx/babirusa-codeserver',
        auto_remove=True,
        detach=True,
        hostname=f"userid{id}.babirusa.skfx.io",
        volumes=[f"{babirusaaa_home}user{id}-config:/home/coder/.config", f"{babirusaaa_home}user{id}-prj:/home/coder/prj"],
        network="babirusa",
        environment=["XDG_DATA_HOME=/home/coder/.config"]
    ).id

    network = client.networks.get('babirusa').attrs

    for cid, payload in network['Containers'].items():
        if new_container == cid:
            ip_address = payload['IPv4Address'].split('/')[0]

    with DBConnection() as db:
        routing_key = secrets.token_hex(16)
        db.write_query("UPDATE code_check SET routing_cookie = %s, target_ip = %s WHERE id = %s AND code = %s", (routing_key, ip_address, id, code))






