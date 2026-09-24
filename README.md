# Simple Agent 01 (`network_agent`) — Google Cloud Agent Platform & Agent Gateway Lab

A beginner-friendly AI Agent built with the **Google Agent Development Kit (ADK)** for studying **Agent Registry** and **Network Services Agent Gateway** on Google Cloud (`gcp-demo-02-307713`).

---

## 1. Zero-Coding Anatomy of an Agent

An ADK Agent requires only **3 files** inside the [`network_agent/`](./network_agent/) folder:

| File | Purpose |
| :--- | :--- |
| [`network_agent/__init__.py`](./network_agent/__init__.py) | Tells Python that `network_agent` is an Agent package (`from . import agent`). |
| [`network_agent/agent.py`](./network_agent/agent.py) | Defines `root_agent` (the Gemini model, instructions, and Python function tools). |
| [`network_agent/requirements.txt`](./network_agent/requirements.txt) | Lists the required Python libraries (`google-adk[a2a]` and `google-cloud-aiplatform[agent_engines]`). |

### How `agent.py` Works
1. **Tools (Functions):** Normal Python functions (`check_gcp_subnet_ips` and `recommend_agent_gateway_mode`). Gemini reads the function description (docstring) and automatically decides when to call them.
2. **The Agent (`root_agent`):** Connects the **Model** (`gemini-2.5-flash`), **Instructions** (system prompt), and **Tools** list.

---

## 2. Deploying the Agent (Cloud Run vs. Vertex AI Agent Engine)

### Option A: Deploy to Cloud Run (with Web UI + A2A Protocol)
Deploys the agent as a serverless container with both an interactive **ADK Web UI** and an **Agent-to-Agent (`--a2a`)** endpoint:
```bash
adk deploy cloud_run \
  --project=gcp-demo-02-307713 \
  --region=asia-southeast2 \
  --service_name=simple-agent-01 \
  --with_ui \
  --a2a \
  ./network_agent \
  -- --allow-unauthenticated
```

### Option B: Deploy to Vertex AI Agent Engine
Deploys the agent into Google Cloud's managed **Vertex AI Agent Platform** runtime (`ReasoningEngine`):
```bash
adk deploy agent_engine \
  --project=gcp-demo-02-307713 \
  --region=asia-southeast2 \
  --display_name="simple-agent-01" \
  --description="Google Cloud Networking & Agent Gateway Assistant" \
  ./network_agent
```

---

## 3. How Agent Platform, Agent Registry, and Agent Gateway Fit Together (Networking View)

```mermaid
flowchart LR
    Client["Client / Peer Agent"] --> AGW["Agent Gateway<br/>(Network Services)"]
    AGW <-->|Governance & Identity| AReg["Agent Registry<br/>(agentregistry.googleapis.com)"]
    AGW -->|CLIENT_TO_AGENT / A2A| CR["Cloud Run Agent<br/>(simple-agent-01)"]
    AGW -->|CLIENT_TO_AGENT| AE["Vertex AI Agent Engine<br/>(simple-agent-01)"]
    CR -->|AGENT_TO_ANYWHERE / PSC-I| MCP["Private VPC / MCP Tools"]
```

### Useful `gcloud` Commands for Studying Agent Gateway

1. **List Agents & MCP Servers in Agent Registry:**
   ```bash
   gcloud alpha agent-registry agents list --location=us-central1 --project=gcp-demo-02-307713
   gcloud alpha agent-registry mcp-servers list --location=us-central1 --project=gcp-demo-02-307713
   ```
2. **Inspect Your Existing Network Services Agent Gateway:**
   ```bash
   gcloud network-services agent-gateways list --location=us-central1 --project=gcp-demo-02-307713
   gcloud network-services agent-gateways describe agent-gateway --location=us-central1 --project=gcp-demo-02-307713
   ```
