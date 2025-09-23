import base64
import hashlib
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class CertUtils:
    """
    Mixin for certificate utilities.
    """

    def validate_certificate(self, cert_data: Dict) -> bool:
        """
        Validate certificate structure and data.

        Args:
            cert_data: Certificate data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            required_fields = ["serial", "certificate"]

            for field in required_fields:
                if field not in cert_data:
                    logger.error(f"Missing required field: {field}")
                    return False

            cert = cert_data["certificate"]
            cert_required_fields = ["state", "cert", "pubkey"]

            for field in cert_required_fields:
                if field not in cert:
                    logger.error(f"Missing required certificate field: {field}")
                    return False

            valid_states = ["valid", "revoked", "invalid"]
            if cert["state"] not in valid_states:
                logger.error(f"Invalid certificate state: {cert['state']}")
                return False

            try:
                base64.b64decode(cert["cert"])
                base64.b64decode(cert["pubkey"])
            except Exception:
                logger.error("Certificate data must be base64 encoded")
                return False

            if not self._validate_certificate_format(cert["cert"]):
                logger.error("Certificate data is not in valid X.509/PEM format")
                return False

            if not self._validate_public_key_format(cert["pubkey"]):
                logger.error("Public key data is not in valid format")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating certificate: {e}")
            return False

    def _validate_certificate_format(self, cert_b64: str) -> bool:
        """
        Validate that certificate data is in valid X.509/PEM format.

        Args:
            cert_b64: Base64 encoded certificate data

        Returns:
            bool: True if valid format, False otherwise
        """
        try:
            cert_data = base64.b64decode(cert_b64)
            cert_str = cert_data.decode()

            if (
                "-----BEGIN CERTIFICATE-----" in cert_str
                and "-----END CERTIFICATE-----" in cert_str
            ):
                return True

            logger.warning("Certificate not in expected PEM format")
            return False

        except Exception as e:
            logger.error(f"Certificate format validation failed: {e}")
            return False

    def _validate_public_key_format(self, pubkey_b64: str) -> bool:
        """
        Validate that public key data is in valid format.

        Args:
            pubkey_b64: Base64 encoded public key data

        Returns:
            bool: True if valid format, False otherwise
        """
        try:
            pubkey_data = base64.b64decode(pubkey_b64)
            pubkey_str = pubkey_data.decode()

            valid_formats = [
                "-----BEGIN PUBLIC KEY-----",
                "-----BEGIN EC PUBLIC KEY-----",
                "-----BEGIN RSA PUBLIC KEY-----",
            ]

            format_valid = any(fmt in pubkey_str for fmt in valid_formats)
            if not format_valid:
                logger.warning("Public key not in expected PEM format")
                return False

            return True

        except Exception as e:
            logger.error(f"Public key format validation failed: {e}")
            return False

    def generate_certificate_serial(self, owner: str, cert_data: bytes) -> str:
        """
        Generate a deterministic serial number for a certificate.

        Args:
            owner: Certificate owner address
            cert_data: Certificate data in bytes

        Returns:
            str: Generated serial number
        """
        try:
            logger.info(f"Generating certificate serial for owner {owner}")
            combined_data = owner.encode() + cert_data
            hash_object = hashlib.sha256(combined_data)
            serial = hash_object.hexdigest()[:16]
            logger.info(f"Generated serial: {serial}")
            return serial
        except Exception as e:
            logger.error(f"Failed to generate certificate serial: {e}")
            return ""
