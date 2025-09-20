# 🌐 Confidential Router (on Azure Confidential Container)

Permissionless, TEE-based routing for forwarding API calls to providers—running inside an Azure **Confidential Container**.

## Prereqs

* Azure CLI ≥ **2.44.1** and **confcom** extension (for CCE policy):

  ```bash
  az --version
  az extension add -n confcom
  ```

  ([Microsoft Learn][1])
* Docker (to build/push your image).
* jq + sha256sum (Linux/macOS tools for templating & hashing).

---

## Quick Start (step-by-step)

### 1) Build & push your image to GHCR

```bash
# build
docker build -t ghcr.io/<gh-user>/confidential-router:latest .

# (optional) login if your GHCR is private
# echo $GITHUB_TOKEN | docker login ghcr.io -u <gh-user> --password-stdin

# push
docker push ghcr.io/<gh-user>/confidential-router:latest

# pin by digest (recommended for CCE stability)
IMAGE_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/<gh-user>/confidential-router:latest)
echo "$IMAGE_DIGEST"
```

---

### 2) Login & set variables

```bash
# login (interactive) and set subscription if needed
az login
# az account set -s "<SUBSCRIPTION_ID_OR_NAME>"

# choose your names/region
GROUP=confidential-router
LOC=eastus
KV_NAME=confidential-router
MAA_NAME=crmaa
UAMI_NAME=cr-uami
CG_NAME=confrouter   # container group name
IMAGE="$IMAGE_DIGEST"  # from step 1 (digest form recommended)

# create resource group
az group create -n $GROUP -l $LOC
```

---

### 3) Create MAA (Microsoft Azure Attestation) provider

```bash
az attestation create -n $MAA_NAME -g $GROUP -l $LOC
MAA_ENDPOINT=$(az attestation show -n $MAA_NAME -g $GROUP --query 'attestUri' -o tsv)
echo "$MAA_ENDPOINT"
```

---

### 4) Create Key Vault (Premium + RBAC + purge protection)

```bash
az keyvault create \
  -n $KV_NAME -g $GROUP -l $LOC \
  --sku premium \
  --enable-rbac-authorization true \
  --enable-purge-protection true --retention-days 90

KV_ID=$(az keyvault show -n $KV_NAME -g $GROUP --query id -o tsv)
AKV_ENDPOINT="https://${KV_NAME}.vault.azure.net"
echo "$AKV_ENDPOINT"
```

---

### 5) Create a **User-Assigned Managed Identity** and assign SKR role

```bash
# UAMI
az identity create -g $GROUP -n $UAMI_NAME -l $LOC
UAMI_ID=$(az identity show -g $GROUP -n $UAMI_NAME --query id -o tsv)
UAMI_PRINCIPAL_ID=$(az identity show -g $GROUP -n $UAMI_NAME --query principalId -o tsv)

# Your own admin access (optional but handy)
ME=$(az ad signed-in-user show --query id -o tsv)
az role assignment create --role "Key Vault Administrator" --assignee-object-id $ME --assignee-principal-type User --scope $KV_ID

# **Grant the identity SKR permission** (release action)
az role assignment create \
  --assignee-object-id $UAMI_PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --role "Key Vault Crypto Service Release User" \
  --scope $KV_ID
```

---

### 6) Prepare the ARM template

Copy your base template and set **image** + **identity** + **env vars** + **sidecar**:

```bash
cp templates/template.base.json templates/template.private.json
```

Minimal deltas you need inside `templates/template.private.json`:

```json
{
  "type": "Microsoft.ContainerInstance/containerGroups",
  "apiVersion": "2023-05-01",
  "name": "<CG_NAME>",
  "location": "<REGION>",
  "identity": {
    "type": "UserAssigned",
    "userAssignedIdentities": {
      "<UAMI_ID>": {}
    }
  },
  "properties": {
    "sku": "Confidential",
    "confidentialComputeProperties": { "ccePolicy": "" },
    "osType": "Linux",
    "containers": [
      {
        "name": "router-container",
        "properties": {
          "image": "<YOUR_IMAGE_DIGEST>",
          "environmentVariables": [
            {"name":"AKV_ENDPOINT","value":"https://<kv-name>.vault.azure.net"},
            {"name":"MAA_ENDPOINT","value":"https://<maa-name>.<region>.attest.azure.net"},
            {"name":"KID","value":"default"},
            {"name":"OPENAI_API_KEY","value":"sk-proj-..."},
            {"name":"OPENROUTER_API_KEY","value":"sk-or-v1..."},
            {"name":"FAL_KEY","value":"4e101177-..."}
          ],
          "ports":[{"port":8080,"protocol":"TCP"}],
          "resources":{"requests":{"cpu":2,"memoryInGB":4}}
        }
      },
      {
        "name": "skr-sidecar-container",
        "properties": {
          "image": "mcr.microsoft.com/aci/skr:2.12",
          "ports":[{"port":8081,"protocol":"TCP"}],
          "resources":{"requests":{"cpu":1,"memoryInGB":1}}
        }
      }
    ],
    "ipAddress": { "type": "Public", "ports": [ {"port":8080,"protocol":"TCP"} ] },
    "restartPolicy": "Always"
  }
}
```

---

### 7) Generate the **CCE policy** (fills template)

```bash
az confcom acipolicygen --template-file templates/template.private.json
# This injects a Base64 CCE policy into .resources[0].properties.confidentialComputeProperties.ccePolicy
```
---

### 8) Compute **CCE hash** and write `skr-policy.json`

```bash
CCE_B64=$(jq -r '.resources[0].properties.confidentialComputeProperties.ccePolicy' templates/template.private.json)
CCE_HASH=$(echo -n "$CCE_B64" | base64 -d | sha256sum | awk '{print $1}')
echo "CCE_HASH = $CCE_HASH"

cat > skr-policy.json <<EOF
{
  "version": "1.0.0",
  "anyOf": [
    {
      "authority": "$MAA_ENDPOINT",
      "allOf": [
        { "claim": "x-ms-attestation-type", "equals": "sevsnpvm" },
        { "claim": "x-ms-compliance-status", "equals": "azure-compliant-uvm" },
        { "claim": "x-ms-sevsnpvm-hostdata", "equals": "$CCE_HASH" }
      ]
    }
  ]
}
EOF
```

---

### 9) Create an **exportable** HSM key with SKR policy

```bash
az keyvault key create \
  --vault-name $KV_NAME \
  --name default \
  --kty RSA-HSM --size 2048 \
  --exportable true \
  --policy @skr-policy.json
```

---

### 10) Deploy the container group & get the IP

```bash
az deployment group create \
  -g $GROUP \
  --template-file templates/template.private.json \
  --parameters name=$CG_NAME location=$LOC

IP=$(az container show -g $GROUP -n $CG_NAME --query ipAddress.ip -o tsv)
echo "Public IP: $IP"
```

---

### 11) Smoke test

```bash
# (example) if your app serves a health endpoint on 8080
curl -fsS http://$IP:8080/healthz || true
```

To test SKR from inside your app, call the sidecar at `http://localhost:8081/key/release` with:

```json
{
  "maa_endpoint": "https://<maa-name>.<region>.attest.azure.net",
  "akv_endpoint": "https://<kv-name>.vault.azure.net",
  "kid": "default"
}
```
