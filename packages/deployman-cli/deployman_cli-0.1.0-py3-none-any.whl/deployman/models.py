from __future__ import annotations
from typing import Optional, Literal, Set, Dict, List
from pydantic import BaseModel, Field, field_validator


class SSHSettings(BaseModel):
    host: str = Field(..., description="Hostname or IP of the target")
    port: int = Field(22, description="SSH port")
    username: Optional[str] = Field(None, description="SSH username; can be provided at runtime")
    key_path: Optional[str] = Field(None, description="Path to private key; use ssh-agent if omitted")


ConnectorType = Literal["ssh"]  # extend later: "k8s", "winrm", etc.


class Target(BaseModel):
    name: str = Field(..., description="Unique target name")
    connector: ConnectorType = Field("ssh", description="Connector type")
    tags: Set[str] = Field(default_factory=set, description="Free-form tags, e.g., {'prod','edge'}")
    ssh: Optional[SSHSettings] = Field(None, description="SSH settings when connector=ssh")

    @field_validator("ssh")
    @classmethod
    def _require_ssh_when_connector_is_ssh(cls, v, info):
        connector = info.data.get("connector")
        if connector == "ssh" and v is None:
            raise ValueError("ssh settings are required when connector='ssh'")
        return v


# ---------------------- Service & Deployment models ----------------------
DeployMethod = Literal["compose"]


class StorageVolume(BaseModel):
    name: str
    path: str = Field(..., description="Absolute path on remote host, e.g., /opt/myapp/data")
    mode: Literal["rw", "ro"] = "rw"


class BackupPath(BaseModel):
    path: str = Field(..., description="Path to include in backup, relative to service base_dir")
    include: List[str] = Field(default_factory=lambda: ["**"], description="Glob patterns to include")
    exclude: List[str] = Field(default_factory=list, description="Glob patterns to exclude")


class BackupOptions(BaseModel):
    enabled: bool = True
    method: Literal["tar"] = "tar"
    paths: List[BackupPath] = Field(default_factory=list, description="Backup paths")
    exclude_patterns: List[str] = Field(default_factory=list, description="Patterns to exclude from backup on remote host")
    backup_dir: str = Field("/opt/backups", description="Base directory for backups on remote host")


class MonitoringOptions(BaseModel):
    enabled: bool = True
    healthcheck_cmd: Optional[str] = Field(
        None,
        description="Shell command to verify service health remotely (returns 0 on success)",
    )


# class ComposeFile(BaseModel):
#     remote_path: str = Field(..., description="Where to write the compose file on the remote host")
#     content: str = Field(..., description="The docker compose YAML content")


class ExtraFile(BaseModel):
    src: str = Field(..., description="Local source path to read content from")
    dest: str = Field(None, description="Remote destination path to write content to")
    mode: str = Field("0644", description="octal string, e.g., 0644")


class ComposeSpec(BaseModel):
    compose_file: str = Field("compose.yaml", description="Filename for the compose file, e.g., compose.yaml")
    compose_target_file: str = Field("compose.yaml", description="Filename for the target compose file, e.g., compose.yaml")
    additional_files: List[ExtraFile] = Field(default_factory=list)
    env: Optional[ExtraFile] = None
    files: List[ExtraFile] = Field(default_factory=list)
    volumes: List[StorageVolume] = Field(default_factory=list)
    project_name: Optional[str] = Field(None, description="Override for compose project name")


class Service(BaseModel):
    name: str
    method: DeployMethod = "compose"
    base_dir: str = Field(..., description="Base directory on remote host for this service, e.g., /opt/myapp")
    compose: ComposeSpec
    backup: BackupOptions = Field(default_factory=BackupOptions)
    monitoring: MonitoringOptions = Field(default_factory=MonitoringOptions)


class AppConfig(BaseModel):
    version: int = 1
    targets: Dict[str, Target] = Field(default_factory=dict)
    services: Dict[str, Service] = Field(default_factory=dict)

    def ensure_unique(self, t: Target) -> None:
        if t.name in self.targets:
            raise ValueError(f"Target with name '{t.name}' already exists")
