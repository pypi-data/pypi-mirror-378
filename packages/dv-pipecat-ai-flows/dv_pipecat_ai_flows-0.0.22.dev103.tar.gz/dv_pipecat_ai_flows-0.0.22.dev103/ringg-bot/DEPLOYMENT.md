# Deployment Guide - Ringg Chatbot

This comprehensive guide covers the deployment architecture, CI/CD pipeline, and operational procedures for the ringg-chatbot system.

## Deployment Architecture Overview

The ringg-chatbot is deployed on Google Kubernetes Engine (GKE) with a sophisticated multi-environment setup:

### Environment Structure
- **Staging** (`dv-stage` branch) → `desivocal-staging-cluster` (asia-south1-a)
- **Production Canary** (`dv-main` branch) → `desivocal-prod-us-e1-cluster` (us-east1)
- **Production Stable** (Manual promotion) → Same production cluster

### Deployment Strategy
```
dv-stage branch → Automatic deployment to Staging
dv-main branch → Automatic deployment to Canary (2 replicas, separate deployment)
Manual trigger → Promote Canary to Stable (60 replicas, main deployment)
```

## CI/CD Pipeline Architecture

### 1. Main Deployment Pipeline (`.github/workflows/github.yml`)

**Triggers:**
- Push to `dv-stage` → Deploy to staging environment
- Push to `dv-main` → Deploy to production canary environment

**Key Features:**
- **Multi-arch Docker builds**: ARM64 for production, AMD64 for staging
- **Google Artifact Registry**: Regional container repositories
- **Workload Identity Federation**: Secure GCP authentication
- **Helm-based deployments**: Infrastructure as Code
- **Secret management**: Kubernetes secrets from GitHub secrets

### 2. Production Promotion Pipeline (`.github/workflows/promote-prod.yml`)

**Manual trigger only** - Promotes canary deployment to stable production:
- Extracts current canary image tag
- Updates stable deployment with canary image
- Uses production values configuration

## Kubernetes Configuration

### Helm Chart Structure (`k8s/dv-pipecat/`)

```
k8s/dv-pipecat/
├── Chart.yaml                 # Helm chart metadata
├── values.yaml                # Base configuration
├── values-stage.yaml          # Staging overrides
├── values-prod.yaml           # Production overrides  
├── values-canary.yaml         # Canary-specific config
└── templates/
    ├── deployment.yaml        # Main deployment template
    ├── service.yaml           # Service configuration
    ├── ingress.yaml           # Ingress rules
    └── hpa.yaml               # Horizontal Pod Autoscaler
```

### Environment-Specific Configurations

#### Staging (`values-stage.yaml`)
```yaml
replicaCount: 1
image:
  pullPolicy: Always
resources:
  limits: { cpu: 1, memory: 1.5Gi }
  requests: { cpu: 500m, memory: 1Gi }
ingress:
  hosts: [{ host: stage-api2.desivocal.com, paths: [{ path: /pc }] }]
```

#### Production Stable (`values-prod.yaml`)
```yaml
replicaCount: 60
resources:
  limits: { cpu: 1, memory: 3Gi }
  requests: { cpu: 1, memory: 2.5Gi }
nodeSelector: { kubernetes.io/arch: arm64 }
ingress:
  hosts: [{ host: use1-api.ringg.ai, paths: [{ path: /pc/* }] }]
terminationGracePeriodSeconds: 270  # 4.5 minutes for graceful shutdowns
```

#### Production Canary (`values-canary.yaml`)
```yaml
releaseTrack: canary
replicaCount: 2
service:
  create: false  # Uses stable service
env:
  - name: LOGGER_NAME
    value: "pipecat-canary"
```

## Deployment Architecture

### Canary vs Stable Deployments

The system uses **separate Kubernetes deployments** for canary and stable versions:

- **`dv-pipecat`** (Stable) - Main production deployment with 60 replicas
- **`dv-pipecat-canary`** (Canary) - Test deployment with 2 replicas  

