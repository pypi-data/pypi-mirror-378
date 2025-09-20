import logging
from dataclasses import dataclass
from typing import Dict

from mlox.service import AbstractService, tls_setup
from mlox.remote import exec_command, fs_create_dir, fs_delete_dir, fs_copy

logger = logging.getLogger(__name__)


@dataclass
class K8sHeadlampService(AbstractService):
    namespace: str = "kube-system"
    service_name: str = "my-headlamp"

    def get_login_token(self, bundle) -> str:
        token = ""
        with bundle.server.get_server_connection() as conn:
            token = exec_command(
                conn,
                f"kubectl create token {self.service_name} --namespace {self.namespace}",
                sudo=True,
            )
        return token

    def setup(self, conn) -> None:
        logger.info("🔧 Installing K8s Headlamp")

        kubeconfig: str = "/etc/rancher/k3s/k3s.yaml"
        src_url = f"https://kubernetes-sigs.github.io/headlamp/"

        # Add kubernetes-dashboard repository
        exec_command(
            conn,
            f"helm repo add headlamp {src_url} --kubeconfig {kubeconfig}",
            sudo=True,
        )
        # Deploy a Helm Release named "kubernetes-dashboard" using the kubernetes-dashboard chart
        exec_command(
            conn,
            f"helm upgrade --install {self.service_name} headlamp/headlamp --create-namespace --namespace {self.namespace} --kubeconfig {kubeconfig}",
            sudo=True,
        )
        node_ip, service_port = self.expose_dashboard_nodeport(conn)
        self.service_urls["Headlamp"] = f"http://{node_ip}:{service_port}"
        self.state = "running"

    def expose_dashboard_nodeport(
        self,
        conn,
        node_port=32001,
    ):
        """
        Converts the Dashboard Service to NodePort and returns (node_ip, node_port).
        """
        # 1) Patch the Service to add a name to the port, which is required.
        patch = (
            f"kubectl -n {self.namespace} patch svc {self.service_name} "
            # f"--type='merge'"
            f'-p \'{{"spec":{{"type":"NodePort","ports":[{{'
            f'"name":"plain-http","port":8080,"targetPort":4466,"nodePort":{node_port}'
            f"}}]}}}}'"
        )
        exec_command(conn, patch, sudo=True)
        node_ip = conn.host

        logger.info(f"Dashboard exposed at http://{node_ip}:{node_port}")
        return node_ip, node_port

    def spin_up(self, conn) -> bool:
        logger.info("🔄 no spinning up...")
        return True

    def spin_down(self, conn) -> bool:
        logger.info("🔄 no spinning down...")
        return True

    def teardown(self, conn):
        """
        Tear down the Kubernetes Dashboard and all related RBAC/namespace.
        """
        logger.info("🗑️ Uninstalling Headlamp")
        cmds = [
            f"kubectl delete deployment {self.service_name} -n {self.namespace} --ignore-not-found || true",
            f"kubectl delete service {self.service_name} -n {self.namespace} --ignore-not-found || true",
            f"kubectl delete svc {self.service_name} -n {self.namespace} --ignore-not-found || true",
        ]

        for cmd in cmds:
            logger.debug(f"Running: {cmd}")
            exec_command(conn, cmd, sudo=True)

        logger.info("✅ Headlamp uninstall complete")
        self.state = "un-initialized"

    def check(self, conn) -> Dict:
        return dict()
