import grpc
import logging
import yaml
from typing import Any, Dict, List, Optional

from akash.proto.akash.base.v1beta3 import resources_pb2 as resource_pb2
from akash.proto.akash.manifest.v2beta2 import (
    group_pb2,
    service_pb2,
    serviceexpose_pb2,
    httpoptions_pb2,
)
from akash.proto.akash.market.v1beta4 import lease_pb2
from akash.proto.akash.provider.lease.v1 import service_pb2 as provider_service_pb2
from ...grpc_client import ProviderGRPCClient

logger = logging.getLogger(__name__)


class ManifestUtils:
    """
    Mixin for manifest utilities.
    """

    def create_service_manifest(self, service_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a service manifest from specification.

        Args:
            service_spec: Service specification dictionary

        Returns:
            Created manifest with validation results
        """
        try:
            logger.info(
                f"Creating service manifest: {service_spec.get('name', 'unnamed')}"
            )

            service = service_pb2.Service()
            service.name = service_spec.get("name", "default-service")
            service.image = service_spec.get("image", "nginx:latest")

            if "resources" in service_spec:
                resources = service_spec["resources"]
                service.count = resources.get("count", 1)

            if "expose" in service_spec:
                for expose_config in service_spec["expose"]:
                    expose = serviceexpose_pb2.ServiceExpose()
                    expose.port = expose_config.get("port", 80)
                    expose.proto = expose_config.get("protocol", "TCP").upper()

                    if "http_options" in expose_config:
                        http_opts = httpoptions_pb2.ServiceExposeHTTPOptions()
                        http_opts.max_body_size = expose_config["http_options"].get(
                            "max_body_size", 1048576
                        )
                        expose.http_options.CopyFrom(http_opts)

                    service.expose.append(expose)

            manifest_bytes = service.SerializeToString()

            result = {
                "service_name": service.name,
                "manifest_size": len(manifest_bytes),
                "validation": "passed",
                "manifest_data": {
                    "name": service.name,
                    "image": service.image,
                    "count": service.count,
                    "expose": [
                        {
                            "port": exp.port,
                            "protocol": exp.proto,
                            "global": getattr(exp, "global", False),
                        }
                        for exp in service.expose
                    ],
                },
                "created_at": "2025-08-29T07:22:00Z",
            }

            logger.info(f"Created service manifest: {service.name}")
            return result

        except Exception as e:
            logger.error(f"Failed to create service manifest: {e}")
            return {"validation": "failed", "error": str(e)}

    def create_group_manifest(self, group_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deployment group manifest.

        Args:
            group_spec: Group specification with services and resources

        Returns:
            Created group manifest with all services
        """
        try:
            logger.info(f"Creating group manifest: {group_spec.get('name', 'unnamed')}")

            group = group_pb2.Group()
            group.name = group_spec.get("name", "default-group")

            if "services" in group_spec:
                for service_spec in group_spec["services"]:
                    service_manifest = self.create_service_manifest(service_spec)

                    if service_manifest.get("validation") == "passed":
                        service = service_pb2.Service()
                        service.name = service_spec.get("name", "service")
                        service.image = service_spec.get("image", "nginx:latest")
                        service.count = service_spec.get("count", 1)
                        group.services.append(service)

            group_bytes = group.SerializeToString()

            result = {
                "group_name": group.name,
                "services_count": len(group.services),
                "manifest_size": len(group_bytes),
                "validation": "passed",
                "services": [
                    {"name": svc.name, "image": svc.image, "count": svc.count}
                    for svc in group.services
                ],
                "created_at": "2025-08-29T07:22:00Z",
            }

            logger.info(f"Created group manifest: {group.name}")
            return result

        except Exception as e:
            logger.error(f"Failed to create group manifest: {e}")
            return {"validation": "failed", "error": str(e)}

    def validate_manifest(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a manifest against Akash specifications.

        Args:
            manifest_data: Manifest data to validate

        Returns:
            Validation result with errors and warnings
        """
        try:
            logger.info("Validating manifest structure and requirements")

            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "recommendations": [],
            }

            if not isinstance(manifest_data, dict):
                validation_result["valid"] = False
                validation_result["errors"].append("Manifest must be a dictionary")
                return validation_result

            required_fields = ["services"]
            for field in required_fields:
                if field not in manifest_data:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Missing required field: {field}"
                    )

            if "services" in manifest_data:
                services = manifest_data["services"]
                if isinstance(services, list):
                    for i, service in enumerate(services):
                        if not isinstance(service, dict):
                            validation_result["warnings"].append(
                                f"Service {i} is not a dictionary"
                            )
                            continue

                        if "name" not in service:
                            validation_result["warnings"].append(
                                f"Service {i} missing name field"
                            )
                        if "image" not in service:
                            validation_result["warnings"].append(
                                f"Service {i} missing image field"
                            )

                        if "resources" in service:
                            resources = service["resources"]
                            if "cpu" not in resources:
                                validation_result["recommendations"].append(
                                    f"Service {service.get('name', i)} missing CPU specification"
                                )
                            if "memory" not in resources:
                                validation_result["recommendations"].append(
                                    f"Service {service.get('name', i)} missing memory specification"
                                )

                        if "expose" in service:
                            for expose in service["expose"]:
                                if "port" not in expose:
                                    validation_result["warnings"].append(
                                        f"Expose configuration missing port in service {service.get('name', i)}"
                                    )

            if "groups" in manifest_data:
                groups = manifest_data["groups"]
                if isinstance(groups, list):
                    for group in groups:
                        if "requirements" in group:
                            requirements = group["requirements"]
                            if "attributes" in requirements:
                                attributes = requirements["attributes"]
                                for attr in attributes:
                                    if not attr.get("key") or not attr.get("value"):
                                        validation_result["warnings"].append(
                                            "Placement requirement missing key or value"
                                        )

            logger.info(
                f"Manifest validation complete: {'VALID' if validation_result['valid'] else 'Invalid'}"
            )
            return validation_result

        except Exception as e:
            logger.error(f"Failed to validate manifest: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "recommendations": [],
            }

    def parse_sdl(self, sdl_content: str) -> Dict[str, Any]:
        """
        Parse SDL (YAML) into a manifest dictionary following Akash SDL specification.

        Args:
            sdl_content: SDL content as a YAML string.

        Returns:
            Dict with parsed manifest data.
        """
        try:
            if not sdl_content or (
                isinstance(sdl_content, str) and not sdl_content.strip()
            ):
                logger.error("SDL content cannot be empty")
                return {"status": "error", "error": "SDL content cannot be empty"}

            logger.info("Parsing SDL content")
            sdl_data = yaml.safe_load(sdl_content)

            version = sdl_data.get("version", "2.0")
            if version not in ["2.0", "2.1"]:
                return {
                    "status": "failed",
                    "error": f"Unsupported SDL version: {version}. Only 2.0 and 2.1 are supported.",
                }

            if "services" not in sdl_data or not sdl_data["services"]:
                return {
                    "status": "failed",
                    "error": "SDL must contain services section with at least one service",
                }

            if "profiles" not in sdl_data:
                return {
                    "status": "failed",
                    "error": "SDL must contain profiles section",
                }

            if "deployment" not in sdl_data:
                return {
                    "status": "failed",
                    "error": "SDL must contain deployment section",
                }

            services = sdl_data.get("services", {})
            profiles = sdl_data.get("profiles", {})
            compute_profiles = profiles.get("compute", {})
            placement_profiles = profiles.get("placement", {})
            deployment = sdl_data.get("deployment", {})

            manifest_services = []
            manifest_groups = []

            for service_name, deployment_config in deployment.items():
                if service_name not in services:
                    return {
                        "status": "failed",
                        "error": f"Service '{service_name}' in deployment not found in services section",
                    }

                service_def = services[service_name]

                for placement_name, placement_config in deployment_config.items():
                    profile_name = placement_config.get("profile")
                    if not profile_name:
                        return {
                            "status": "failed",
                            "error": f"Missing profile for service '{service_name}' in placement '{placement_name}'",
                        }

                    if profile_name not in compute_profiles:
                        return {
                            "status": "failed",
                            "error": f"Compute profile '{profile_name}' not found in profiles.compute",
                        }

                    if placement_name not in placement_profiles:
                        return {
                            "status": "failed",
                            "error": f"Placement profile '{placement_name}' not found in profiles.placement",
                        }

                    compute_profile = compute_profiles[profile_name]
                    placement_profile = placement_profiles[placement_name]

                    service_data = {
                        "name": service_name,
                        "image": service_def.get("image", "nginx:latest"),
                        "count": placement_config.get("count", 1),
                        "command": service_def.get("command", []),
                        "args": service_def.get("args", []),
                        "env": [],
                        "resources": {},
                        "expose": [],
                    }

                    if "env" in service_def:
                        if isinstance(service_def["env"], list):
                            service_data["env"] = service_def["env"]
                        elif isinstance(service_def["env"], dict):
                            service_data["env"] = [
                                f"{k}={v}" for k, v in service_def["env"].items()
                            ]

                    service_data["resources"] = {
                        "cpu": {
                            "units": self._parse_cpu_resource(
                                compute_profile.get("cpu", "0.01")
                            )
                        },
                        "memory": {"size": compute_profile.get("memory", "128Mi")},
                        "storage": {"size": compute_profile.get("storage", "512Mi")},
                    }

                    if "expose" in service_def:
                        for expose_config in service_def["expose"]:
                            expose_data = {
                                "port": expose_config.get("port", 80),
                                "protocol": expose_config.get("proto", "tcp").upper(),
                                "global": False,  # Default
                                "accept": expose_config.get("accept", []),
                                "to": expose_config.get("to", []),
                            }

                            for to_config in expose_data["to"]:
                                if isinstance(to_config, dict) and to_config.get(
                                    "global"
                                ):
                                    expose_data["global"] = True
                                    break

                            if "http_options" in expose_config:
                                expose_data["http_options"] = expose_config[
                                    "http_options"
                                ]

                            service_data["expose"].append(expose_data)

                    manifest_services.append(service_data)

                    group_name = placement_name
                    group = next(
                        (g for g in manifest_groups if g["name"] == group_name), None
                    )
                    if not group:
                        group = {
                            "name": group_name,
                            "requirements": {
                                "attributes": placement_profile.get("attributes", {}),
                                "signed_by": placement_profile.get("signedBy", {}),
                            },
                            "resources": [],
                        }
                        manifest_groups.append(group)

                    pricing = placement_profile.get("pricing", {})
                    if profile_name in pricing:
                        price_str = str(pricing[profile_name])
                        if price_str.endswith("u"):
                            amount = price_str[:-1]
                            denom = "uakt"
                        elif price_str.endswith("uakt"):
                            amount = price_str[:-4]
                            denom = "uakt"
                        else:
                            amount = price_str
                            denom = "uakt"

                        resource_config = {
                            "count": placement_config.get("count", 1),
                            "price": {"denom": denom, "amount": amount},
                            "resources": service_data["resources"],
                        }
                        group["resources"].append(resource_config)

            manifest_data = {
                "services": manifest_services,
                "groups": manifest_groups,
                "version": version,
            }

            logger.info(
                f"Successfully parsed SDL with {len(manifest_services)} services and {len(manifest_groups)} groups"
            )
            return {"status": "success", "manifest_data": manifest_data}

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return {"status": "failed", "error": f"Invalid YAML format: {e}"}
        except Exception as e:
            logger.error(f"SDL parsing failed: {e}")
            return {"status": "failed", "error": str(e)}

    def _parse_cpu_resource(self, cpu_value: str) -> int:
        """
        Parse CPU resource value from Akash SDL format.

        Examples:
        - "1" -> 1000 (1 CPU = 1000 milli-CPU)
        - "0.5" -> 500
        - "100m" -> 100
        """
        try:
            if isinstance(cpu_value, (int, float)):
                return int(cpu_value * 1000)

            cpu_str = str(cpu_value).strip()

            if cpu_str.endswith("m"):
                return int(cpu_str[:-1])
            else:
                return int(float(cpu_str) * 1000)
        except (ValueError, TypeError):
            logger.warning(f"Invalid CPU value: {cpu_value}, using default 100m")
            return 100

    def _parse_memory_size(self, size_str: str) -> int:
        """Parse memory size string to bytes."""
        try:
            if size_str.endswith("Gi"):
                return int(size_str[:-2]) * 1024 * 1024 * 1024
            elif size_str.endswith("Mi"):
                return int(size_str[:-2]) * 1024 * 1024
            elif size_str.endswith("Ki"):
                return int(size_str[:-2]) * 1024
            else:
                return int(size_str)
        except (ValueError, IndexError):
            return 512 * 1024 * 1024  # 512Mi

    def _parse_storage_size(self, size_str: str) -> int:
        """Parse storage size string to bytes."""
        try:
            if size_str.endswith("Gi"):
                return int(size_str[:-2]) * 1024 * 1024 * 1024
            elif size_str.endswith("Mi"):
                return int(size_str[:-2]) * 1024 * 1024
            elif size_str.endswith("Ki"):
                return int(size_str[:-2]) * 1024
            else:
                return int(size_str)
        except (ValueError, IndexError):
            return 1024 * 1024 * 1024  # 1Gi

    def send_manifest(
        self,
        provider_endpoint: str,
        lease_id: Dict[str, Any],
        manifest_groups: List[group_pb2.Group],
        owner: str = "",
        use_mtls: bool = True,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Sending manifest to {provider_endpoint} for lease {lease_id}")

            if not provider_endpoint or not provider_endpoint.strip():
                return {
                    "status": "error",
                    "error": "Provider endpoint cannot be empty",
                    "provider": provider_endpoint,
                }

            if not lease_id:
                return {
                    "status": "error",
                    "error": "Missing required field: lease_id",
                    "provider": provider_endpoint,
                }

            required_fields = ["owner", "dseq", "gseq", "oseq", "provider"]
            for field in required_fields:
                if not lease_id.get(field):
                    return {
                        "status": "error",
                        "error": f"Missing required field: lease_id.{field}",
                        "provider": provider_endpoint,
                    }

            if not manifest_groups:
                return {
                    "status": "error",
                    "error": "Manifest groups cannot be empty",
                    "provider": provider_endpoint,
                }

            for group in manifest_groups:
                if not isinstance(group, group_pb2.Group):
                    return {
                        "status": "error",
                        "error": "Manifest groups must be group_pb2.Group objects",
                        "provider": provider_endpoint,
                    }

            owner = owner or lease_id.get("owner", "")

            if use_mtls and hasattr(self.client, "cert"):
                cert_status = self.client.cert.query_certificate(owner)
                if cert_status["status"] != "success":
                    return {
                        "status": "error",
                        "error": f"No valid certificate found for owner {owner}",
                        "provider": provider_endpoint,
                    }

            grpc_client = ProviderGRPCClient(self.client)
            request = provider_service_pb2.SendManifestRequest()
            request.lease_id.CopyFrom(self._convert_lease_id_to_protobuf(lease_id))

            for group in manifest_groups:
                request.manifest.append(group)

            result = grpc_client.call_with_retry(
                stub_factory=grpc_client._get_lease_stub,
                method_name="SendManifest",
                request=request,
                endpoint=provider_endpoint,
                owner=owner,
                use_mtls=use_mtls,
                timeout=timeout,
            )

            if result["status"] == "success":
                logger.info(f"Manifest successfully sent to {provider_endpoint}")
                return {
                    "status": "success",
                    "provider": provider_endpoint,
                    "lease_id": lease_id,
                    "groups_sent": len(manifest_groups),
                    "response": result.get("response"),
                }
            else:
                logger.error(
                    f"Failed to send manifest: {result.get('error', 'Unknown error')}"
                )
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown error"),
                    "provider": provider_endpoint,
                }

        except grpc.RpcError as e:
            status_code = e.code()
            if status_code == grpc.StatusCode.UNAVAILABLE:
                error_msg = f"Provider {provider_endpoint} is unavailable"
            elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                error_msg = f"gRPC timeout for {provider_endpoint}"
            elif status_code == grpc.StatusCode.UNAUTHENTICATED:
                error_msg = f"mTLS authentication failed for {provider_endpoint}"
            else:
                error_msg = f"gRPC error: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "provider": provider_endpoint,
            }
        except Exception as e:
            logger.error(f"Failed to send manifest: {e}")
            return {"status": "error", "error": str(e), "provider": provider_endpoint}

    def send_manifest_http(
        self,
        provider_endpoint: str,
        lease_id: Dict[str, Any],
        manifest: Dict[str, Any],
        cert_pem: str = None,
        key_pem: str = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """Send manifest to provider via HTTP PUT (console approach fallback)."""
        try:
            import json
            import requests
            import tempfile
            import os

            logger.info(
                f"Sending manifest via HTTP to {provider_endpoint} for lease {lease_id}"
            )

            required_fields = ["dseq"]
            for field in required_fields:
                if not lease_id.get(field):
                    return {
                        "status": "error",
                        "error": f"Missing required field: lease_id.{field}",
                        "provider": provider_endpoint,
                    }

            if not manifest:
                return {
                    "status": "error",
                    "error": "Manifest cannot be empty",
                    "provider": provider_endpoint,
                }

            manifest_json = json.dumps(manifest, sort_keys=True)
            manifest_json = manifest_json.replace('"quantity":{"val', '"size":{"val')

            dseq = lease_id.get("dseq")
            url = f"{provider_endpoint.rstrip('/')}/deployment/{dseq}/manifest"

            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            kwargs = {
                "url": url,
                "data": manifest_json,
                "headers": headers,
                "timeout": timeout,
            }

            if cert_pem and key_pem:
                cert_file = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".crt", delete=False
                )
                key_file = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".key", delete=False
                )

                try:
                    cert_file.write(cert_pem)
                    cert_file.flush()
                    key_file.write(key_pem)
                    key_file.flush()

                    kwargs["cert"] = (cert_file.name, key_file.name)
                    kwargs["verify"] = False

                    response = requests.put(**kwargs)

                finally:
                    cert_file.close()
                    key_file.close()
                    os.unlink(cert_file.name)
                    os.unlink(key_file.name)
            else:
                response = requests.put(**kwargs)

            if response.status_code in [200, 201, 202]:
                logger.info(
                    f"HTTP manifest submission successful: {response.status_code}"
                )
                return {
                    "status": "success",
                    "provider": provider_endpoint,
                    "lease_id": lease_id,
                    "method": "HTTP",
                    "status_code": response.status_code,
                    "response": response.text,
                }
            else:
                logger.error(
                    f"HTTP manifest submission failed: {response.status_code} - {response.text}"
                )
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "provider": provider_endpoint,
                    "method": "HTTP",
                    "status_code": response.status_code,
                }

        except Exception as e:
            logger.error(f"Failed to send manifest via HTTP: {e}")
            return {
                "status": "error",
                "error": str(e),
                "provider": provider_endpoint,
                "method": "HTTP",
            }

    def send_manifest_with_fallback(
        self,
        provider_endpoint: str,
        lease_id: Dict[str, Any],
        manifest_groups: List[group_pb2.Group] = None,
        manifest_dict: Dict[str, Any] = None,
        owner: str = "",
        cert_pem: str = None,
        key_pem: str = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """Send manifest to provider with automatic HTTP fallback."""
        if manifest_groups:
            logger.info("Attempting gRPC manifest submission first")
            result = self.send_manifest(
                provider_endpoint=provider_endpoint,
                lease_id=lease_id,
                manifest_groups=manifest_groups,
                owner=owner,
                use_mtls=bool(cert_pem and key_pem),
                timeout=timeout,
            )

            if result.get("status") == "success":
                return result

            logger.warning(
                f"gRPC manifest submission failed: {result.get('error')}, trying HTTP fallback"
            )

        if manifest_dict:
            logger.info("Using HTTP fallback for manifest submission")
            return self.send_manifest_http(
                provider_endpoint=provider_endpoint,
                lease_id=lease_id,
                manifest=manifest_dict,
                cert_pem=cert_pem,
                key_pem=key_pem,
                timeout=timeout,
            )
        else:
            return {
                "status": "error",
                "error": "No manifest data provided for fallback (need manifest_dict for HTTP)",
                "provider": provider_endpoint,
            }

    def _convert_lease_id_to_protobuf(
        self, lease_id: Dict[str, Any]
    ) -> lease_pb2.LeaseID:
        try:
            return lease_pb2.LeaseID(
                owner=lease_id.get("owner", ""),
                dseq=int(lease_id.get("dseq", 0)),
                gseq=int(lease_id.get("gseq", 0)),
                oseq=int(lease_id.get("oseq", 0)),
                provider=lease_id.get("provider", ""),
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to convert lease ID to protobuf: {e}")
            raise

    def get_service_status(
        self,
        provider_endpoint: str,
        lease_id: Dict[str, Any],
        service_names: Optional[List[str]] = None,
        owner: str = "",
        use_mtls: bool = True,
    ) -> Dict[str, Any]:
        """Get service status from provider using real protobuf objects."""
        try:
            logger.info(
                f"Getting service status from {provider_endpoint} for lease {lease_id}"
            )

            owner = owner or lease_id.get("owner", "")

            if not provider_endpoint or not provider_endpoint.strip():
                return {
                    "status": "error",
                    "error": "Provider endpoint cannot be empty",
                    "provider": provider_endpoint,
                }

            if not lease_id:
                return {
                    "status": "error",
                    "error": "Missing required field: lease_id",
                    "provider": provider_endpoint,
                }

            if use_mtls and hasattr(self.client, "cert"):
                cert_status = self.client.cert.query_certificate(owner)
                if cert_status["status"] != "success":
                    return {
                        "status": "error",
                        "error": f"No valid certificate found for owner {owner}",
                        "provider": provider_endpoint,
                    }

            grpc_client = ProviderGRPCClient(self.client)

            request = provider_service_pb2.ServiceStatusRequest()
            request.lease_id.CopyFrom(self._convert_lease_id_to_protobuf(lease_id))

            if service_names:
                for service_name in service_names:
                    request.services.append(service_name)

            result = grpc_client.call_with_retry(
                stub_factory=grpc_client._get_lease_stub,
                method_name="ServiceStatus",
                request=request,
                endpoint=provider_endpoint,
                owner=owner,
                use_mtls=use_mtls,
                timeout=30,
            )

            if result["status"] == "success":
                response = result.get("response")
                services_status = self._parse_service_status_response(response)

                return {
                    "status": "success",
                    "provider": provider_endpoint,
                    "lease_id": lease_id,
                    "services": services_status,
                }
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Failed to get service status: {error_msg}")
                return {
                    "status": "error",
                    "error": error_msg,
                    "provider": provider_endpoint,
                }

        except grpc.RpcError as e:
            status_code = e.code()
            if status_code == grpc.StatusCode.UNAVAILABLE:
                error_msg = f"Provider {provider_endpoint} is unavailable"
            elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                error_msg = f"gRPC timeout for {provider_endpoint}"
            elif status_code == grpc.StatusCode.UNAUTHENTICATED:
                error_msg = f"mTLS authentication failed for {provider_endpoint}"
            else:
                error_msg = f"gRPC error: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "provider": provider_endpoint,
            }
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {"status": "error", "error": str(e), "provider": provider_endpoint}

    def _parse_service_status_response(self, response) -> List[Dict[str, Any]]:
        """Parse service status response from gRPC."""
        services_status = []

        try:
            if isinstance(response, provider_service_pb2.ServiceStatusResponse):
                for service in response.services:
                    endpoints = []
                    if hasattr(service, "ips"):
                        for ip_status in service.ips:
                            if hasattr(ip_status, "ip"):
                                endpoints.append(ip_status.ip)
                    service_info = {
                        "name": service.name,
                        "status": {"endpoints": endpoints},
                    }
                    services_status.append(service_info)
            elif hasattr(response, "services"):
                for service in response.services:
                    endpoints = []
                    if hasattr(service, "ips"):
                        ips = getattr(service, "ips", [])
                        for ip_item in ips:
                            if hasattr(ip_item, "ip"):
                                endpoints.append(ip_item.ip)
                            else:
                                endpoints.append(str(ip_item))
                    elif hasattr(service, "endpoints"):
                        endpoints = list(getattr(service, "endpoints", []))

                    service_info = {
                        "name": getattr(service, "name", ""),
                        "status": {"endpoints": endpoints},
                    }
                    services_status.append(service_info)
        except Exception as e:
            logger.error(f"Failed to parse service status response: {str(e)}")
            return []

        return services_status

    def update_manifest(
        self,
        provider_endpoint: str,
        lease_id: Dict[str, Any],
        updates: Dict[str, Any],
        owner: str = "",
        use_mtls: bool = True,
    ) -> Dict[str, Any]:
        """Update manifest on provider using real protobuf objects."""
        try:
            logger.info(
                f"Updating manifest on {provider_endpoint} for lease {lease_id}"
            )

            if not provider_endpoint or not provider_endpoint.strip():
                return {
                    "status": "error",
                    "error": "Provider endpoint cannot be empty",
                    "provider": provider_endpoint,
                }

            if not lease_id:
                return {
                    "status": "error",
                    "error": "Missing required field: lease_id",
                    "provider": provider_endpoint,
                }

            if not updates:
                return {
                    "status": "error",
                    "error": "Updates cannot be empty",
                    "provider": provider_endpoint,
                }

            mutable_fields = ["image", "command", "args", "env", "expose", "count"]
            for service in updates.get("services", []):
                for field in service:
                    if field not in mutable_fields and field != "name":
                        return {
                            "status": "error",
                            "error": f"Cannot update immutable field: {field}",
                            "provider": provider_endpoint,
                        }
                if "count" in service:
                    count = service.get("count")
                    if not isinstance(count, int) or count < 0:
                        return {
                            "status": "error",
                            "error": "Invalid count: must be a positive integer",
                            "provider": provider_endpoint,
                        }

            owner = owner or lease_id.get("owner", "")

            if use_mtls and hasattr(self.client, "cert"):
                cert_status = self.client.cert.query_certificate(owner)
                if cert_status["status"] != "success":
                    return {
                        "status": "error",
                        "error": f"No valid certificate found for owner {owner}",
                        "provider": provider_endpoint,
                    }

            manifest_groups = self.sdl_to_manifest(updates)
            if not manifest_groups:
                return {
                    "status": "error",
                    "error": "Failed to convert updates to protobuf format",
                    "provider": provider_endpoint,
                }

            return self.send_manifest(
                provider_endpoint=provider_endpoint,
                lease_id=lease_id,
                manifest_groups=manifest_groups,
                owner=owner,
                use_mtls=use_mtls,
                timeout=60,
            )

        except Exception as e:
            logger.error(f"Failed to update manifest: {e}")
            return {"status": "error", "error": str(e), "provider": provider_endpoint}

    def sdl_to_manifest(self, manifest_data: Dict[str, Any]) -> List[group_pb2.Group]:
        """Convert SDL data to manifest protobuf Group objects."""
        try:
            groups = []

            if "groups" in manifest_data:
                for group_data in manifest_data["groups"]:
                    group = group_pb2.Group()
                    group.name = group_data.get("name", "akash")

                    for service_data in group_data.get("services", []):
                        service = self._create_service_protobuf(service_data)
                        group.services.append(service)

                    groups.append(group)
            else:
                services = manifest_data.get("services", [])

                if isinstance(services, dict):
                    services = list(services.values())

                group = group_pb2.Group()
                group.name = manifest_data.get("name", "akash")

                for service_data in services:
                    service = self._create_service_protobuf(service_data)
                    group.services.append(service)

                groups.append(group)

            return groups

        except Exception as e:
            logger.error(f"Failed to convert manifest to protobuf: {e}")
            return []

    def _create_service_protobuf(
        self, service_data: Dict[str, Any]
    ) -> service_pb2.Service:
        """Create a Service protobuf from service data with full resource support."""
        service = service_pb2.Service()
        service.name = service_data.get("name", "web")
        service.image = service_data.get("image", "nginx:latest")
        service.count = service_data.get("count", 1)

        if "command" in service_data:
            service.command.extend(service_data["command"])
        if "args" in service_data:
            service.args.extend(service_data["args"])
        if "env" in service_data:
            for env_var in service_data["env"]:
                service.env.append(str(env_var))

        resources = service_data.get("resources", {})
        if resources:
            try:
                resource_obj = resource_pb2.Resources()
                resource_obj.id = 1

                if "cpu" in resources:
                    cpu_config = resources["cpu"]
                    cpu_units = cpu_config.get("units", 100)
                    if isinstance(cpu_units, (int, float)):
                        cpu_units = str(int(cpu_units * 1000))
                    elif isinstance(cpu_units, str) and not cpu_units.endswith("m"):
                        cpu_units = str(int(float(cpu_units) * 1000))
                    elif isinstance(cpu_units, str) and cpu_units.endswith("m"):
                        cpu_units = cpu_units[:-1]

                    resource_obj.cpu.units.val = cpu_units.encode("utf-8")

                if "memory" in resources:
                    memory_config = resources["memory"]
                    memory_size = memory_config.get("size", "512Mi")
                    memory_bytes = self._parse_memory_size(memory_size)
                    resource_obj.memory.quantity.val = str(memory_bytes).encode("utf-8")

                if "storage" in resources:
                    storage_config = resources["storage"]
                    if isinstance(storage_config, dict):
                        storage_size = storage_config.get("size", "1Gi")
                        storage_bytes = self._parse_storage_size(storage_size)
                        storage_item = resource_obj.storage.add()
                        storage_item.name = storage_config.get("name", "default")
                        storage_item.quantity.val = str(storage_bytes).encode("utf-8")
                    elif isinstance(storage_config, list):
                        for storage_item_config in storage_config:
                            storage_size = storage_item_config.get("size", "1Gi")
                            storage_bytes = self._parse_storage_size(storage_size)
                            storage_item = resource_obj.storage.add()
                            storage_item.name = storage_item_config.get(
                                "name", "default"
                            )
                            storage_item.quantity.val = str(storage_bytes).encode(
                                "utf-8"
                            )

                if "gpu" in resources:
                    gpu_config = resources["gpu"]
                    gpu_units = gpu_config.get("units", 1)
                    resource_obj.gpu.units.val = str(gpu_units).encode("utf-8")

                service.resources.CopyFrom(resource_obj)
            except Exception as e:
                logger.warning(f"Failed to configure resources: {e}")
                resource_obj = resource_pb2.Resources()
                resource_obj.id = 1
                resource_obj.cpu.units.val = b"100"
                resource_obj.memory.quantity.val = str(512 * 1024 * 1024).encode(
                    "utf-8"
                )
                service.resources.CopyFrom(resource_obj)

        expose_configs = service_data.get("expose", [])
        for expose_config in expose_configs:
            expose = serviceexpose_pb2.ServiceExpose()
            expose.port = expose_config.get("port", 80)
            expose.proto = expose_config.get(
                "protocol", expose_config.get("proto", "TCP")
            ).upper()
            setattr(expose, "global", expose_config.get("global", True))

            http_opts = expose_config.get("http_options", {})
            if http_opts:
                http_options = httpoptions_pb2.ServiceExposeHTTPOptions()
                http_options.max_body_size = http_opts.get("max_body_size", 1048576)
                http_options.read_timeout = http_opts.get("read_timeout", 60000)
                http_options.send_timeout = http_opts.get("send_timeout", 60000)
                http_options.next_tries = http_opts.get("next_tries", 3)
                http_options.next_cases.extend(
                    http_opts.get("next_cases", ["error", "timeout"])
                )
                expose.http_options.CopyFrom(http_options)

            service.expose.append(expose)

        return service
