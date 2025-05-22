import os
import docker
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from distutils.dir_util import copy_tree
from app.data.schemas import LoginRequest
from app.data.models import User, UserPort
dir_path = os.path.dirname(os.path.realpath(__file__))

router = APIRouter(prefix="/codespaces")

@router.post('/launch/')
async def launchCodespace(login: LoginRequest) -> str:
    user = await User.find_one(User.username == login.username)
    if user and login.password == user.password:
        client = docker.from_env()
        babirusaaa_home = os.path.normpath(dir_path + '../../../babirusa/')
        
        ex_userport = await UserPort.find_one(UserPort.username == login.username)
        
        if ex_userport:
            return str(ex_userport.ip)
        else:
            if not os.path.exists(os.path.normpath(babirusaaa_home + f"/user-{login.username}-config")):
                copy_tree(os.path.normpath(babirusaaa_home + "/baseconfig"), os.path.normpath(babirusaaa_home + f"/user-{login.username}-config"))
                copy_tree(os.path.normpath(babirusaaa_home + "/baseprj"), os.path.normpath(babirusaaa_home + f"/user-{login.username}-prj"))
                
            client.images.get("skfx/babirusa-codeserver")

            new_container = client.containers.run(
                'skfx/babirusa-codeserver',
                detach=True,
                user=0,
                command=["--disable-telemetry", "--disable-update-check"],
                # hostname=f"user-{login.username}.babirusa.skfx.io",
                hostname="0.0.0.0",
                volumes=[f"{babirusaaa_home}/user-{login.username}-config:/home/coder/.config", f"{babirusaaa_home}/user-{login.username}-prj:/home/coder/prj"],
                # network="babirusa",
                environment=["XDG_DATA_HOME=/home/coder/.config", f"PASSWORD={login.password}"],
                # ports={'8080/tcp': 8080}
            ).id

            network = client.networks.get('bridge').attrs

            for cid, payload in network['Containers'].items():
                if new_container == cid:
                    ip_address = payload['IPv4Address'].split('/')[0]

                    userport = UserPort(username=login.username, ip=ip_address)
                    await userport.create()
                    return ip_address
    
    else:
        raise HTTPException(403)