**Key Differences:**
```yaml
# Stable deployment
replicaCount: 60
service: { create: true }  # Creates main service

# Canary deployment  
replicaCount: 2
service: { create: false } # Uses stable service
releaseTrack: canary
```

**Traffic Routing:**
- Both deployments share the same service (`dv-pipecat`)
- Canary pods are identified by `version: canary` labels
- Manual testing is done against canary pods before promoting to stable

## Secret Management

### GitHub Secrets Configuration

**Staging Secrets:**
- `STAGE_SECRETS_JSON` - Application environment variables as JSON
- `STAGE_CREDS_JSON` - GCP service account credentials

**Production Secrets:**  
- `PROD_SECRETS_JSON` - Production environment variables as JSON
- `PROD_CREDS_JSON` - Production GCP service account credentials

### Kubernetes Secret Structure

**Application Secrets (`dv-pipecat-app-secrets`):**
```bash
# Created from SECRETS_JSON
kubectl create secret generic dv-pipecat-app-secrets \
  --from-literal=OPENAI_API_KEY=value \
  --from-literal=REDIS_URL=value \
  # ... other environment variables
```

**GCP Credentials Secret (`dv-pipecat-gcp-creds`):**
```bash
# Mounted as file in container
kubectl create secret generic dv-pipecat-gcp-creds \
  --from-file=creds.json=/dev/stdin
```

## Container Configuration

### Deployment Template Features

**Resource Management:**
```yaml
resources:
  limits: { cpu: 1, memory: 3Gi }    # Production limits
  requests: { cpu: 1, memory: 2.5Gi } # Guaranteed resources
terminationGracePeriodSeconds: 270    # Graceful shutdown (4.5min)
```

**Health Checks:**
```yaml
readinessProbe:
  httpGet: { path: /pc/v1/healthcheck, port: 8765 }
  initialDelaySeconds: 60
  periodSeconds: 30
livenessProbe:
  httpGet: { path: /pc/v1/healthcheck, port: 8765 }  
  initialDelaySeconds: 90
  periodSeconds: 60
```

**Volume Mounts:**
```yaml
volumeMounts:
- name: secret-volume-gcp-creds
  mountPath: "/app/creds.json"
  subPath: creds.json
  readOnly: true
```

**Environment Variables:**
```yaml
envFrom:
- secretRef:
    name: dv-pipecat-app-secrets  # All env vars from secret
env:
- name: LOGGER_NAME
  value: "pipecat"  # Static environment variables
```

## Deployment Workflow

### 1. Development to Staging

```bash
# Push to staging branch
git checkout dv-stage
git merge feature-branch
git push origin dv-stage

# Automatic deployment triggered:
# 1. Build AMD64 Docker image
# 2. Push to ringg-registry-stage
# 3. Deploy to desivocal-staging-cluster
# 4. Use values-stage.yaml configuration
```

### 2. Staging to Production Canary

```bash
# Push to main branch  
git checkout dv-main
git merge dv-stage
git push origin dv-main

# Automatic canary deployment:
# 1. Build ARM64 Docker image  
# 2. Push to ringg-registry-prod
# 3. Deploy to desivocal-prod-us-e1-cluster
# 4. Use values-prod.yaml + values-canary.yaml
# 5. Creates dv-pipecat-canary deployment (2 replicas)
```

### 3. Canary to Stable Promotion

```bash
# Manual trigger in GitHub Actions
# Navigate to: Actions → Promote Canary → Stable → Run workflow

# Promotion process:
# 1. Extract current canary image tag
# 2. Update stable deployment (dv-pipecat) with canary image
# 3. Rolling update to 60 replicas
# 4. Manual testing can be done against canary before promotion
```

## Operational Procedures

### Monitoring Deployments

**Check Deployment Status:**
```bash
# Connect to production cluster
gcloud container clusters get-credentials desivocal-prod-us-e1-cluster --zone us-east1

# Check deployment status
kubectl get deployments
kubectl get pods -l app.kubernetes.io/name=dv-pipecat

# Check canary vs stable
kubectl get pods -l version=stable
kubectl get pods -l version=canary
```

