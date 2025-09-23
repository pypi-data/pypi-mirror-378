from typing import Any, Dict


class MarketUtils:
    """
    Mixin for market utilities.
    """

    def _create_bid_msg(
        self,
        provider: str,
        deployment_owner: str,
        deployment_dseq: str,
        group_seq: str,
        order_seq: str,
        price: str,
    ) -> Dict[str, Any]:
        """Create bid message for testing."""
        return {
            "@type": "/akash.market.v1beta4.MsgCreateBid",
            "id": {
                "owner": deployment_owner,
                "dseq": deployment_dseq,
                "gseq": group_seq,
                "oseq": order_seq,
                "provider": provider,
            },
            "price": {"amount": price.replace("uakt", ""), "denom": "uakt"},
            "deposit": {"amount": price.replace("uakt", ""), "denom": "uakt"},
        }

    def _create_close_bid_msg(
        self,
        provider: str,
        deployment_owner: str,
        deployment_dseq: str,
        group_seq: str,
        order_seq: str,
    ) -> Dict[str, Any]:
        """Create close bid message for testing."""
        return {
            "@type": "/akash.market.v1beta4.MsgCloseBid",
            "id": {
                "owner": deployment_owner,
                "dseq": deployment_dseq,
                "gseq": group_seq,
                "oseq": order_seq,
                "provider": provider,
            },
        }

    def _create_lease_msg(
        self,
        provider: str,
        deployment_owner: str,
        deployment_dseq: str,
        group_seq: str,
        order_seq: str,
    ) -> Dict[str, Any]:
        """Create lease message for testing."""
        return {
            "@type": "/akash.market.v1beta4.MsgCreateLease",
            "id": {
                "owner": deployment_owner,
                "dseq": deployment_dseq,
                "gseq": group_seq,
                "oseq": order_seq,
                "provider": provider,
            },
        }

    def _create_close_lease_msg(
        self,
        provider: str,
        deployment_owner: str,
        deployment_dseq: str,
        group_seq: str,
        order_seq: str,
    ) -> Dict[str, Any]:
        """Create close lease message for testing."""
        return {
            "@type": "/akash.market.v1beta4.MsgCloseLease",
            "id": {
                "owner": deployment_owner,
                "dseq": deployment_dseq,
                "gseq": group_seq,
                "oseq": order_seq,
                "provider": provider,
            },
        }

    def _create_withdraw_lease_msg(
        self,
        provider: str,
        deployment_owner: str,
        deployment_dseq: str,
        group_seq: str,
        order_seq: str,
    ) -> Dict[str, Any]:
        """Create withdraw lease message for testing."""
        return {
            "@type": "/akash.market.v1beta4.MsgWithdrawLease",
            "id": {
                "owner": deployment_owner,
                "dseq": deployment_dseq,
                "gseq": group_seq,
                "oseq": order_seq,
                "provider": provider,
            },
        }
