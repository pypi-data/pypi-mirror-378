import streamlit as st

from typing import Dict

from mlox.config import ServiceConfig
from mlox.infra import Infrastructure, Bundle
from mlox.servers.ubuntu.k3s import UbuntuK3sServer
from mlox.servers.ubuntu.ui_native import setup as setup_native
from mlox.servers.ubuntu.ui_native import settings as settings_native


def setup(infra: Infrastructure, config: ServiceConfig) -> Dict:
    params = setup_native(infra, config)

    controller_url = ""
    controller_token = ""
    controller_uuid = ""

    k8s_controller = [None] + infra.list_kubernetes_controller()
    join_k8s_bundle = st.selectbox(
        "Create new Kubernetes cluster or select existing controller to join",
        k8s_controller,
        format_func=lambda x: "Create new cluster" if not x else x.name,
    )

    if join_k8s_bundle:
        controller_url = f"https://{join_k8s_bundle.server.ip}:6443"
        controller_token = join_k8s_bundle.server.get_backend_status().get(
            "k3s.token", ""
        )
        controller_uuid = join_k8s_bundle.server.uuid

    params["${K3S_CONTROLLER_URL}"] = controller_url
    params["${K3S_CONTROLLER_TOKEN}"] = controller_token
    params["${K3S_CONTROLLER_UUID}"] = controller_uuid

    return params


def settings(infra: Infrastructure, bundle: Bundle, server: UbuntuK3sServer):
    with st.expander("Kubernetes Config"):
        st.markdown(
            "You can use the following command to access the Kubernetes cluster:"
        )
        st.code(
            f"export KUBECONFIG={server.kubeconfig_path}\nkubectl get nodes",
            language="bash",
        )
        # kubectl apply
        kubectl_yaml = st.text_area("kubectl config", height=400)
        if st.button("Apply config YAML", type="primary", icon="🚀", disabled=True):
            # server.apply_yaml(kubectl_yaml)
            st.info("YAML applied.")
    settings_native(infra, bundle, server)