**View Logs:**
```bash
# Stable pods
kubectl logs -l version=stable -f

# Canary pods  
kubectl logs -l version=canary -f

# Specific pod
kubectl logs dv-pipecat-canary-xxxx-yyyy -f
```

### Rollback Procedures

**Rollback Canary:**
```bash
# Use previous stable image for canary
helm upgrade dv-pipecat-canary ./k8s/dv-pipecat \
  -f ./k8s/dv-pipecat/values-prod.yaml \
  -f ./k8s/dv-pipecat/values-canary.yaml \
  --set image.tag=<previous-stable-tag>
```

**Rollback Stable:**
```bash
# Use Helm rollback
helm rollback dv-pipecat

# Or promote previous canary
helm upgrade dv-pipecat ./k8s/dv-pipecat \
  -f ./k8s/dv-pipecat/values-prod.yaml \
  --set image.tag=<previous-working-tag>
```

### Health Check Endpoints

**Application Health:**
```bash
# Via ingress (production)
curl https://use1-api.ringg.ai/pc/v1/healthcheck

# Via staging
curl https://stage-api2.desivocal.com/pc/v1/healthcheck

# Direct pod access
kubectl port-forward pod/dv-pipecat-xxx 8765:8765
curl http://localhost:8765/pc/v1/healthcheck
```

### Scaling Operations

**Manual Scaling:**
```bash
# Scale stable deployment
kubectl scale deployment dv-pipecat --replicas=80

# Scale canary deployment  
kubectl scale deployment dv-pipecat-canary --replicas=5
```

**Auto-scaling (HPA):**
```yaml
# Currently disabled, can be enabled in values-prod.yaml
autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 100
  targetCPUUtilizationPercentage: 75
```

## Security Configuration

### Workload Identity Federation

**Service Account Setup:**
- **Pool**: `desivocal-staging-pool`  
- **Provider**: `github`
- **Service Account**: `gke-githubactions-svc-stage@desivocalprod01.iam.gserviceaccount.com`

### Network Security

**Ingress Configuration:**
- **GKE Ingress Controller**: Native Google Cloud Load Balancer
- **Path Routing**: `/pc/*` for production, `/pc` for staging
- **TLS**: Managed certificates (commented configurations available)

**Kubernetes Security:**
- **Network Policies**: Standard Kubernetes network isolation
- **RBAC**: Role-based access control for service accounts
- **Secret Management**: Encrypted at rest with automatic rotation

## Troubleshooting Guide

### Common Issues

**1. Pod Startup Failures:**
```bash
# Check pod events
kubectl describe pod dv-pipecat-xxx

# Check container logs
kubectl logs dv-pipecat-xxx -c dv-pipecat

# Common causes:
# - Missing secrets (check secret mounts)
# - Invalid image tag
# - Resource constraints
# - Health check failures
```

**2. Service Routing Issues:**
```bash
# Check service endpoints
kubectl get endpoints dv-pipecat

# Check service configuration
kubectl describe service dv-pipecat

# Verify pod labels match service selectors
kubectl get pods -l app.kubernetes.io/name=dv-pipecat --show-labels
```

**3. CI/CD Pipeline Failures:**
```bash
# Common GitHub Actions issues:
# - Workload Identity authentication
# - Docker build failures (multi-arch)
# - Helm deployment errors
# - Secret creation failures
```

### Performance Monitoring

**Resource Usage:**
```bash
# Check CPU/Memory usage
kubectl top pods -l app.kubernetes.io/name=dv-pipecat

# Check node resources
kubectl top nodes
```

**Application Metrics:**
```bash
# Health check response times
curl -w "@curl-format.txt" https://use1-api.ringg.ai/pc/v1/healthcheck

# WebSocket connections
kubectl logs -l app.kubernetes.io/name=dv-pipecat | grep "WebSocket"
```

This deployment architecture provides robust, scalable, and secure hosting for the ringg-chatbot system with comprehensive monitoring, rollback capabilities, and automated deployment pipelines.