# SPDX-License-Identifier: Apache-2.0

import argparse
import asyncio
import json
import os
from urllib.parse import unquote

import httpx
import pkg_resources  # type: ignore
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, PlainTextResponse

try:
    from .heartbeat import HeartbeatService  # import as module
except ImportError:
    from heartbeat import HeartbeatService  # type: ignore  # import as script


# Create router
router = APIRouter()

# Global variable to store proxy nodes and their target nodes
# Example structure:
# [
#     {
#         "name": "proxy1",
#         "host": "127.0.0.1",
#         "port": "8001",
#         "nodes": [
#             {"name": "node1", "host": "127.0.0.1", "port": "8002"},
#             {"name": "node2", "host": "127.0.0.1", "port": "8003"}
#         ]
#     }
# ]
target_nodes = []

# Initialize heartbeat service with app context
heartbeat_service: HeartbeatService = HeartbeatService()

global args
args = None


async def fetch_child_nodes_from_proxy(proxy_node):
    """Fetch child nodes from proxy node"""
    try:
        url = f"http://{proxy_node['host']}:{proxy_node['port']}/api/nodes"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return_nodes = []
            added_names = set()  # Track node names to avoid duplicates
            nodes = response.json().get("nodes", [])

            # Process each node: only add leaf nodes (nodes without children)
            for node in nodes:
                if node.get("children"):
                    # If node has children, add only the children (leaf nodes)
                    for child in node["children"]:
                        # Skip if already added
                        if child["name"] in added_names:
                            continue
                        child["proxy_id"] = proxy_node["name"]
                        return_nodes.append(child)
                        added_names.add(child["name"])
                else:
                    # Skip if already added
                    if node["name"] in added_names:
                        continue
                    node["proxy_id"] = proxy_node["name"]
                    return_nodes.append(node)
                    added_names.add(node["name"])
            return return_nodes
    except Exception as e:
        print(f"Failed to fetch nodes from proxy {proxy_node['name']}: {e}")
        return []


