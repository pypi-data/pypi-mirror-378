# Foreman MCP Server

MCP server for Foreman host management and infrastructure automation.

## Features

- List and search hosts from Foreman
- Get detailed host information
- Search by location, OS, and environment
- Generic configuration via environment variables

## Installation

```bash
pip install git+https://github.com/rorymcmahon/foreman-mcp-server.git
```

Or for development:
```bash
git clone https://github.com/rorymcmahon/foreman-mcp-server.git
cd foreman-mcp-server
pip install -e .
```

## Configuration

Set the following environment variables:

- `FOREMAN_URL`: Base URL of your Foreman instance (e.g., `https://foreman.example.com`)
- `FOREMAN_USERNAME`: Foreman username
- `FOREMAN_PASSWORD`: **Personal Access Token** (not your web login password - create this in User Administration → Personal Access Tokens)
- `FOREMAN_VERIFY_SSL`: Whether to verify SSL certificates (default: `true`)

### Required Permissions

The user account needs the following minimum permissions to use all MCP server tools:

| Resource Type | Permission | Purpose |
|---------------|------------|---------|
| Host | `view_hosts` | List and search hosts, get host details and status |
| Organization | `view_organizations` | List organizations |
| Location | `view_locations` | List locations |
| Hostgroup | `view_hostgroups` | List and search by hostgroups |
| Subnet | `view_subnets` | List subnets and get subnet details |
| Domain | `view_domains` | List domains and get domain details |
| SmartProxy | `view_smart_proxies` | List smart proxies and get proxy details |

### Recommended Roles

Instead of assigning individual permissions, you can use these built-in roles:

| Role | Description | Recommended For |
|------|-------------|-----------------|
| **Viewer** | Read-only access to most Foreman resources | General monitoring and inventory queries |
| **Ansible Tower Inventory Reader** | Specific permissions for inventory access | Automated systems integration |
| **Organization admin** | Full access within assigned organizations | Organization-specific administration |

**Note**: The "Viewer" role provides the most appropriate permissions for this MCP server's read-only operations.

## MCP Configuration

Add to your MCP client configuration:

```json
{
  "foreman-mcp-server": {
    "command": "foreman-mcp-server",
    "env": {
      "FOREMAN_URL": "https://foreman.example.com",
      "FOREMAN_USERNAME": "your-username",
      "FOREMAN_PASSWORD": "your-password",
      "FOREMAN_VERIFY_SSL": "true"
    }
  }
}
```

## Available Tools

### Host Management
- `list_hosts(search, per_page, page)` - List hosts with optional search
- `get_host(host_id)` - Get detailed host information
- `get_host_status(host_id)` - Get status information for a specific host

### Host Search Functions
- `search_hosts_by_location(location, per_page)` - Search by location
- `search_hosts_by_os(os_name, per_page)` - Search by operating system
- `search_hosts_by_environment(environment, per_page)` - Search by environment
- `search_hosts_by_hostgroup(hostgroup, per_page)` - Search by hostgroup
- `search_hosts_by_fact(fact_name, fact_value, per_page)` - Search by custom facts

### Infrastructure Information
- `list_organizations(per_page)` - List all organizations
- `list_locations(per_page)` - List all locations
- `list_hostgroups(per_page)` - List all hostgroups
- `list_subnets(per_page)` - List all subnets
- `get_subnet(subnet_id)` - Get detailed subnet information
- `list_domains(per_page)` - List all domains
- `get_domain(domain_id)` - Get detailed domain information
- `list_smart_proxies(per_page)` - List all smart proxies
- `get_smart_proxy(proxy_id)` - Get detailed smart proxy information

## Development

```bash
pip install -e ".[dev]"
pytest
```
