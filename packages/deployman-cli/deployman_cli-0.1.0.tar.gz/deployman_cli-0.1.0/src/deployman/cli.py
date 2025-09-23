from __future__ import annotations
from typing import Optional
import typer
from rich import print
from rich.table import Table
from deployman.services.backup_service import BackupService
from deployman.services.targets_service import TargetsService
from deployman.services.deploy_service import DeployService

app = typer.Typer(help="deployman — manage deployment targets and deployments")


def _print_targets_table(service: TargetsService) -> None:
    rows = service.list()
    table = Table(show_header=True, header_style="bold")
    table.add_column("Name", style="bold")
    table.add_column("Connector")
    table.add_column("Host")
    table.add_column("Port")
    table.add_column("User")
    table.add_column("Tags")
    for t in sorted(rows, key=lambda x: x.name):
        host = t.ssh.host if t.ssh else "-"
        port = str(t.ssh.port) if t.ssh else "-"
        user = t.ssh.username or "-" if t.ssh else "-"
        table.add_row(t.name, t.connector, host, port, user, ",".join(sorted(t.tags)))
    print(table)


targets_app = typer.Typer(help="Manage targets")
app.add_typer(targets_app, name="targets")

service_app = typer.Typer(help="Manage services")
app.add_typer(service_app, name="service")

backup_app = typer.Typer(help="Backup and restore")
app.add_typer(backup_app, name="backup")

restore_app = typer.Typer(help="Restore from backup")
app.add_typer(restore_app, name="restore")


@targets_app.command("list")
def cmd_targets_list() -> None:
    """List all configured targets."""
    service = TargetsService()
    _print_targets_table(service)


@targets_app.command("add")
def cmd_targets_add(
    name: str = typer.Option(..., help="Unique name of the target"),
    host: str = typer.Option(..., help="Hostname or IP"),
    user: Optional[str] = typer.Option(None, "--user", help="SSH username"),
    port: int = typer.Option(22, "--port", help="SSH port"),
    key_path: Optional[str] = typer.Option(None, "--key-path", help="Path to private key (optional)"),
    tags: str = typer.Option("", help="Comma-separated tags, e.g. prod,edge"),
):
    """Add a new target (SSH)."""
    service = TargetsService()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    t = service.add(name=name, tags=tag_list, host=host, port=port, username=user, key_path=key_path)
    print(f"[green]Added target[/green]: {t.name} -> {t.ssh.host}:{t.ssh.port}")


@targets_app.command("remove")
def cmd_targets_remove(name: str = typer.Option(..., help="Name of target to remove")) -> None:
    """Remove a target by name."""
    service = TargetsService()
    if service.remove(name):
        print(f"[yellow]Removed[/yellow] target: {name}")
    else:
        print(f"[red]No such target[/red]: {name}")


@targets_app.command("check")
def cmd_targets_check(
    name: Optional[str] = typer.Option(None, "--name", help="Name of a single target to check"),
    all_: bool = typer.Option(False, "--all", help="Check all targets (default if --name not provided)"),
) -> None:
    """Check reachability of one target or all targets."""
    service = TargetsService()

    results = service.check([name] if name else None)
    if not results:
        print("[yellow]No targets configured.[/yellow]")
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("Name", style="bold")
    table.add_column("Status")
    table.add_column("Message")
    for n, ok, msg in results:
        status = "OK" if ok else "FAIL"
        status_markup = f"[green]{status}[/green]" if ok else f"[red]{status}[/red]"
        table.add_row(n, status_markup, msg)
    print(table)


@service_app.command("deploy")
def cmd_service_deploy(
    service_file: str = typer.Option(..., "--service-file", help="Path to service spec YAML"),
    target: str = typer.Option(..., "--target", help="Target name to deploy to"),
) -> None:
    """Deploy a compose-based service spec to a remote target."""
    d = DeployService()
    result = d.deploy(service_file, target_name=target)
    print(result)


@service_app.command("backup")
def cmd_service_backup(
    service_file: str = typer.Option(..., "--service-file", help="Path to service spec YAML"),
    target: str = typer.Option(..., "--target", help="Target name to deploy to"),
    local_path: Optional[str] = typer.Option(None, "--local-path", help="Local destination path"),
) -> None:
    """Download a single file from the remote host to the local machine."""
    backup_service = BackupService()
    result = backup_service.backup(service_file=service_file, target_name=target, local_path=local_path)
    print(result)


@service_app.command("restore")
def cmd_service_restore(
    service_file: str = typer.Option(..., "--service-file", help="Path to service spec YAML"),
    target: str = typer.Option(..., "--target", help="Target name to deploy to"),
    local_path: Optional[str] = typer.Option(None, "--local-path", help="Local source path"),
) -> None:
    """Restore backup files from local machine to the remote host."""
    backup_service = BackupService()
    result = backup_service.restore(service_file=service_file, target_name=target, local_path=local_path)
    print(result)