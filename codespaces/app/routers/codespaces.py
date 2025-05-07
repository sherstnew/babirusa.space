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
            return str(ex_userport.port)
        else:
            user_ports = await UserPort.find().to_list()
        
            used_ports = list(map(lambda x: x["port"], user_ports))
            
            global port
            port = 0
            
            if len(used_ports) == 0:
                port = 1000
            else:
                if max(used_ports) + 1 < 52000:
                    port = max(used_ports) + 1
                else:
                    return HTTPException(404)

            if not os.path.exists(os.path.normpath(babirusaaa_home + f"/user-{login.username}-config")):
                copy_tree(os.path.normpath(babirusaaa_home + "/baseconfig"), os.path.normpath(babirusaaa_home + f"/user-{login.username}-config"))
                copy_tree(os.path.normpath(babirusaaa_home + "/baseprj"), os.path.normpath(babirusaaa_home + f"/user-{login.username}-prj"))
                

            new_container = client.containers.run(
                'skfx/babirusa-codeserver',
                auto_remove=True,
                detach=True,
                # hostname=f"user-{login.username}.babirusa.skfx.io",
                hostname="0.0.0.0",
                volumes=[f"{babirusaaa_home}/user-{login.username}-config:/home/coder/.config", f"{babirusaaa_home}/user-{login.username}-prj:/home/coder/prj"],
                network="babirusa",
                environment=["XDG_DATA_HOME=/home/coder/.config", f"PASSWORD={login.password}"],
                ports={'8080/tcp': port}
            ).id
            
            userport = UserPort(username=login.username, port=port)
            await userport.create()

            network = client.networks.get('babirusa').attrs

            for cid, payload in network['Containers'].items():
                if new_container == cid:
                    ip_address = payload['IPv4Address'].split('/')[0]

            return str(port)
    
    else:
        raise HTTPException(403)



