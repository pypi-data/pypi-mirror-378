import logging

from dataclasses import dataclass, field
from typing import Dict, Any

from mlox.service import AbstractService, tls_setup
from mlox.remote import (
    fs_copy,
    fs_read_file,
    fs_touch,
    fs_delete_dir,
    fs_create_dir,
    fs_create_empty_file,
    fs_find_and_replace,
    fs_append_line,
    docker_down,
    exec_command,
    docker_service_state,
)

# Configure logging (optional, but recommended)
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@dataclass
class OtelDockerService(AbstractService):
    relic_endpoint: str
    relic_key: str
    config: str
    port_grpc: str | int
    port_http: str | int
    port_health: str | int
    service_url: str = field(init=False, default="")

    def get_telemetry_data(self, bundle) -> Any:
        with bundle.server.get_server_connection() as conn:
            data = fs_read_file(
                conn, f"{self.target_path}/otel-data/telemetry.json", format="txt/plain"
            )
        return data

    def setup(self, conn) -> None:
        fs_create_dir(conn, self.target_path)
        fs_create_dir(conn, f"{self.target_path}/otel-data")
        fs_touch(conn, f"{self.target_path}/otel-data/telemetry.json")
        exec_command(conn, f"chmod 777 {self.target_path}/otel-data", sudo=True)
        exec_command(
            conn, f"chmod 777 {self.target_path}/otel-data/telemetry.json", sudo=True
        )

        fs_copy(conn, self.template, f"{self.target_path}/{self.target_docker_script}")
        fs_copy(conn, self.config, f"{self.target_path}/otel-collector-config.yaml")

        if len(self.relic_key) > 4 and len(self.relic_endpoint) > 4:
            fs_find_and_replace(
                conn,
                f"{self.target_path}/otel-collector-config.yaml",
                "file]",
                "file, otlphttp]",
            )

        tls_setup(conn, conn.host, self.target_path)
        self.certificate = fs_read_file(
            conn, f"{self.target_path}/cert.pem", format="txt/plain"
        )
        # setup env file
        env_path = f"{self.target_path}/{self.target_docker_env}"
        fs_create_empty_file(conn, env_path)
        fs_append_line(conn, env_path, f"OTEL_PORT_GRPC={self.port_grpc}")
        fs_append_line(conn, env_path, f"OTEL_PORT_HTTP={self.port_http}")
        fs_append_line(conn, env_path, f"OTEL_PORT_HEALTH={self.port_health}")
        fs_append_line(conn, env_path, f"OTEL_RELIC_KEY={self.relic_key}")
        fs_append_line(conn, env_path, f"OTEL_RELIC_ENDPOINT={self.relic_endpoint}")
        self.service_url = f"https://{conn.host}:{self.port_grpc}"
        self.service_ports["OTLP gRPC receiver"] = int(self.port_grpc)
        self.service_ports["OTLP HTTP receiver"] = int(self.port_http)
        self.service_ports["OTEL health check"] = int(self.port_health)
        self.service_urls["OTLP gRPC receiver"] = (
            f"https://{conn.host}:{self.port_grpc}"
        )
        self.service_urls["OTLP HTTP receiver"] = (
            f"https://{conn.host}:{self.port_http}"
        )
        self.service_urls["OTLP health"] = f"https://{conn.host}:{self.port_health}/health/status"
        self.state = "running"

    def teardown(self, conn):
        docker_down(
            conn,
            f"{self.target_path}/{self.target_docker_script}",
            remove_volumes=True,
        )
        fs_delete_dir(conn, self.target_path)
        self.state = "un-initialized"

    def check(self, conn) -> Dict:
        docker_state = docker_service_state(conn, "otel-collector")
        status = "failed"
        if docker_state == "running":
            status = "running"
        elif docker_state in ("created", "restarting"):
            status = "starting"

        return {"status": status, "docker_state": docker_state}
