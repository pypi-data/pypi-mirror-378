import json
import base64

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings
from pathlib import Path
from django.utils.cache import patch_vary_headers

from utils.api import api_login_required

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from .models import Node, NetMessage, NodeRole
from .utils import capture_screenshot, save_screenshot


@api_login_required
def node_list(request):
    """Return a JSON list of all known nodes."""

    nodes = [
        {
            "hostname": node.hostname,
            "address": node.address,
            "port": node.port,
            "last_seen": node.last_seen,
            "features": list(node.features.values_list("slug", flat=True)),
        }
        for node in Node.objects.prefetch_related("features")
    ]
    return JsonResponse({"nodes": nodes})


@csrf_exempt
def node_info(request):
    """Return information about the local node and sign ``token`` if provided."""

    node = Node.get_local()
    if node is None:
        node, _ = Node.register_current()

    token = request.GET.get("token", "")
    data = {
        "hostname": node.hostname,
        "address": node.address,
        "port": node.port,
        "mac_address": node.mac_address,
        "public_key": node.public_key,
        "features": list(node.features.values_list("slug", flat=True)),
    }

    if token:
        try:
            priv_path = (
                Path(node.base_path or settings.BASE_DIR)
                / "security"
                / f"{node.public_endpoint}"
            )
            private_key = serialization.load_pem_private_key(
                priv_path.read_bytes(), password=None
            )
            signature = private_key.sign(
                token.encode(),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            data["token_signature"] = base64.b64encode(signature).decode()
        except Exception:
            pass

    response = JsonResponse(data)
    response["Access-Control-Allow-Origin"] = "*"
    return response


def _add_cors_headers(request, response):
    origin = request.headers.get("Origin")
    if origin:
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Credentials"] = "true"
        allow_headers = request.headers.get(
            "Access-Control-Request-Headers", "Content-Type"
        )
        response["Access-Control-Allow-Headers"] = allow_headers
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        patch_vary_headers(response, ["Origin"])
    return response


@csrf_exempt
@api_login_required
def register_node(request):
    """Register or update a node from POSTed JSON data."""

    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "ok"})
        return _add_cors_headers(request, response)

    if request.method != "POST":
        response = JsonResponse({"detail": "POST required"}, status=400)
        return _add_cors_headers(request, response)

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        data = request.POST

    if hasattr(data, "getlist"):
        raw_features = data.getlist("features")
        if not raw_features:
            features = None
        elif len(raw_features) == 1:
            features = raw_features[0]
        else:
            features = raw_features
    else:
        features = data.get("features")

    hostname = data.get("hostname")
    address = data.get("address")
    port = data.get("port", 8000)
    mac_address = data.get("mac_address")
    public_key = data.get("public_key")
    token = data.get("token")
    signature = data.get("signature")

    if not hostname or not address or not mac_address:
        response = JsonResponse(
            {"detail": "hostname, address and mac_address required"}, status=400
        )
        return _add_cors_headers(request, response)

    verified = False
    if public_key and token and signature:
        try:
            pub = serialization.load_pem_public_key(public_key.encode())
            pub.verify(
                base64.b64decode(signature),
                token.encode(),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            verified = True
        except Exception:
            response = JsonResponse({"detail": "invalid signature"}, status=403)
            return _add_cors_headers(request, response)

    mac_address = mac_address.lower()
    defaults = {
        "hostname": hostname,
        "address": address,
        "port": port,
    }
    if verified:
        defaults["public_key"] = public_key

    node, created = Node.objects.get_or_create(
        mac_address=mac_address,
        defaults=defaults,
    )
    if not created:
        node.hostname = hostname
        node.address = address
        node.port = port
        update_fields = ["hostname", "address", "port"]
        if verified:
            node.public_key = public_key
            update_fields.append("public_key")
        node.save(update_fields=update_fields)
        if features is not None:
            if isinstance(features, (str, bytes)):
                feature_list = [features]
            else:
                feature_list = list(features)
            node.update_manual_features(feature_list)
        response = JsonResponse(
            {"id": node.id, "detail": f"Node already exists (id: {node.id})"}
        )
        return _add_cors_headers(request, response)

    if features is not None:
        if isinstance(features, (str, bytes)):
            feature_list = [features]
        else:
            feature_list = list(features)
        node.update_manual_features(feature_list)

    response = JsonResponse({"id": node.id})
    return _add_cors_headers(request, response)


@api_login_required
def capture(request):
    """Capture a screenshot of the site's root URL and record it."""

    url = request.build_absolute_uri("/")
    try:
        path = capture_screenshot(url)
    except Exception as exc:  # pragma: no cover - depends on selenium setup
        return JsonResponse({"detail": str(exc)}, status=500)
    node = Node.get_local()
    screenshot = save_screenshot(path, node=node, method=request.method)
    node_id = screenshot.node.id if screenshot and screenshot.node else None
    return JsonResponse({"screenshot": str(path), "node": node_id})


@csrf_exempt
@api_login_required
def public_node_endpoint(request, endpoint):
    """Public API endpoint for a node.

    - ``GET`` returns information about the node.
    - ``POST`` broadcasts the request body as a :class:`NetMessage`.
    """

    node = get_object_or_404(Node, public_endpoint=endpoint, enable_public_api=True)

    if request.method == "GET":
        data = {
            "hostname": node.hostname,
            "address": node.address,
            "port": node.port,
            "badge_color": node.badge_color,
            "last_seen": node.last_seen,
            "features": list(node.features.values_list("slug", flat=True)),
        }
        return JsonResponse(data)

    if request.method == "POST":
        NetMessage.broadcast(
            subject=request.method,
            body=request.body.decode("utf-8") if request.body else "",
            seen=[str(node.uuid)],
        )
        return JsonResponse({"status": "stored"})

    return JsonResponse({"detail": "Method not allowed"}, status=405)


@csrf_exempt
def net_message(request):
    """Receive a network message and continue propagation."""

    if request.method != "POST":
        return JsonResponse({"detail": "POST required"}, status=400)
    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"detail": "invalid json"}, status=400)

    signature = request.headers.get("X-Signature")
    sender_id = data.get("sender")
    if not signature or not sender_id:
        return JsonResponse({"detail": "signature required"}, status=403)
    node = Node.objects.filter(uuid=sender_id).first()
    if not node or not node.public_key:
        return JsonResponse({"detail": "unknown sender"}, status=403)
    try:
        public_key = serialization.load_pem_public_key(node.public_key.encode())
        public_key.verify(
            base64.b64decode(signature),
            request.body,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    except Exception:
        return JsonResponse({"detail": "invalid signature"}, status=403)

    msg_uuid = data.get("uuid")
    subject = data.get("subject", "")
    body = data.get("body", "")
    reach_name = data.get("reach")
    reach_role = None
    if reach_name:
        reach_role = NodeRole.objects.filter(name=reach_name).first()
    seen = data.get("seen", [])
    if not msg_uuid:
        return JsonResponse({"detail": "uuid required"}, status=400)
    msg, created = NetMessage.objects.get_or_create(
        uuid=msg_uuid,
        defaults={"subject": subject[:64], "body": body[:256], "reach": reach_role},
    )
    if not created:
        msg.subject = subject[:64]
        msg.body = body[:256]
        update_fields = ["subject", "body"]
        if reach_role and msg.reach_id != reach_role.id:
            msg.reach = reach_role
            update_fields.append("reach")
        msg.save(update_fields=update_fields)
    msg.propagate(seen=seen)
    return JsonResponse({"status": "propagated", "complete": msg.complete})


def last_net_message(request):
    """Return the most recent :class:`NetMessage`."""

    msg = NetMessage.objects.order_by("-created").first()
    if not msg:
        return JsonResponse({"subject": "", "body": ""})
    return JsonResponse({"subject": msg.subject, "body": msg.body})
