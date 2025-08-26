#!/usr/bin/env python3
import os
import sys
import time
import json
import argparse
import hashlib
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon import defines

def debug_banner(name):
    p = os.path.abspath(__file__)
    try:
        sha = hashlib.sha1(open(p, "rb").read()).hexdigest()[:10]
    except Exception:
        sha = "unknown"
    print(f"\n=== {name} START ===")
    print(f"__file__: {p}")
    print(f"cwd     : {os.getcwd()}")
    print(f"mtime   : {time.ctime(os.path.getmtime(p))}")
    print(f"sha1    : {sha}")
    print(f"python  : {os.sys.executable}\n")

class MIoTResource(Resource):
    def __init__(self, name="MIoTResource", coap_server=None):
        super(MIoTResource, self).__init__(name, coap_server, visible=True, observable=False, allow_children=True)

    def render_POST(self, request):
        try:
            print(f"\n=== Received POST to /miot/ ===")
            print(f"Payload: {request.payload}")
            data = json.loads(request.payload)
            print(f"Parsed JSON: {data}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")

        # Build NON-confirmable response to match client
        res = request
        res.code = defines.Codes.CREATED.number
        res.mid = request.mid
        res.token = request.token
        res.type = defines.Types['NON']  # Match NON type
        res.payload = "OK"
        return res

class CoAPServer(CoAP):
    def __init__(self, host, port, resource_path="miot/"):
        CoAP.__init__(self, (host, port))
        self.add_resource(resource_path, MIoTResource())
        print(f"CoAP server listening on {host}:{port}, resource: /{resource_path}")

def main():
    debug_banner("custom_coap_server")
    parser = argparse.ArgumentParser(description="Custom CoAP Server for MIoT")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=5683, help="Port number")
    parser.add_argument("--resource", default="miot/", help="Resource path (with trailing slash)")
    args = parser.parse_args()

    server = CoAPServer(args.host, args.port, resource_path=args.resource)
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print("Shutting down CoAP server...")
        server.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
