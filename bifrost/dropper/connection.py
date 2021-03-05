import asyncio
import logging
from os.path import basename
from tempfile import TemporaryFile
from urllib.parse import urlsplit

import requests
from django.core.files import File
from python_graphql_client import GraphqlClient

from ..models import BifrostFile
from ..settings import (
    BIFROST_DROPPER_ENDPOINT,
    BIFROST_DROPPER_HEIMDALL_LICENSE,
    BIFROST_DROPPER_SOCKET_ENDPOINT,
)
from .exceptions import SettingEntryNotFound

logger = logging.getLogger(__name__)

RECONNECT_TIMEOUT = 5

if not BIFROST_DROPPER_ENDPOINT:
    raise SettingEntryNotFound(
        f"BIFROST_DROPPER_ENDPOINT not set. Check your project settings"
    )

if not BIFROST_DROPPER_SOCKET_ENDPOINT:
    raise SettingEntryNotFound(
        f"BIFROST_DROPPER_ENDPOINT not set. Check your project settings"
    )

if not BIFROST_DROPPER_HEIMDALL_LICENSE:
    raise SettingEntryNotFound(
        f"BIFROST_DROPPER_HEIMDALL_LICENSE not set. Check your project settings"
    )


def download_to_file_field(url, field):
    with TemporaryFile() as tf:
        r = requests.get(url, stream=True)
        for chunk in r.iter_content(chunk_size=4096):
            tf.write(chunk)

        tf.seek(0)
        field.save(basename(urlsplit(url).path), File(tf))


def download_file(url):
    r = requests.get(url, allow_redirects=True)

    with open("bridge-drop.tgz", "wb") as file:
        file.write(r.content)

        private_file = BifrostFile.objects.get_or_create(file__name=file.name)

        private_file.file.save(file.name, File(file))
        return private_file


def authenticate():
    client = GraphqlClient(endpoint=BIFROST_DROPPER_ENDPOINT)
    query = """
				mutation tokenAuth($username: String!, $password: String!) {
						tokenAuth(username: $username, password: $password) {
								token
								refreshToken
								user {
										username
								}
						}
				}
	"""

    variables = {"username": "cisco", "password": "ciscocisco"}

    result = client.execute(query=query, variables=variables)

    try:
        return result["data"]["tokenAuth"]["token"]
    except KeyError as ex:
        logger.error(f"Unable to authenticate to {BIFROST_DROPPER_ENDPOINT}: {str(ex)}")
        raise ex


async def connect():
    try:
        client = GraphqlClient(endpoint=BIFROST_DROPPER_SOCKET_ENDPOINT)

        query = """
                subscription onNewHeimdallGeneration($licenseKey: ID!) {
                    onNewHeimdallGeneration(licenseKey: $licenseKey) {
                        state
                        url
                        taskId
                    }
                }
            """

        variables = {"licenseKey": BIFROST_DROPPER_HEIMDALL_LICENSE}

        async def subscription_handle(data):
            from .schema import OnNewDropperHeimdallGeneration

            if "errors" in data:
                logger.error(data["errors"])

            state = data["data"]["onNewHeimdallGeneration"]["state"]
            url = data["data"]["onNewHeimdallGeneration"]["url"]
            task_id = data["data"]["onNewHeimdallGeneration"]["taskId"]

            if url:
                private_file = BifrostFile()
                download_to_file_field(url, private_file.file)
                url = private_file.get_download_url()

            # Processed `f5f27e3b-e5a2-41d8-9447-b3d3d214d278`(SUCCESS) -> http://localhost:8000/...
            logger.info(f"Processed `{task_id}`({state})` -> {url}")
            await OnNewDropperHeimdallGeneration.new_dropper_heimdall_generation(
                state, url
            )

        def subscription_callback(data):
            loop = asyncio.get_event_loop()
            loop.create_task(subscription_handle(data))

        await client.subscribe(
            query=query, variables=variables, handle=subscription_callback
        )

    except Exception as ex:
        logger.error(
            f"Unable to connect to {BIFROST_DROPPER_SOCKET_ENDPOINT}: {str(ex)}"
        )
        logger.info(
            f"Reconnecting to {BIFROST_DROPPER_SOCKET_ENDPOINT} in {RECONNECT_TIMEOUT}s"
        )

        await asyncio.sleep(RECONNECT_TIMEOUT)
        await connect()
