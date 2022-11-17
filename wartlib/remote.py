import shutil

from fabric import Connection


def publish_file(local_path, server, user, remote_path):
    if server == "localhost":
        shutil.copy(local_path, remote_path)
    else:
        connection = Connection(host=server, user=user)
        connection.put(local_path, remote_path, preserve_mode=False)
