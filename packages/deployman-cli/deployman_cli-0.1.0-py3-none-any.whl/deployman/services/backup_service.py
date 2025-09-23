from __future__ import annotations
from fnmatch import fnmatch
from pathlib import Path
from deployman.services.targets_service import TargetsService
from deployman.storage import ConfigRepository
from deployman.connectors.base import ConnectorFactory
from deployman.services.service import ServiceLoader


class BackupService:
    def __init__(self, repo: ConfigRepository | None = None) -> None:
        self.repo = repo or ConfigRepository()

    def _get_remote_backup_files(self, connection, service):
        """
        Get list of files to backup from remote host, based on service backup paths and patterns.
        Args:
            connection: Connector instance connected to target host.
            service: Service instance with backup configuration.

        Returns:
            list of file paths on remote host to include in backup.
        """
        files = []
        for path in service.backup.paths:
            path_files = connection.list_files(path.path, recursive=True)  # noqa: E1101
            path_files = self._match_patterns(
                path_files,
                include_patterns=path.include,
                exclude_patterns=path.exclude,
            )
            files.extend(path_files)
        return files

    def _get_local_backup_files(self, service, local_path: Path):
        """
        Get list of local files to restore, based on service backup paths and patterns.
        Args:
            service: Service instance with backup configuration.
            local_base: Base local directory where backup files are stored.
        Returns:
            list of local file paths to restore.
        """
        return [f for f in local_path.glob("**/*") if f.is_file()]

    def _match_patterns(self, files, include_patterns=None, exclude_patterns=None):
        """
        Filter a list of files by include and exclude patterns.

        Args:
            files (list[str]): List of file paths.
            include_patterns (list[str]): Glob-style patterns to include.
            exclude_patterns (list[str]): Glob-style patterns to exclude.

        Returns:
            list[str]: Filtered list of files.
        """
        include_patterns = include_patterns or ["**"]  # default: include everything
        exclude_patterns = exclude_patterns or []

        def matches_any(path, patterns):
            """Return True if path matches any of the given patterns."""
            return any(fnmatch(path, pat) for pat in patterns)

        output = []
        for f in files:
            # f_norm = f.replace(os.sep, "/")  # normalize separators
            if matches_any(f, include_patterns) and not matches_any(f, exclude_patterns):
                output.append(f)
        return output

    def backup(self, *, service_file: str, target_name: str, local_path: str) -> str:
        service = ServiceLoader.load_service(service_file)
        target = TargetsService(self.repo).load_target(target_name)

        if service is None:
            return f"[red]ERROR[/red] Service file '{service_file}' could not be loaded"

        if target is None:
            return f"[red]ERROR[/red] Target '{target_name}' not found"

        connection = ConnectorFactory.create(target)

        lp = Path(local_path, service.name) if local_path else Path(service.backup.backup_dir, service.name)

        backup_files = self._get_remote_backup_files(connection, service)
        _service_target_dir = str(Path(service.base_dir, service.name))

        for backup_file in backup_files:
            remote_path = backup_file
            local_path = backup_file.replace(_service_target_dir, str(lp))
            connection.get(remote_path, local_path)

        return f"[green]SUCCESS[/green] Downloaded backup files from {target_name} to '{lp}'"

    def restore(self, *, service_file: str, target_name: str, local_path: str) -> str:
        service = ServiceLoader.load_service(service_file)
        target = TargetsService(self.repo).load_target(target_name)

        if service is None:
            return f"[red]ERROR[/red] Service file '{service_file}' could not be loaded"

        if target is None:
            return f"[red]ERROR[/red] Target '{target_name}' not found"

        connection = ConnectorFactory.create(target)
        lp = Path(local_path, service.name) if local_path else Path(service.backup.backup_dir, service.name)
        restore_files = self._get_local_backup_files(service, lp)

        for restore_file in restore_files:
            local_path = str(restore_file)
            remote_path = str(restore_file).replace(str(lp), str(Path(service.base_dir, service.name)))
            print(f"[DEBUG] Restoring local file {local_path} to remote path {remote_path}")
            connection.put(local_path, remote_path)
