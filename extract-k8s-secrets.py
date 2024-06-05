import argparse
import base64
import os
import yaml
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

def load_kube_config(kubeconfig, context=None):
    try:
        with open(kubeconfig, 'r') as f:
            kube_config = yaml.safe_load(f)
        config.load_kube_config(config_file=kubeconfig, context=context)
        print("Kubeconfig loaded successfully.")
        print("Current context:", kube_config.get('current-context', 'None'))
        print("Available contexts:", [ctx['name'] for ctx in kube_config.get('contexts', [])])
    except FileNotFoundError:
        print(f"Kube config file not found: {kubeconfig}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing kube config file: {e}")
        exit(1)
    except ConfigException as e:
        print(f"Failed to load kube config: {e}")
        print("Please ensure that the kubeconfig file is correctly set up and contains the necessary context information.")
        print("Available contexts in kubeconfig file:")
        with open(kubeconfig, 'r') as f:
            kube_config = yaml.safe_load(f)
            for ctx in kube_config.get('contexts', []):
                print(f" - {ctx['name']}")
        exit(1)

def get_secrets(namespace=None):
    v1 = client.CoreV1Api()
    try:
        if namespace:
            secrets = v1.list_namespaced_secret(namespace, watch=False)
        else:
            secrets = v1.list_secret_for_all_namespaces(watch=False)
        return secrets.items
    except Exception as e:
        print(f"Failed to list secrets: {e}")
        exit(1)

def decode_secret_data(secret_data):
    decoded_data = {}
    if secret_data is not None:
        for key, value in secret_data.items():
            try:
                decoded_data[key] = base64.b64decode(value).decode('utf-8')
            except Exception as e:
                print(f"Failed to decode secret {key}: {e}")
                decoded_data[key] = "Decoding error"
    return decoded_data

def prettify_output(namespace, name, decoded_data):
    print(f"Namespace: {namespace}\nName: {name}")
    print("Data:")
    for key, value in decoded_data.items():
        print(f"  {key}: {value}")
    print("-" * 40)

def print_usage():
    usage_text = """
    Usage: python script_name.py [--kubeconfig KUBECONFIG] [--context CONTEXT] [--namespace NAMESPACE]

    Options:
      --kubeconfig KUBECONFIG Path to the kubeconfig file (default: ~/.kube/config)
      --context CONTEXT       Kubernetes context to use (default: current context)
      --namespace NAMESPACE   Kubernetes namespace to get secrets from (default: all namespaces)

    Example:
      python script_name.py
      python script_name.py --kubeconfig /path/to/kubeconfig
      python script_name.py --context my-context
      python script_name.py --namespace my-namespace
      python script_name.py --kubeconfig /path/to/kubeconfig --context my-context --namespace my-namespace
    """
    print(usage_text)

def main():
    parser = argparse.ArgumentParser(description='Extract all K8s secrets and print as plain text')
    parser.add_argument('--kubeconfig', type=str, default=os.path.expanduser("~/.kube/config"),
                        help='Path to the kubeconfig file (default: ~/.kube/config)')
    parser.add_argument('--context', type=str, help='Kubernetes context to use')
    parser.add_argument('--namespace', type=str, help='Kubernetes namespace to use')
    args = parser.parse_args()

    if not args.context and not args.namespace:
        print_usage()

    load_kube_config(kubeconfig=args.kubeconfig, context=args.context)

    secrets = get_secrets(namespace=args.namespace)
    for secret in secrets:
        if 'helm' in secret.metadata.name.lower():
            continue  # Exclude secrets containing 'helm'
        
        decoded_data = decode_secret_data(secret.data)
        prettify_output(secret.metadata.namespace, secret.metadata.name, decoded_data)

if __name__ == "__main__":
    main()

