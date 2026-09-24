import ipaddress
from google.adk.agents.llm_agent import Agent


# ============================================================================
# STEP 1: Define "Tools" (Simple Python functions that the AI Agent can call)
# ============================================================================

def check_gcp_subnet_ips(cidr_block: str) -> dict:
    """Calculates usable IPs and GCP-reserved addresses for a VPC subnet CIDR.

    Args:
        cidr_block: An IPv4 CIDR string, for example '10.10.0.0/24' or '192.168.1.0/28'.
    """
    try:
        net = ipaddress.ip_network(cidr_block, strict=False)
        hosts = list(net.hosts())
        # In Google Cloud VPCs, 4 IP addresses are reserved in every primary subnet range:
        # Network address, Default gateway (first host), Second-to-last host, Broadcast address.
        usable_gcp_hosts = max(0, net.num_addresses - 4)
        return {
            "status": "success",
            "cidr": str(net),
            "netmask": str(net.netmask),
            "total_addresses": net.num_addresses,
            "usable_ips_in_gcp_vpc": usable_gcp_hosts,
            "gcp_reserved_ips": {
                "network_address": str(net.network_address),
                "default_gateway": str(hosts[0]) if len(hosts) >= 1 else "N/A",
                "second_to_last_reserved": str(hosts[-1]) if len(hosts) >= 2 else "N/A",
                "broadcast_address": str(net.broadcast_address),
            },
        }
    except ValueError as e:
        return {"status": "error", "message": f"Invalid CIDR block '{cidr_block}': {e}"}


def recommend_agent_gateway_mode(traffic_pattern: str) -> dict:
    """Recommends the Google Cloud Agent Gateway deployment mode for a given networking scenario.

    Args:
        traffic_pattern: Description of traffic flow (e.g., 'client to agent', 'agent to mcp tool', 'existing ALB', 'existing SWP').
    """
    pattern = traffic_pattern.lower()
    if "alb" in pattern or "load balancer" in pattern or "swp" in pattern or "secure web proxy" in pattern:
        return {
            "recommended_mode": "Self-Managed Agent Gateway (selfManaged)",
            "attachment_target": "Existing Application Load Balancer (ALB) or Secure Web Proxy (SWP)",
            "how_it_works": (
                "Attaches Agent Gateway governance policies via Service Extensions to your existing "
                "Cloud Load Balancing or Secure Web Proxy infrastructure while binding to Agent Registry."
            ),
        }
    elif "egress" in pattern or "tool" in pattern or "mcp" in pattern or "anywhere" in pattern:
        return {
            "recommended_mode": "Google-Managed Agent Gateway (googleManaged: AGENT_TO_ANYWHERE)",
            "networking_features": "PSC-Interface Egress (networkAttachment) + DNS Peering to your VPC",
            "how_it_works": (
                "Google orchestrates a managed proxy in a tenant project with an mTLS endpoint, "
                "governing outbound Agent-to-Tool (MCP) and Agent-to-Agent (A2A) calls using Agent Registry bindings."
            ),
        }
    else:
        return {
            "recommended_mode": "Google-Managed Agent Gateway (googleManaged: CLIENT_TO_AGENT)",
            "networking_features": "Managed mTLS Endpoint + Root CA validation + Agent Registry governance",
            "how_it_works": (
                "Protects inbound Client-to-Agent or Agent-to-Agent (A2A) traffic with Google-managed "
                "proxy orchestration and identity/registry enforcement."
            ),
        }


# ============================================================================
# STEP 2: Define the Agent (Brain + Instructions + Tools)
# ============================================================================

root_agent = Agent(
    model="gemini-2.5-flash",
    name="network_agent",
    description="A Google Cloud Networking & Agent Gateway specialist assistant.",
    instruction=(
        "You are a friendly Google Cloud Networking & Agent Gateway Assistant built for Customer Engineers. "
        "Keep answers clear, structured, and beginner-friendly. "
        "Use `check_gcp_subnet_ips` whenever the user asks about subnet CIDRs or IP sizing, "
        "and use `recommend_agent_gateway_mode` when asked about Agent Gateway architecture or traffic flows."
    ),
    tools=[check_gcp_subnet_ips, recommend_agent_gateway_mode],
)