async def fetch_nodes_from_supplier(url):
    """Fetch node information from node supplier"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            unique_nodes = set()
            for api_address, info in data.get("processInfos", {}).items():
                for entity in info.get("lmCacheInfoEntities", []):
                    # Parse apiAddress to get host and port
                    url = entity["apiAddress"]
                    if url.startswith("http://"):
                        url = url[7:]
                    host, port = url.split(":")
                    node_key = f"{host}:{port}"
                    unique_nodes.add(node_key)

            return [
                {
                    "name": f"proxy_{host_port.replace(':', '_')}",
                    "host": host_port.split(":")[0],
                    "port": host_port.split(":")[1],
                    "nodes": [],
                }
                for host_port in unique_nodes
            ]
    except Exception as e:
        print(f"Failed to fetch nodes from supplier: {e}")
        return []


def load_config(config_path=None):
    global target_nodes
    try:
        # Prioritize user-specified configuration file
        if config_path:
            with open(config_path, "r") as f:
                target_nodes = json.load(f)
            print(
                f"Loaded {len(target_nodes)} target nodes from specified path: "
                f"{config_path}"
            )
        else:
            # Use package resource path as default configuration
            default_config_path = pkg_resources.resource_filename(
                "lmcache_frontend", "config.json"
            )
            with open(default_config_path, "r") as f:
                target_nodes = json.load(f)
            print(f"Loaded default configuration with {len(target_nodes)} target nodes")
    except Exception as e:
        print(f"Failed to load configuration file: {e}")
        target_nodes = []


def validate_node(node, is_proxy=False):
    """Validate a single node configuration"""
    if not isinstance(node, dict):
        return False

    required_keys = {"name", "host", "port"}
    if not required_keys.issubset(node.keys()):
        return False

    if "proxy_id" in node and node["proxy_id"]:
        if not isinstance(node["proxy_id"], str):
            return False

    return True


def validate_nodes(nodes):
    """Validate list of nodes"""
    if not isinstance(nodes, list):
        return False

    return all(validate_node(node) for node in nodes)


@router.get("/api/nodes")
async def get_all_nodes():
    """Get all nodes in tree structure (proxies with their child nodes)"""
    all_nodes = []
    for proxy in target_nodes:
        # Create proxy node with children property
        proxy_node = {
            "id": f"proxy_{proxy['name']}",
            "name": proxy["name"],
            "host": proxy["host"],
            "port": proxy["port"],
            "is_proxy": True,
            "children": [],
        }

        # Add child nodes
        for node in proxy.get("nodes", []):
            proxy_node["children"].append(
                {
                    "id": f"node_{node['name']}",
                    "name": node["name"],
                    "host": node["host"],
                    "port": node["port"],
                    "is_proxy": False,
                    "proxy_id": proxy["name"],
                }
            )

        all_nodes.append(proxy_node)

    return {"nodes": all_nodes}


@router.get("/api/proxies/{proxy_name}/refresh")
async def refresh_proxy_nodes(proxy_name: str):
    """Refresh child nodes of a proxy"""
    proxy = next((p for p in target_nodes if p["name"] == proxy_name), None)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")

    try:
        child_nodes = await fetch_child_nodes_from_proxy(proxy)
        proxy["nodes"] = child_nodes
        return {"status": "success", "nodes": child_nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/proxies")
async def get_proxies():
    """Get all proxy nodes (without child nodes)"""
    proxies = [
        {"name": proxy["name"], "host": proxy["host"], "port": proxy["port"]}
        for proxy in target_nodes
    ]
    return {"proxies": proxies}


@router.get("/api/proxies/{proxy_name}/nodes")
async def get_proxy_nodes(proxy_name: str):
    """Get all nodes under specified proxy"""
    proxy = next((p for p in target_nodes if p["name"] == proxy_name), None)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    return {"nodes": proxy["nodes"]}


# ==== Node Management Endpoints ====
@router.post("/api/proxies")
async def add_proxy(request: Request):
    """Add a new proxy node"""
    global target_nodes
    try:
        new_proxy = await request.json()
        if not validate_node(new_proxy, is_proxy=True):
            raise HTTPException(status_code=400, detail="Invalid proxy format")

        # Check for duplicate names
        if any(proxy["name"] == new_proxy["name"] for proxy in target_nodes):
            raise HTTPException(status_code=409, detail="Proxy name already exists")

        # Ensure nodes field exists
        if "nodes" not in new_proxy:
            new_proxy["nodes"] = []

        target_nodes.append(new_proxy)
        return {"status": "success", "message": "Proxy added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/proxies/{proxy_name}/nodes")
async def add_node_to_proxy(proxy_name: str, request: Request):
    """Add child node to proxy"""
    global target_nodes
    try:
        new_node = await request.json()
        if not validate_node(new_node):
            raise HTTPException(status_code=400, detail="Invalid node format")

        # Find corresponding proxy
        proxy = next((p for p in target_nodes if p["name"] == proxy_name), None)
        if not proxy:
            raise HTTPException(status_code=404, detail="Proxy not found")

        # Check for duplicate names
        if any(node["name"] == new_node["name"] for node in proxy["nodes"]):
            raise HTTPException(status_code=409, detail="Node name already exists")

        proxy["nodes"].append(new_node)
        return {"status": "success", "message": "Node added to proxy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/nodes/{node_name}")
async def update_node(node_name: str, request: Request):
    """Update an existing node"""
    global target_nodes
    try:
        updated_node = await request.json()
        if not validate_node(updated_node):
            raise HTTPException(status_code=400, detail="Invalid node format")

        for i, node in enumerate(target_nodes):
            if node["name"] == node_name:
                target_nodes[i] = updated_node
                return {"status": "success", "message": "Node updated"}

        raise HTTPException(status_code=404, detail="Node not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/nodes/{node_name}")
async def delete_node(node_name: str):
    """Delete a node from the target list"""
    global target_nodes
    try:
        original_count = len(target_nodes)
        target_nodes = [node for node in target_nodes if node["name"] != node_name]

        if len(target_nodes) == original_count:
            raise HTTPException(status_code=404, detail="Node not found")

        return {"status": "success", "message": "Node deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.api_route(
    "/proxy2/{node_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def proxy_request_by_name(request: Request, node_name: str, path: str):
    """Proxy requests using node name as identifier"""
    # Find node by name
    node = next((n for n in target_nodes if n["name"] == node_name), None)
    if not node:
        # Find node from local_proxy
        proxy_node = next((n for n in target_nodes if n["name"] == "local_proxy"), None)
        if proxy_node:
            node = next(
                (n for n in proxy_node["nodes"] if n["name"] == node_name), None
            )
    if not node:
        raise HTTPException(
            status_code=404, detail=f"Node with name '{node_name}' not found"
        )

    # Use existing proxy_request logic
    return await proxy_request(
        request, target_host=node["host"], target_port_or_socket=node["port"], path=path
    )


@router.api_route(
    "/proxy/{target_host}/{target_port_or_socket}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def proxy_request(
    request: Request, target_host: str, target_port_or_socket: str | int, path: str
):
    """Proxy requests to the specified target host and port or socket path"""
    target_port_or_socket = unquote(str(target_port_or_socket))
    # Check if target_port_or_socket is a socket path (contains '/')
    is_socket_path = "/" in target_port_or_socket

    if is_socket_path:
        # For socket paths, use UDS transport
        socket_path = target_port_or_socket
        target_url = f"http://localhost/{path}"

        # Create UDS transport
        transport = httpx.AsyncHTTPTransport(uds=socket_path)
    else:
        port = target_port_or_socket
        target_url = f"http://{target_host}:{port}/{path}"
        transport = None  # Use default transport

    headers = {}
    for key, value in request.headers.items():
        if key.lower() in [
            "host",
            "content-length",
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        ]:
            continue
        headers[key] = value

    body = await request.body()

    # Create client with appropriate transport
    async with httpx.AsyncClient(transport=transport) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=60.0,
            )

            response_headers = {}
            for key, value in response.headers.items():
                if key.lower() in [
                    "connection",
                    "keep-alive",
                    "proxy-authenticate",
                    "proxy-authorization",
                    "the",
                    "trailers",
                    "transfer-encoding",
                    "upgrade",
                ]:
                    continue
                response_headers[key] = value

            return PlainTextResponse(
                content=response.content,
                headers=response_headers,
                media_type=response.headers.get("content-type", "text/plain"),
                status_code=response.status_code,
            )

        except httpx.ConnectError as e:
            if is_socket_path:
                detail = f"Failed to connect to socket: {socket_path}"
            else:
                detail = f"Failed to connect to target service {target_host}:{port}"
            raise HTTPException(status_code=502, detail=detail) from e
        except httpx.TimeoutException as e:
            if is_socket_path:
                detail = f"Connection to socket {socket_path} timed out"
            else:
                detail = f"Connection to target service {target_host}:{port} timed out"
            raise HTTPException(status_code=504, detail=detail) from e
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error communicating with target service: {str(e)}",
            ) from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}") from e


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lmcache-monitor"}


@router.get("/api/heartbeat/status")
async def get_heartbeat_status():
    """Get heartbeat status"""
    return heartbeat_service.status()


@router.post("/api/heartbeat/start")
async def start_heartbeat_api(request: Request):
    """Start heartbeat service"""
    try:
        data = await request.json()
        heartbeat_url = data.get("heartbeat_url")
        initial_delay = data.get("initial_delay", 0)
        interval = data.get("interval", 30)

        if not heartbeat_url:
            raise HTTPException(status_code=400, detail="heartbeat_url is required")

        heartbeat_service.start(heartbeat_url, initial_delay, interval)
        return {"status": "success", "message": "Heartbeat service started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/heartbeat/stop")
async def stop_heartbeat_api():
    """Stop heartbeat service"""
    try:
        heartbeat_service.stop()
        return {"status": "success", "message": "Heartbeat service stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def load_nodes_from_supplier(node_supplier_url: str | None = None):
    """Load node information from node supplier"""
    global target_nodes

    if not node_supplier_url:
        return False

    print(f"Fetching nodes from supplier: {node_supplier_url}")
    nodes = await fetch_nodes_from_supplier(node_supplier_url)
    if nodes:
        target_nodes = nodes
        print(f"Loaded {len(target_nodes)} proxy nodes from supplier")

        # Get child nodes for each proxy
        print("Fetching child nodes for each proxy...")
        for proxy in target_nodes:
            child_nodes = await fetch_child_nodes_from_proxy(proxy)
            proxy["nodes"] = child_nodes
            print(f"Proxy {proxy['name']} loaded {len(child_nodes)} child nodes")
        return True
    else:
        print("Warning: No nodes loaded from supplier")
        return False


async def initialize_nodes(node_supplier_url: str | None = None):
    """Initialize node configuration"""
    global target_nodes
    global args

    if args is None:
        raise ValueError("args is not initialized")

    if node_supplier_url:
        await load_nodes_from_supplier(node_supplier_url)
    elif args.nodes:
        try:
            nodes = json.loads(args.nodes)
            if validate_nodes(nodes):
                target_nodes = [
                    {
                        "name": "local_proxy",
                        "host": args.host,
                        "port": args.port,
                        "nodes": nodes,
                    }
                ]
                print(f"Loaded {len(nodes)} target nodes from command line arguments")
        except json.JSONDecodeError:
            print("Failed to parse nodes JSON parameter")
    elif args.config:
        load_config(args.config)


@router.get("/")
async def serve_frontend():
    """Return frontend homepage"""
    # Check if node supplier URL is configured
    if args.node_supplier_url:
        await initialize_nodes(args.node_supplier_url)

    try:
        # Use package resource path
        index_path = pkg_resources.resource_filename(
            "lmcache_frontend", "static/index.html"
        )
        return FileResponse(index_path)
    except Exception:
        # Development environment uses local files
        return FileResponse("static/index.html")


# Helper function to fetch metrics from a single node
async def _fetch_node_metrics(node):
    """Fetch metrics from a single node"""
    try:
        # Check if port is a socket path
        is_socket_path = "/" in node["port"]

        if is_socket_path:
            # Use UDS transport for socket paths
            transport = httpx.AsyncHTTPTransport(uds=node["port"])
            # Use localhost as host
            url = "http://localhost/metrics"
            async with httpx.AsyncClient(transport=transport, timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        else:
            # Build URL for regular port
            url = f"http://{node['host']}:{node['port']}/metrics"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
    except Exception as e:
        return f"# ERROR: Failed to get metrics from {node['name']}: {str(e)}\n"


@router.get("/metrics")
async def aggregated_metrics():
    """Aggregate metrics from all nodes"""
    if not target_nodes:
        return PlainTextResponse("# No nodes configured\n", status_code=404)

    # TODO(baoloongmao): Support gather all metrics
    if isinstance(target_nodes, dict) and "local_proxy" in target_nodes:
        nodes = target_nodes["local_proxy"]["nodes"]
    elif isinstance(target_nodes, list):
        proxy_node = next(
            (n for n in target_nodes if n.get("name") == "local_proxy"), None
        )
        nodes = proxy_node["nodes"] if proxy_node else []
    else:
        nodes = []

    if not nodes:
        return PlainTextResponse(
            "# No nodes available for metrics collection\n", status_code=404
        )

    metrics_results = await asyncio.gather(
        *[_fetch_node_metrics(node) for node in nodes]
    )

    # Combine all metrics with node name as comment header
    aggregated = ""
    for i, metrics in enumerate(metrics_results):
        node = nodes[i]
        aggregated += (
            f"# Metrics from node: {node['name']} ({node['host']}:{node['port']})\n"
        )
        aggregated += metrics
        aggregated += "\n\n"

    return PlainTextResponse(aggregated)


def create_app():
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Flexible Proxy Server",
        description="HTTP proxy service supporting specified target hosts and ports",
    )
    app.include_router(router)

    # Get static file path (prefer package resources)
    try:
        static_path = pkg_resources.resource_filename("lmcache_frontend", "static")
    except Exception:
        static_path = os.path.join(os.path.dirname(__file__), "static")

    # Mount static file service
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    return app


def main():
    global args  # 声明使用全局变量
    parser = argparse.ArgumentParser(description="LMCache Cluster Monitoring Tool")
    parser.add_argument(
        "--port", type=int, default=8000, help="Service port, default 8000"
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Bind host address, default 0.0.0.0"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Specify configuration file path, default uses internal config.json",
    )
    parser.add_argument(
        "--nodes",
        type=str,
        default=None,
        help="Directly specify target nodes as a JSON string. "
        'Example: \'[{"name":"node1","host":"127.0.0.1","port":8001}]\'',
    )
    parser.add_argument(
        "--heartbeat-url",
        type=str,
        default=None,
        help="Heartbeat service URL, e.g.: http://example.com/heartbeat",
    )
    parser.add_argument(
        "--heartbeat-initial-delay",
        type=int,
        default=0,
        help="Initial delay before starting heartbeat (seconds), default 0",
    )
    parser.add_argument(
        "--heartbeat-interval",
        type=int,
        default=30,
        help="Heartbeat interval (seconds), default 30",
    )
    parser.add_argument(
        "--node-supplier-url",
        type=str,
        default=None,
        help="URL to fetch node information from, e.g.: http://example.com/lmcache_infos",
    )

    args = parser.parse_args()  # 赋值给全局变量

    # Initialize node configuration
    asyncio.run(initialize_nodes(args.node_supplier_url))

    app = create_app()
    print(f"Monitoring service running at http://{args.host}:{args.port}")
    print(f"Node management: http://{args.host}:{args.port}/static/index.html")

    # Start heartbeat service if URL is configured
    if args.heartbeat_url:
        # Set application configuration for heartbeat service
        heartbeat_service.set_app_config(args.host, args.port, target_nodes)

        print("Starting heartbeat service...")
        print(f"Heartbeat URL: {args.heartbeat_url}")
        print(f"Initial delay: {args.heartbeat_initial_delay}s")
        print(f"Interval: {args.heartbeat_interval}s")
        print(f"API Address: http://{args.host}:{args.port}")
        print(f"Target nodes count: {len(target_nodes)}")

        heartbeat_service.start(
            args.heartbeat_url, args.heartbeat_initial_delay, args.heartbeat_interval
        )
    else:
        print("Heartbeat URL not configured, heartbeat disabled")

    try:
        uvicorn.run(app, host=args.host, port=args.port)
    finally:
        # Stop heartbeat service when app closes
        print("Shutting down application...")
        heartbeat_service.stop()


if __name__ == "__main__":
    main()
