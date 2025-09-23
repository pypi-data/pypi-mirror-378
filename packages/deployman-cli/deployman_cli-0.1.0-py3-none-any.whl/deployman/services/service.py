from pathlib import Path
import yaml
from deployman.models import Service


class ServiceLoader:
    """Utility class to load service specifications from YAML files."""

    @staticmethod
    def load_service(service_file: str) -> Service:
        data = yaml.safe_load(Path(service_file).read_text(encoding="utf-8"))

        service = Service.model_validate(data)

        if service.method == "compose":
            service_dir = Path(service_file).parent
            _service_target_dir = Path(service.base_dir, service.name)
            service.compose.compose_file = str(Path(service_dir, service.compose.compose_file))
            service.compose.compose_target_file = str(Path(_service_target_dir, service.compose.compose_target_file))
            for af in service.compose.additional_files:
                af.dest = af.dest or af.src
                af.src = str(Path(service_dir, af.src))
                af.dest = str(Path(_service_target_dir, af.dest))

            for path in service.backup.paths:
                path.path = str(Path(_service_target_dir, path.path))
                path.include = [str(Path(path.path, p)) for p in path.include]
                path.exclude = [str(Path(path.path, p)) for p in path.exclude]

        return service
