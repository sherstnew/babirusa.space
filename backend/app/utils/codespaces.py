import logging
import os
import shutil
from distutils.dir_util import copy_tree
from typing import Optional

import docker
from app import SECRET_KEY_USER
from app.data.models import Pupil, UserIp
from app.utils.error import Error
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
cipher = Fernet(SECRET_KEY_USER)


def _get_paths():
    """
    Returns (container_babirusa, host_babirusa).

    container_babirusa — path as seen inside the backend container (used for
        file operations like copy / makedirs that happen in THIS process).
    host_babirusa — the same directory but expressed as a HOST path so the
        Docker daemon (which runs on the host) can set up bind-mounts for the
        child codeserver containers.

    The backend container is started with:
        volumes:
          - ./backend:/app                          # host→container
          - /var/run/docker.sock:/var/run/docker.sock

    So inside the container  /app/babirusa  corresponds to
       on the host           <project_root>/backend/babirusa

    HOST_BACKEND_PATH must be set in docker-compose.yml / .env to the
    *absolute host path* of the backend directory, e.g.
        HOST_BACKEND_PATH=/home/deploy/babirusa.space/backend
    """
    # --- container-local path (always /app/babirusa when running in Docker) ---
    container_babirusa = os.path.normpath(
        os.path.join(dir_path, "..", "..", "..", "babirusa")
    )

    # --- host path (what the Docker daemon sees) ---
    host_backend = os.getenv("HOST_BACKEND_PATH", "").strip()
    if host_backend:
        host_babirusa = os.path.normpath(os.path.join(host_backend, "babirusa"))
    else:
        # Fallback: assume we are NOT inside a container (local dev).
        # In that case container path == host path.
        host_babirusa = container_babirusa
        logger.warning(
            "HOST_BACKEND_PATH is not set — assuming local (non-Docker) execution. "
            "Volume bind-mounts will use container-internal paths which will NOT work "
            "when the backend itself runs inside Docker."
        )

    return container_babirusa, host_babirusa


async def launch_codespace(username: str, password: str) -> Optional[str]:
    user = await Pupil.find_one(Pupil.username == username)
    if user and password == (
        cipher.decrypt(user.hashed_password.encode("utf-8")).decode("utf-8")
    ):
        client = docker.from_env()

        container_babirusa, host_babirusa = _get_paths()

        logger.info(
            "Codespace paths — container: %s, host: %s",
            container_babirusa,
            host_babirusa,
        )

        ex_userip = await UserIp.find_one(UserIp.username == username)

        if ex_userip:
            return str(ex_userip.ip)
        else:
            # ---- ensure base directories exist (inside container) ----
            baseconfig_path = os.path.join(container_babirusa, "baseconfig")
            baseprj_path = os.path.join(container_babirusa, "baseprj")

            os.makedirs(baseconfig_path, exist_ok=True)
            os.makedirs(baseprj_path, exist_ok=True)

            # ---- per-user directories (container paths for file-ops) ----
            user_config_container = os.path.join(
                container_babirusa, f"user-{username}-config"
            )
            user_prj_container = os.path.join(
                container_babirusa, f"user-{username}-prj"
            )

            # Copy base templates if user dirs don't exist yet
            if not os.path.exists(user_config_container) or not os.path.exists(
                user_prj_container
            ):
                if os.path.exists(baseconfig_path):
                    try:
                        copy_tree(baseconfig_path, user_config_container)
                    except Exception:
                        os.makedirs(user_config_container, exist_ok=True)

                if os.path.exists(baseprj_path):
                    try:
                        copy_tree(baseprj_path, user_prj_container)
                    except Exception:
                        os.makedirs(user_prj_container, exist_ok=True)

            # Ensure directories exist even if copy_tree was skipped
            os.makedirs(user_config_container, exist_ok=True)
            os.makedirs(user_prj_container, exist_ok=True)

            # ---- ensure main.py is in the USER's project dir ----
            base_main = os.path.join(baseprj_path, "main.py")
            user_main = os.path.join(user_prj_container, "main.py")

            if os.path.exists(base_main) and not os.path.exists(user_main):
                shutil.copy2(base_main, user_main)
                logger.info("Copied main.py → %s", user_main)

            # ---- HOST paths for Docker bind-mounts ----
            host_user_config = os.path.normpath(
                os.path.join(host_babirusa, f"user-{username}-config")
            )
            host_user_prj = os.path.normpath(
                os.path.join(host_babirusa, f"user-{username}-prj")
            )

            logger.info(
                "Volume mounts (host paths) — config: %s, prj: %s",
                host_user_config,
                host_user_prj,
            )

            # ---- pull / verify image ----
            image_name = os.getenv("CODESPACE_IMAGE", "skfx/babirusa-codeserver")
            try:
                client.images.get(image_name)
            except docker.errors.ImageNotFound:
                logger.info("Image %s not found locally, pulling…", image_name)
                client.images.pull(image_name)

            # ---- start container with HOST paths in volumes ----
            new_container = client.containers.run(
                image_name,
                detach=True,
                user=0,
                command=[
                    "--disable-telemetry",
                    "--disable-update-check",
                    "--log=debug",
                    "/home/coder/prj",
                ],
                hostname="0.0.0.0",
                volumes={
                    host_user_config: {
                        "bind": "/home/coder/.config",
                        "mode": "rw",
                    },
                    host_user_prj: {
                        "bind": "/home/coder/prj",
                        "mode": "rw",
                    },
                },
                environment={
                    "XDG_DATA_HOME": "/home/coder/.config",
                    "PASSWORD": password,
                },
                mem_limit="512m",
                mem_reservation="256m",
                nano_cpus=500000000,
                cpu_shares=512,
            ).id

            # ---- resolve container IP on the bridge network ----
            network = client.networks.get("bridge").attrs

            for cid, payload in network["Containers"].items():
                if new_container == cid:
                    ip_address = payload["IPv4Address"].split("/")[0]
                    logger.info("Found IP address: %s", ip_address)
                    userport = UserIp(
                        username=username,
                        ip=ip_address,
                        container_id=new_container,
                    )
                    logger.info("Creating UserIp entry for user %s", username)
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
        try:
            status = client.containers.get(userip.container_id).status.lower()
        except docker.errors.NotFound:
            status = "removed"
        except Exception:
            status = "unknown"

        if pupil.container_status != status:
            pupil.container_status = status
            await pupil.save()
        pupils.append(pupil)

    return pupils
