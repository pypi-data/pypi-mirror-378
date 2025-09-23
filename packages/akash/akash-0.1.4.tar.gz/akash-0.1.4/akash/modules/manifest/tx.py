import logging
from typing import Dict, Any

from ...tx import broadcast_transaction_rpc

logger = logging.getLogger(__name__)


class ManifestTx:
    """
    Mixin for manifest transaction operations.
    """

    def deploy_manifest(
        self,
        manifest_data: Dict[str, Any],
        wallet,
        memo: str = "",
        fee_amount: str = None,
        gas_limit: int = None,
        gas_adjustment: float = 1.2,
        use_simulation: bool = True,
    ) -> Dict[str, Any]:
        """
        Deploy a validated manifest to the Akash network.

        Args:
            manifest_data: Complete manifest specification
            wallet: Wallet for deployment transaction
            memo: Transaction memo
            fee_amount: Fee amount in uakt
            gas_limit: Gas limit override
            gas_adjustment: Multiplier for gas estimation
            use_simulation: Whether to simulate for gas estimation

        Returns:
            Deployment result with transaction details
        """
        try:
            logger.info(f"Deploying manifest: {manifest_data.get('name', 'unnamed')}")

            validation = self.validate_manifest(manifest_data)
            if not validation["valid"]:
                logger.error(f"Manifest validation failed: {validation['errors']}")
                return {
                    "status": "failed",
                    "error": "Manifest validation failed",
                    "validation_errors": validation["errors"],
                }

            group_result = self.create_group_manifest(
                {
                    "name": manifest_data.get("name", "akash-deployment"),
                    "services": list(manifest_data.get("services", {}).values()),
                }
            )

            if group_result.get("validation") != "passed":
                logger.error(
                    f"Group manifest creation failed: {group_result.get('error')}"
                )
                return {
                    "status": "failed",
                    "error": "Group manifest creation failed",
                    "details": group_result,
                }

            msg = {
                "@type": "/akash.deployment.v1beta3.MsgCreateDeployment",
                "id": {
                    "owner": wallet.address,
                    "dseq": str(abs(hash(str(manifest_data))) % 1000000),
                },
                "groups": group_result["services"],
                "version": manifest_data.get("version", "v2beta2").encode("utf-8"),
                "deposit": {
                    "denom": "uakt",
                    "amount": manifest_data.get("deposit", "5000000"),
                },
            }

            result = broadcast_transaction_rpc(
                client=self.client,
                wallet=wallet,
                messages=[msg],
                memo=memo,
                fee_amount=fee_amount,
                gas_limit=gas_limit,
                gas_adjustment=gas_adjustment,
                use_simulation=use_simulation,
                wait_for_confirmation=True,
                confirmation_timeout=30,
            )

            response = {
                "status": "success" if result.success else "failed",
                "deployment_id": f"dep_{abs(hash(str(manifest_data))) % 1000000}",
                "tx_hash": result.tx_hash if result.success else "",
                "manifest": group_result,
                "services_deployed": group_result["services_count"],
            }

            if not result.success:
                response["error"] = result.raw_log
                logger.error(f"Deployment failed: {result.raw_log}")
            else:
                logger.info(f"Deployment successful: {response['deployment_id']}")

            return response

        except Exception as e:
            logger.error(f"Failed to deploy manifest: {e}")
            return {"status": "failed", "error": str(e)}

    def update_deployment_manifest(
        self,
        deployment_id: str,
        updated_manifest: Dict[str, Any],
        wallet,
        memo: str = "",
        fee_amount: str = None,
        gas_limit: int = None,
        gas_adjustment: float = 1.2,
        use_simulation: bool = True,
    ) -> Dict[str, Any]:
        """
        Update an existing deployment manifest.

        Args:
            deployment_id: Deployment to update
            updated_manifest: New manifest specification
            wallet: Wallet for update transaction
            memo: Transaction memo
            fee_amount: Fee amount in uakt
            gas_limit: Gas limit override
            gas_adjustment: Multiplier for gas estimation
            use_simulation: Whether to simulate for gas estimation

        Returns:
            Update result with transaction details
        """
        try:
            logger.info(f"Updating manifest for deployment: {deployment_id}")

            validation = self.validate_manifest(updated_manifest)
            if not validation["valid"]:
                logger.error(
                    f"Updated manifest validation failed: {validation['errors']}"
                )
                return {
                    "status": "failed",
                    "error": "Updated manifest validation failed",
                    "validation_errors": validation["errors"],
                }

            msg = {
                "@type": "/akash.deployment.v1beta3.MsgUpdateDeployment",
                "id": {
                    "owner": wallet.address,
                    "dseq": deployment_id.replace("dep_", ""),
                },
                "groups": list(updated_manifest.get("services", {}).values()),
                "version": updated_manifest.get("version", "v2beta2").encode("utf-8"),
            }

            result = broadcast_transaction_rpc(
                client=self.client,
                wallet=wallet,
                messages=[msg],
                memo=memo,
                fee_amount=fee_amount,
                gas_limit=gas_limit,
                gas_adjustment=gas_adjustment,
                use_simulation=use_simulation,
                wait_for_confirmation=True,
                confirmation_timeout=30,
            )

            response = {
                "status": "success" if result.success else "failed",
                "deployment_id": deployment_id,
                "tx_hash": result.tx_hash if result.success else "",
                "updated_services": len(updated_manifest.get("services", {})),
            }

            if not result.success:
                response["error"] = result.raw_log
                logger.error(f"Manifest update failed: {result.raw_log}")
            else:
                logger.info(f"Manifest update successful: {deployment_id}")

            return response

        except Exception as e:
            logger.error(f"Failed to update manifest: {e}")
            return {"status": "failed", "error": str(e)}
