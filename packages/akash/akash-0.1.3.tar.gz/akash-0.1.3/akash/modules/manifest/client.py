import logging

from .query import ManifestQuery
from .tx import ManifestTx
from .utils import ManifestUtils

logger = logging.getLogger(__name__)


class ManifestClient(ManifestQuery, ManifestTx, ManifestUtils):
    """Client for manifest operations."""

    def __init__(self, client):
        self.client = client
        logger.info("Initialized ManifestClient with production gRPC support")
