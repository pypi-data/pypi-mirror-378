import datetime
import logging
import os
import ssl
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from typing import Dict, Any, Optional

from .query import CertQuery
from .tx import CertTx
from .utils import CertUtils

logger = logging.getLogger(__name__)


class CertClient(CertQuery, CertTx, CertUtils):
    """
    Ccertificate client for mTLS-enabled gRPC communication.
    Integrates certificate creation with local file storage for provider authentication.
    """

    def __init__(self, akash_client):
        """
        Initialize certificate client with main Akash client.

        Args:
            akash_client: Parent AkashClient instance
        """
        self.akash_client = akash_client
        self.cert_dir = "certs"
        logger.info("Initialized CertClient with mTLS support")

    def verify_certificate_files(self) -> Dict[str, Any]:
        """
        Verify that certificate files exist and are readable for gRPC.

        Returns:
            Dict with verification status
        """
        try:
            cert_paths = {
                "client_cert": f"{self.cert_dir}/client.pem",
                "client_key": f"{self.cert_dir}/client-key.pem",
                "ca_cert": f"{self.cert_dir}/ca.pem",
            }

            verification = {"status": "success", "files": {}}

            for name, path in cert_paths.items():
                if os.path.exists(path):
                    try:
                        with open(path, "r") as f:
                            content = f.read()
                        verification["files"][name] = {
                            "exists": True,
                            "readable": True,
                            "size": len(content),
                        }
                    except Exception as e:
                        verification["files"][name] = {
                            "exists": True,
                            "readable": False,
                            "error": str(e),
                        }
                        verification["status"] = "partial"
                else:
                    verification["files"][name] = {"exists": False, "readable": False}
                    verification["status"] = "failed"

            logger.info(f"Certificate verification: {verification['status']}")
            return verification

        except Exception as e:
            logger.error(f"Certificate verification failed: {e}")
            return {"status": "error", "error": str(e)}

    def cleanup_certificates(self) -> Dict[str, Any]:
        """
        Clean up locally stored certificate files.

        Returns:
            Dict with cleanup status
        """
        try:
            if not os.path.exists(self.cert_dir):
                return {
                    "status": "success",
                    "message": "No certificate files to clean up",
                }

            cert_files = ["client.pem", "client-key.pem", "ca.pem"]

            cleaned = []
            for cert_file in cert_files:
                file_path = f"{self.cert_dir}/{cert_file}"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned.append(cert_file)

            try:
                os.rmdir(self.cert_dir)
            except OSError:
                pass

            logger.info(f"Cleaned up {len(cleaned)} certificate files")
            return {
                "status": "success",
                "cleaned_files": cleaned,
                "message": f"Removed {len(cleaned)} certificate files",
            }

        except Exception as e:
            logger.error(f"Certificate cleanup failed: {e}")
            return {"status": "error", "error": str(e)}

    def create_ssl_context(self) -> Dict[str, Any]:
        """
        Create SSL context for mTLS connections.

        Returns:
            Dict with SSL context or error information
        """
        try:
            cert_paths = self.get_cert_file_paths()
            client_cert_path = cert_paths["client_cert"]
            client_key_path = cert_paths["client_key"]
            ca_cert_path = cert_paths["ca_cert"]

            missing_files = []
            for path in [client_cert_path, client_key_path, ca_cert_path]:
                if not os.path.exists(path):
                    missing_files.append(path)

            if missing_files:
                return {
                    "status": "error",
                    "error": f"Certificate files not found: {', '.join(missing_files)}",
                }

            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_REQUIRED

            context.load_cert_chain(client_cert_path, client_key_path)

            context.load_verify_locations(ca_cert_path)

            return {"status": "success", "ssl_context": context}

        except ssl.SSLError as e:
            logger.error(f"SSL context creation failed: {e}")
            return {"status": "error", "error": f"SSL error: {e}"}
        except (IOError, OSError) as e:
            logger.error(f"SSL context creation failed: {e}")
            return {"status": "error", "error": f"File read error: {e}"}
        except Exception as e:
            logger.error(f"SSL context creation failed: {e}")
            return {"status": "error", "error": str(e)}

    def validate_ssl_certificate(self, cert_pem: str) -> bool:
        """
        Validate SSL certificate PEM format.

        Args:
            cert_pem: Certificate in PEM format

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            try:
                if not cert_pem or not isinstance(cert_pem, str):
                    logger.error("Certificate data is empty or invalid")
                    return False
            except TypeError:
                if not cert_pem:
                    logger.error("Certificate data is empty or invalid")
                    return False

            if "-----BEGIN CERTIFICATE-----" not in cert_pem:
                logger.error("Missing BEGIN CERTIFICATE marker")
                return False

            if "-----END CERTIFICATE-----" not in cert_pem:
                logger.error("Missing END CERTIFICATE marker")
                return False

            try:
                x509.load_pem_x509_certificate(cert_pem.encode())
                return True
            except Exception as parse_error:
                logger.error(f"Certificate parsing failed: {parse_error}")
                return False

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def get_cert_file_paths(self) -> Dict[str, str]:
        """
        Get standard certificate file paths.

        Returns:
            Dict with certificate file paths
        """
        return {
            "client_cert": f"{self.cert_dir}/client.pem",
            "client_key": f"{self.cert_dir}/client-key.pem",
            "ca_cert": f"{self.cert_dir}/ca.pem",
        }

    def check_cert_files_exist(self) -> bool:
        """
        Check if certificate files exist.

        Returns:
            bool: True if all certificate files exist, False otherwise
        """
        cert_paths = self.get_cert_file_paths()

        for name, path in cert_paths.items():
            if not os.path.exists(path):
                return False

        return True

    def check_expiry(self, certificate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check certificate expiry status.

        Args:
            certificate: Certificate dictionary from query_certificates or similar

        Returns:
            Dict with expiry information:
                - expired: bool
                - valid_until: datetime string (if parseable)
                - days_remaining: int (if not expired)
                - message: str description
        """
        try:
            import base64
            from datetime import datetime, timezone

            cert_b64 = None
            if isinstance(certificate, dict):
                if (
                    "certificate" in certificate
                    and "cert" in certificate["certificate"]
                ):
                    cert_b64 = certificate["certificate"]["cert"]
                elif "cert" in certificate:
                    cert_b64 = certificate["cert"]

            if not cert_b64:
                return {
                    "expired": False,
                    "valid_until": None,
                    "days_remaining": None,
                    "message": "Unable to extract certificate data",
                }

            cert_der = base64.b64decode(cert_b64)

            cert = x509.load_der_x509_certificate(cert_der)

            not_after = cert.not_valid_after_utc
            now = datetime.now(timezone.utc)

            days_remaining = (not_after - now).days

            return {
                "expired": now > not_after,
                "valid_until": not_after.isoformat(),
                "days_remaining": days_remaining if days_remaining > 0 else 0,
                "message": f"Certificate {'expired' if now > not_after else f'valid for {days_remaining} days'}",
            }

        except Exception as e:
            logger.error(f"Failed to check certificate expiry: {e}")
            return {
                "expired": False,
                "valid_until": None,
                "days_remaining": None,
                "message": f"Error checking expiry: {str(e)}",
            }

    def _generate_mtls_certificate(self, wallet, ca_cert_path: Optional[str] = None):
        """
        Private method to generate mTLS certificate.

        Args:
            wallet: Wallet for certificate generation
            ca_cert_path: Optional CA certificate path

        Returns:
            Tuple of (private_key, certificate)
        """
        private_key = ec.generate_private_key(ec.SECP256R1())

        wallet_id = wallet if isinstance(wallet, str) else wallet.address
        subject = issuer = self._create_x509_name(wallet_id)

        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(int(self._get_certificate_serial_for_owner(wallet_id), 16))
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .sign(private_key, hashes.SHA256())
        )

        return (private_key, certificate)

    def _create_x509_name(self, common_name: str) -> Any:
        """
        Create X509 name for certificate subject.

        Args:
            common_name: Common name for certificate

        Returns:
            X509 Name object
        """
        return x509.Name(
            [x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, common_name)]
        )

    def _get_certificate_serial_for_owner(self, owner: str) -> str:
        """
        Generate certificate serial for owner.

        Args:
            owner: Certificate owner

        Returns:
            Certificate serial number (16 characters)
        """
        import uuid

        return uuid.uuid4().hex[:16]
