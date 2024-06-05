# K8s Secrets Extractor

This script extracts all Kubernetes secrets from a specified context and namespace, and prints them as plain text. It allows you to specify the kubeconfig file, Kubernetes context, and namespace to use. Secrets containing the keyword 'helm' are excluded.

## Prerequisites

- Python 3.x
- Kubernetes Python client library (`kubernetes`)

You can install the Kubernetes Python client library using pip:

```bash
pip install kubernetes
```

## Usage

```bash
python extract-k8s-secrets.py [--kubeconfig KUBECONFIG] [--context CONTEXT] [--namespace NAMESPACE]
```

## Examples

```bash
python extract-k8s-secrets.py
python extract-k8s-secrets.py --kubeconfig /path/to/kubeconfig
python extract-k8s-secrets.py --namespace my-namespace
python extract-k8s-secrets.py --kubeconfig /path/to/kubeconfig --context my-context --namespace my-namespace
```  
