import io
import shutil
import tempfile

import chevron
from fabric import Connection


def publish_file(local_path, server, user, remote_path):
    if server == "localhost":
        shutil.copy(local_path, remote_path)
    else:
        connection = Connection(host=server, user=user)
        connection.put(local_path, remote_path, preserve_mode=False)


def publish_report(local_template, data, target_filename, server, user, target_root):
    with open(
        local_template, "r"
    ) as template, tempfile.TemporaryDirectory() as d, io.open(
        f"{d}/{target_filename}", "w", encoding="utf8"
    ) as f:
        output = chevron.render(template, data)
        f.write(output)
        f.close()
        publish_file(f.name, server, user, f"{target_root}/reports/{target_filename}")
