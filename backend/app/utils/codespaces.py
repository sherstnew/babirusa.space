import os
import docker
import shutil
from distutils.dir_util import copy_tree
from app import SECRET_KEY_USER
from app.data.models import Pupil, UserIp
from typing import List
from cryptography.fernet import Fernet
from app.utils.error import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



dir_path = os.path.dirname(os.path.realpath(__file__))
cipher = Fernet(SECRET_KEY_USER)

async def launch_codespace(username: str, password: str) -> str | None:
    user = await Pupil.find_one(Pupil.username == username)
    if user and password == (cipher.decrypt(user.hashed_password.encode('utf-8')).decode('utf-8')):
        client = docker.from_env()
        babirusaaa_home = os.path.normpath(dir_path + '../../../babirusa/')
        
        ex_userip = await UserIp.find_one(UserIp.username == username)
        
        if ex_userip:
            return str(ex_userip.ip)
        else:
            if not os.path.exists(os.path.normpath(babirusaaa_home + f"/baseconfig")):
                os.makedirs(os.path.normpath(babirusaaa_home + f"/baseconfig"))
            
            if (not os.path.exists(os.path.normpath(babirusaaa_home + f"/user-{username}-config"))) or (not os.path.exists(os.path.normpath(babirusaaa_home + f"/user-{username}-prj"))):
                copy_tree(os.path.normpath(babirusaaa_home + "/baseconfig"), os.path.normpath(babirusaaa_home + f"/user-{username}-config"))
                copy_tree(os.path.normpath(babirusaaa_home + "/baseprj"), os.path.normpath(babirusaaa_home + f"/user-{username}-prj"))
            
            base_main = os.path.join(babirusaaa_home + "/baseprj", "main.py")
            user_main = os.path.join(babirusaaa_home + "/baseprj", "main.py")

            if os.path.exists(base_main) and not os.path.exists(user_main):
                shutil.copy2(base_main, user_main)
        
            client.images.get("skfx/babirusa-codeserver")

            new_container = client.containers.run(
                'skfx/babirusa-codeserver',
                detach=True,
                user=0,
                command=["--disable-telemetry", "--disable-update-check", "--log=debug", "/home/coder/prj"],
                hostname="0.0.0.0",
                volumes=[f"{babirusaaa_home}/user-{username}-config:/home/coder/.config", f"{babirusaaa_home}/user-{username}-prj:/home/coder/prj"],
                environment=["XDG_DATA_HOME=/home/coder/.config", f"PASSWORD={password}"],
                mem_limit="512m",
                mem_reservation="256m",
                nano_cpus=500000000,
                cpu_shares=512,
            ).id

            network = client.networks.get('bridge').attrs

            for cid, payload in network['Containers'].items():
                # logger.info(f"Checking container ID: {cid}")
                if new_container == cid:
                    ip_address = payload['IPv4Address'].split('/')[0]
                    logger.info(f"Found IP address: {ip_address}")
                    userport = UserIp(
                                    username=username,
                                    ip=ip_address,
                                    container_id=new_container
                                )
                    logger.info(f"Creating UserIp entry for user")
                    await userport.create()
                    return ip_address
    
    else:
        return None
    

async def check_container_status(pupils):
    usernames = []
    for pupil in pupils:
        usernames.append(pupil.username)
        
    userips = await UserIp.find_many({"username": {"$in": usernames}}).to_list()
    print(userips, flush=True)
    if not userips:
        raise Error.PUPIL_NOT_FOUND
    
    client = docker.from_env()
    pupils = []
    for userip in userips:
        pupil = await Pupil.find_one(Pupil.username == userip.username)
        print(pupil, 'pupil', flush=True)
        if pupil:
            pupil = pupil.fetch_links()
        status = client.containers.get(userip.container_id).status.lower()
        if pupil.container_status != status:
            pupil.container_status = status
            await pupil.save()
        pupils.append(pupil)
        
    return pupils
        
    



