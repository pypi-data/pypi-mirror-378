#!/usr/bin/env python3

import os
import requests
from requests.auth import HTTPBasicAuth
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Foreman Server")

def get_foreman_config():
    """Get Foreman configuration from environment variables"""
    base_url = os.getenv('FOREMAN_URL')
    username = os.getenv('FOREMAN_USERNAME')
    password = os.getenv('FOREMAN_PASSWORD')
    verify_ssl = os.getenv('FOREMAN_VERIFY_SSL', 'true').lower() == 'true'
    
    if not base_url:
        raise ValueError("FOREMAN_URL environment variable is required")
    if not username or not password:
        raise ValueError("FOREMAN_USERNAME and FOREMAN_PASSWORD environment variables are required")
    
    return {
        'base_url': base_url.rstrip('/'),
        'auth': HTTPBasicAuth(username, password),
        'verify_ssl': verify_ssl
    }

@mcp.tool()
def list_hosts(search: str = "", per_page: int = 20, page: int = 1) -> dict:
    """List hosts from Foreman with optional search filter"""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/v2/hosts"
        
        params = {
            'per_page': per_page,
            'page': page
        }
        
        if search:
            params['search'] = search
            
        response = requests.get(url, auth=config['auth'], params=params, 
                              verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to list hosts: {str(e)}"}

@mcp.tool()
def get_host(host_id: str) -> dict:
    """Get detailed information about a specific host"""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/v2/hosts/{host_id}"
        
        response = requests.get(url, auth=config['auth'], verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to get host {host_id}: {str(e)}"}

@mcp.tool()
def search_hosts_by_location(location: str, per_page: int = 20) -> dict:
    """Search hosts by location (e.g., 'SYD03', 'MEL03')"""
    search_query = f"location ~ {location}"
    return list_hosts(search=search_query, per_page=per_page)

@mcp.tool()
def search_hosts_by_os(os_name: str, per_page: int = 20) -> dict:
    """Search hosts by operating system (e.g., 'Windows', 'Oracle Linux')"""
    search_query = f"os ~ {os_name}"
    return list_hosts(search=search_query, per_page=per_page)

@mcp.tool()
def search_hosts_by_environment(environment: str, per_page: int = 20) -> dict:
    """Search hosts by environment (e.g., 'production', 'development')."""
    search_query = f"environment = {environment}"
    return list_hosts(search=search_query, per_page=per_page)


@mcp.tool()
def list_organizations(per_page: int = 20) -> dict:
    """List all organizations in Foreman."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/katello/api/organizations"
        
        params = {'per_page': per_page}
        
        response = requests.get(url, auth=config['auth'], params=params,
                              verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to list organizations: {str(e)}"}


@mcp.tool()
def list_locations(per_page: int = 50) -> dict:
    """List all locations in Foreman."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/locations"
        
        params = {'per_page': per_page}
        
        response = requests.get(url, auth=config['auth'], params=params,
                              verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to list locations: {str(e)}"}


@mcp.tool()
def list_hostgroups(per_page: int = 50) -> dict:
    """List all hostgroups in Foreman."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/hostgroups"
        
        params = {'per_page': per_page}
        
        response = requests.get(url, auth=config['auth'], params=params,
                              verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to list hostgroups: {str(e)}"}


@mcp.tool()
def search_hosts_by_hostgroup(hostgroup: str, per_page: int = 20) -> dict:
    """Search hosts by hostgroup name or title."""
    search_query = f"hostgroup ~ {hostgroup}"
    return list_hosts(search=search_query, per_page=per_page)


@mcp.tool()
def get_host_status(host_id: str) -> dict:
    """Get status information for a specific host."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/hosts/{host_id}/status"
        
        response = requests.get(url, auth=config['auth'], verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to get host status for {host_id}: {str(e)}"}


@mcp.tool()
def search_hosts_by_fact(fact_name: str, fact_value: str, per_page: int = 20) -> dict:
    """Search hosts by a specific fact name and value."""
    search_query = f"facts.{fact_name} = {fact_value}"
    return list_hosts(search=search_query, per_page=per_page)


@mcp.tool()
def list_subnets(per_page: int = 50) -> dict:
    """List all subnets in Foreman."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/subnets"
        
        params = {'per_page': per_page}
        
        response = requests.get(url, auth=config['auth'], params=params,
                              verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to list subnets: {str(e)}"}


@mcp.tool()
def get_subnet(subnet_id: str) -> dict:
    """Get detailed information about a specific subnet."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/subnets/{subnet_id}"
        
        response = requests.get(url, auth=config['auth'], verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to get subnet {subnet_id}: {str(e)}"}


@mcp.tool()
def list_domains(per_page: int = 50) -> dict:
    """List all domains in Foreman."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/domains"
        
        params = {'per_page': per_page}
        
        response = requests.get(url, auth=config['auth'], params=params,
                              verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to list domains: {str(e)}"}


@mcp.tool()
def get_domain(domain_id: str) -> dict:
    """Get detailed information about a specific domain."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/domains/{domain_id}"
        
        response = requests.get(url, auth=config['auth'], verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to get domain {domain_id}: {str(e)}"}


@mcp.tool()
def list_smart_proxies(per_page: int = 50) -> dict:
    """List all smart proxies in Foreman."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/smart_proxies"
        
        params = {'per_page': per_page}
        
        response = requests.get(url, auth=config['auth'], params=params,
                              verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to list smart proxies: {str(e)}"}


@mcp.tool()
def get_smart_proxy(proxy_id: str) -> dict:
    """Get detailed information about a specific smart proxy."""
    try:
        config = get_foreman_config()
        url = f"{config['base_url']}/api/smart_proxies/{proxy_id}"
        
        response = requests.get(url, auth=config['auth'], verify=config['verify_ssl'], timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return {"error": f"Failed to get smart proxy {proxy_id}: {str(e)}"}

def main() -> None:
    """Main entry point for the server."""
    mcp.run()


if __name__ == "__main__":
    main()
