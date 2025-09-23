from __future__ import annotations
from typing import Tuple

from deployman.connectors.base import Connector
from deployman.models import Service
from deployman.storage import ConfigRepository


class ComposeDeployer:
    def __init__(self, repo: ConfigRepository | None = None) -> None:
        self.repo = repo or ConfigRepository()

    def deploy(self, service: Service, connection: Connector, start: bool = True) -> Tuple[bool, str]:
        # Upload files (compose, env, extras)
        connection.put_file(service.compose.compose_file, service.compose.compose_target_file, 0o644)

        for file in service.compose.additional_files:
            connection.put_file(file.src, file.dest, int(file.mode, 8))

        # Ensure volumes exist
        # for v in service.compose.volumes:
        #     connection.exec(f"mkdir -p {v.path}")

        # Optional pre-backup (before restart)
        # if service.backup.enabled and service.backup.include_paths:
        #     ts = int(time.time())
        #     backup_dir = service.backup.backup_dir.rstrip('/') + f"/{service.name}"
        #     connection.exec(f"mkdir -p {backup_dir}")
        #     tar_cmd = (
        #         "tar -czf "
        #         f"{backup_dir}/{service.name}-{ts}.tar.gz "
        #         + " ".join(service.backup.include_paths)
        #     )
        #     code, out, err = connection.exec(tar_cmd)
        #     if code != 0:
        #         return False, f"Backup failed: {err or out}"

        pull_cmd = f"docker compose -p {service.name} -f {service.compose.compose_target_file} pull"
        up_cmd = f"docker compose -p {service.name} -f {service.compose.compose_target_file} up -d"
        # if not start:
        #     # still pull images for later start
        #     connection.exec(pull_cmd)
        #     return True, f"Uploaded files and pulled images for '{service.name}' on {target_name}"

        code, out, err = connection.exec(pull_cmd)
        if code != 0:
            return False, f"Compose pull failed: {err or out}"
        code, out, err = connection.exec(up_cmd)
        if code != 0:
            return False, f"Compose up failed: {err or out}"

        # Monitoring: run healthcheck if configured
        # if service.monitoring.enabled and service.monitoring.healthcheck_cmd:
        #     code, out, err = connection.exec(service.monitoring.healthcheck_cmd)
        #     if code != 0:
        #         return False, f"Healthcheck failed: {err or out}"

        return True, f"Service '{service.name}' deployed to {connection.t.name}"
