import json
import logging
import pandas as pd
import streamlit as st

from typing import cast, Dict

from mlox.services.gcp.secret_service import GCPSecretService
from mlox.infra import Infrastructure, Bundle
from mlox.secret_manager import AbstractSecretManagerService

logger = logging.getLogger(__name__)


def setup(infra: Infrastructure, bundle: Bundle) -> dict | None:
    params: Dict = dict()

    my_secret_manager_services = infra.filter_by_group("secret-manager")
    if len(my_secret_manager_services) == 0:
        st.error("No secret manager service found in the infrastructure.")
        return params

    c1, c2 = st.columns([30, 70])
    select_secret_manager_service = c1.selectbox(
        "Select Secret Manager Service",
        my_secret_manager_services,
        format_func=lambda x: x.name,
        key="secret_manager_service",
    )
    secret_name = c2.text_input(
        "Secret Name", value="MLOX_GCP_SECRET_MANAGER_KEY", key="secret_name"
    )

    st.markdown("""
To access the secret manager, a service account with the following roles are necessary:
1. secret manager secret accessor (view and read secret contents)
2. secret manager viewer (list secrets)
3. secret manager admin (create and update secrets and versions)
            """)
    keyfile_dict = st.text_area(
        "Add the contents of your service account keyfile.json here"
    )
    is_keyfile_dict = False
    try:
        keyfile_dict = json.loads(keyfile_dict)
        is_keyfile_dict = True
    except Exception as e:  # noqa: BLE001
        st.info("Invalid JSON format. Please provide a valid JSON object. ")
        logger.warning(f"Invalid JSON format for keyfile: {e}")

    if hasattr(select_secret_manager_service, "get_secret_manager"):
        sms = cast(AbstractSecretManagerService, select_secret_manager_service)
        sm = sms.get_secret_manager(infra)
        if st.button("Save Secret", type="primary", disabled=not is_keyfile_dict):
            sm.save_secret(secret_name, keyfile_dict)

    params["${SECRET_MANAGER_UUID}"] = select_secret_manager_service.uuid
    params["${SECRET_NAME}"] = secret_name

    return params


def settings(infra: Infrastructure, bundle: Bundle, service: GCPSecretService):
    # st.header(f"Settings for service {service.name}")
    # st.write(f"UUID: {service.secret_manager_uuid}")

    sm = service.get_secret_manager(infra)
    secrets = sm.list_secrets(keys_only=True)

    df = pd.DataFrame(
        [[k, "****"] for k, v in secrets.items()], columns=["Key", "Value"]
    )
    selection = st.dataframe(
        df,
        hide_index=True,
        selection_mode="single-row",
        use_container_width=True,
        on_select="rerun",
    )
    if len(selection["selection"]["rows"]) > 0:
        idx = selection["selection"]["rows"][0]
        key = df.iloc[idx]["Key"]
        with st.container(border=True):
            st.markdown(f"### Secret: `{key}`")
            st.write("You can use this secret in your code as follows:")
            st.code(
                f"from mlox.services.gcp_secrets import GCPSecretsService\n"
                f"tsm = GCPSecretsService()\n"
                f"secret_value = tsm.load_secret('{key}')"
            )
            st.markdown("#### Value:")
            value = sm.load_secret(key)
            # Display the secret value, but mask it
            if st.toggle(
                "Tree View",
                value=False,
                disabled=not isinstance(value, Dict),
                key=f"show_secret_{key}",
            ):
                st.write(value)
            else:
                st.text_area(
                    "Value",
                    value=value,
                    height=200,
                    disabled=True,
                    key=f"secret_{key}",
                )
        # st.write(tsm.load_secret(key))

    with st.form("Add Secret"):
        name = st.text_input("Key")
        value = st.text_area("Value")
        if st.form_submit_button("Add Secret"):
            sm.save_secret(name, value)
            st.rerun()
