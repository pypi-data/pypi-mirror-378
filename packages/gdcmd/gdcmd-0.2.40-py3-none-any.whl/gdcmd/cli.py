﻿import os
import click
from gdcmd.helm.list_charts import list_charts
from gdcmd.helm.template import template
from gdcmd.helm.validate import validate
from gdcmd.keycloak import import_realm, get_user_uuid_by_username, get_access_token, delete_user
from gdcmd.secrets import decrypt_secrets, create_new_key, encrypt_secrets


@click.group()
def cli():
    """CLI for GridDot platform tools"""
    pass


@click.group()
def keycloak():
    """Tools for managing keycloak"""
    pass


@keycloak.command("provision", short_help="Provision Keycloak with realms and users")
@click.option('--url', help='Keycloak server URL')
@click.option('--username', help='User name')
@click.option('--password', help='Username password')
@click.option('--realms-dir', help='Path to the directory with realm JSON files')
@click.option('--delete-user-when-provisioned', type=bool, default=True)
@click.option('--email-password', help='Email provider password')
def keycloak_provision(url, username, password, realms_dir, delete_user_when_provisioned, email_password):
    """Keycloak provisioning tool"""

    for realm_path in os.listdir(realms_dir):
        full_path = os.path.join(realms_dir, realm_path)
        print(f"Importing realm from {full_path}")
        import_realm(url, username, password, full_path, email_password, True)

    if str(delete_user_when_provisioned).lower() == 'yes':
        token = get_access_token(url, username, password)
        user_id = get_user_uuid_by_username(url, "master", token, username)
        delete_user(url, "master", token, user_id)
        print(f"Deleted user {username} from master realm.")


@click.group()
def secrets():
    """Tools for managing secrets"""
    pass


@secrets.command("decrypt", short_help="Decrypt secrets files using the private key .secrets/key.pem")
@click.option('--file', '-f', multiple=True, help='Path to the encrypted secrets file(s)')
def secrets_decrypt(file: tuple[str]):
    decrypt_secrets(list(file))


@secrets.command("create", short_help="Create a new RSA key pair: .secrets/key.pem and .secrets/key.pub")
def secrets_create():
    create_new_key()


@secrets.command("encrypt", short_help="Encrypt secrets files using the public key .secrets/key.pub")
@click.option('--file', '-f', multiple=True, help='Path to the secrets file(s) to encrypt')
def secrets_encrypt(file: tuple[str]):
    encrypt_secrets(list(file))


@click.group()
def helm():
    """Tools for managing deployments"""
    pass


@helm.command("list", short_help="List all deployments from helm repository")
def helm_list():
    helm_charts = list_charts()
    print("Possible deployments:")
    for chart in helm_charts:
        print(f"- {chart}")


@helm.command("template",
              short_help="Templates a Kubernetes deployment using helm for podman kube play command",
              help="You can list deployments with `griddot helm list`")
@click.argument("deployment")
@click.option('--values', '-f', multiple=True, help='Path to the values file for the helm chart')
def helm_template(deployment: str, values: tuple[str]):
    if deployment not in list_charts():
        raise click.BadParameter(f"Deployment '{deployment}' not found in helm repository. "
                                 f"Use `griddot helm list` to see available deployments.")

    for value in values:
        if not os.path.exists(value):
            raise click.BadParameter(f"Values file '{value}' does not exist.")

    templated_yaml = template(deployment, values)
    print(templated_yaml)


@helm.command("validate", short_help="Validates all the values.yaml files against the griddot/suite deployment installation")
@click.option('--values', '-f', multiple=True, help='Path to the values file for the helm chart')
def helm_validate(values: tuple[str]):
    for value in values:
        if not os.path.exists(value):
            raise click.BadParameter(f"Values file '{value}' does not exist.")

    validate(values)


cli.add_command(secrets)
cli.add_command(keycloak)
cli.add_command(helm)
