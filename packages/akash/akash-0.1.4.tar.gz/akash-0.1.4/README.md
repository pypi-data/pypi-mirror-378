# Akash Python SDK

Python SDK for interacting with the Akash Network blockchain and deploying workloads on the decentralized cloud
marketplace.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-akash--py.cosmosrescue.com-blue.svg)](https://akash-py.cosmosrescue.com/)

## Installation

```bash
pip install akash
```

### Prerequisites

- Python 3.8+

## Quick start

### Setup

```python
from akash import AkashClient, AkashWallet

wallet = AkashWallet.from_mnemonic("your twelve word mnemonic phrase here")
print(f"Wallet address: {wallet.address}")

client = AkashClient("https://akash-rpc.polkachu.com:443")
print(f"Connected: {client.health_check()}")
```

### Send tokens

```python
from akash import AkashClient, AkashWallet

client = AkashClient("https://akash-rpc.polkachu.com:443")
wallet = AkashWallet.from_mnemonic("your mnemonic here")

result = client.bank.send(
    wallet=wallet,
    to_address="akash1recipient_address",
    amount="1000000",
    memo=""
)

if result.success:
    print(f"Transfer successful: {result.tx_hash}")
else:
    print(f"Transfer failed: {result.raw_log}")
```

### Vote on governance proposal

```python
from akash import AkashClient, AkashWallet

client = AkashClient("https://akash-rpc.polkachu.com:443")
wallet = AkashWallet.from_mnemonic("your mnemonic here")

result = client.governance.vote(
    wallet=wallet,
    proposal_id=42,
    option="YES"
)

if result.success:
    print(f"Vote successful: {result.tx_hash}")
else:
    print(f"Vote failed: {result.raw_log}")
```

### Deploy application

```python
from akash import AkashClient, AkashWallet
import time

wallet = AkashWallet.from_mnemonic("your mnemonic here")
client = AkashClient("https://akash-rpc.polkachu.com:443")

print("Step 1: Creating certificate for mTLS...")
client.cert.create_certificate(wallet)

print("Step 2: Creating deployment...")
groups = [{
    'name': 'web',
    'resources': [{
        'cpu': '500',
        'memory': '134217728',
        'storage': '1073741824',
        'price': '100',
        'count': 1
    }]
}]

deployment_result = client.deployment.create_deployment(
    wallet=wallet,
    groups=groups,
    deposit="5000000"
)
print(f"Deployment created: {deployment_result.tx_hash}")

dseq = deployment_result.get_dseq()
print(f"Deployment DSEQ: {dseq}")

print("Step 3: Waiting for bids...")
time.sleep(30)

bids = client.market.get_bids(dseq=dseq)
if not bids:
    print("No bids received")
    exit()

best_bid = min(bids, key=lambda b: int(b['bid']['price']['amount']))
provider = best_bid['bid']['bid_id']['provider']
print(f"Best bid from provider: {provider}")

print("Step 4: Creating lease...")
lease_result = client.market.create_lease(
    wallet=wallet,
    bid_id=best_bid['bid']['bid_id']
)
print(f"Lease created: {lease_result.tx_hash}")

providers = client.provider.get_providers()
provider_info = next(p for p in providers if p['owner'] == provider)
provider_endpoint = provider_info['host_uri']

print("Step 5: Submitting manifest...")
manifest = {
    "version": "2.0",
    "services": {
        "web": {
            "image": "nginx:latest",
            "expose": [
                {
                    "port": 80,
                    "as": 80,
                    "to": [{"global": True}]
                }
            ]
        }
    },
    "profiles": {
        "compute": {
            "web": {
                "resources": {
                    "cpu": {"units": 0.5},
                    "memory": {"quantity": {"val": "128Mi"}},
                    "storage": {"quantity": {"val": "1Gi"}}
                }
            }
        },
        "placement": {
            "akash": {
                "pricing": {
                    "web": {"denom": "uakt", "amount": "100"}
                }
            }
        }
    },
    "deployment": {
        "web": {"akash": {"profile": "web", "count": 1}}
    }
}

lease_id = {
    "owner": wallet.address,
    "dseq": dseq,
    "gseq": 1,
    "oseq": 1,
    "provider": provider
}

manifest_result = client.deployment.submit_manifest_to_provider(
    provider_endpoint=provider_endpoint,
    lease_id=lease_id,
    manifest=manifest
)

if manifest_result["status"] == "success":
    print("Manifest submitted successfully")
    print("Your nginx application is now running")
else:
    print(f"Manifest submission failed: {manifest_result['error']}")
```

### Provider discovery

```python
from akash import AkashClient

client = AkashClient("https://akash-rpc.polkachu.com:443")

all_providers = client.provider.get_providers()
gpu_providers = client.provider.get_providers_by_capabilities(["gpu"])
high_perf_providers = client.provider.get_providers_by_capabilities(["high-performance"])
us_providers = client.provider.get_providers_by_region("us-west")

if all_providers:
    provider_detail = client.provider.get_provider(all_providers[0]['owner'])
    print(f"Provider: {provider_detail['host_uri']}")

print(f"Total: {len(all_providers)}, GPU: {len(gpu_providers)}")
print(f"High Performance: {len(high_perf_providers)}, US West: {len(us_providers)}")
```

### Market operations

```python
from akash import AkashClient, AkashWallet

client = AkashClient("https://akash-rpc.polkachu.com:443")
wallet = AkashWallet.from_mnemonic("provider mnemonic here")

bids = client.market.get_bids(state="open", limit=20)
print(f"Found {len(bids)} open bids")

bid = client.market.create_bid(
    deployment_owner="akash1...",
    deployment_dseq=123,
    group_gseq=1,
    order_oseq=1,
    provider=wallet.address,
    price_amount=1000,
    price_denom="uakt"
)

leases = client.market.get_leases(provider=wallet.address)
print(f"Active leases: {len(leases)}")
```

## Core components

### AkashClient

Main entry point for the SDK. Manages RPC connections and provides access to all functionality.

```python
from akash import AkashClient

client = AkashClient("https://akash-rpc.polkachu.com:443")

with AkashClient("https://akash-rpc.polkachu.com:443") as client:
    deployments = client.deployment.get_deployments()
```

### AkashWallet

Handles wallet operations, key management, and transaction signing.

```python
from akash import AkashWallet

wallet = AkashWallet.generate()
print(f"New wallet: {wallet.address}")
print(f"Mnemonic: {wallet.mnemonic}")

wallet = AkashWallet.from_mnemonic("your mnemonic phrase")

wallet = AkashWallet.from_private_key(private_key_bytes)

signed_tx = wallet.sign_transaction(tx_data)
balance = wallet.get_balance()
```

### Sub-clients

The client provides access to all Akash modules:

- **audit**: Provider audit operations
- **auth**: Authentication operations
- **authz**: Authorization operations
- **bank**: Token transfers and balance queries
- **cert**: Certificate management
- **deployment**: Deployment lifecycle management
- **discovery**: Service discovery operations
- **distribution**: Staking rewards distribution
- **escrow**: Escrow account management
- **evidence**: Evidence of misbehavior submission
- **feegrant**: Fee grant operations
- **governance**: Governance proposals and voting
- **ibc**: Inter-blockchain communication
- **inflation**: Inflation parameter queries
- **inventory**: Hardware inventory management
- **manifest**: Deployment manifest operations
- **market**: Bidding and lease operations
- **provider**: Provider discovery and filtering
- **slashing**: Validator slashing operations
- **staking**: Validator staking operations

## Network endpoints

**Testnet:**

- RPC: `https://rpc.sandbox-01.aksh.pw:443`
- Chain ID: `sandbox-01`

**Mainnet:**

- RPC: `https://akash-rpc.polkachu.com:443`
- Chain ID: `akashnet-2`

## Links

- [This SDK documentation](https://akash-py.cosmosrescue.com/)
- [Akash documentation](https://docs.akash.network/)
- [SDL specification](https://docs.akash.network/sdl)
