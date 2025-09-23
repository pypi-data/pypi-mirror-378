# tests/test_variant_tools.py
import pytest
from opentargets_mcp.queries import OpenTargetsClient
from opentargets_mcp.tools.variant import VariantApi
from .conftest import TEST_VARIANT_ID_1

@pytest.mark.asyncio
class TestVariantTools:
    """Tests for tools related to Variants."""
    variant_api = VariantApi()

    async def test_get_variant_info(self, client: OpenTargetsClient):
        result = await self.variant_api.get_variant_info(client, TEST_VARIANT_ID_1)
        assert result is not None
        assert "variant" in result
        if result.get("variant"):
            assert result["variant"]["id"] == TEST_VARIANT_ID_1
            assert "chromosome" in result["variant"]
            assert "position" in result["variant"]
            assert "referenceAllele" in result["variant"]
            assert "alternateAllele" in result["variant"]

    async def test_get_variant_credible_sets(self, client: OpenTargetsClient):
        result = await self.variant_api.get_variant_credible_sets(client, TEST_VARIANT_ID_1, page_size=1)
        assert result is not None
        assert "variant" in result
        if result.get("variant"):
            assert "credibleSets" in result["variant"]
            if result["variant"]["credibleSets"]:
                assert "rows" in result["variant"]["credibleSets"]

    async def test_get_variant_pharmacogenomics(self, client: OpenTargetsClient):
        result = await self.variant_api.get_variant_pharmacogenomics(client, TEST_VARIANT_ID_1, page_size=1)
        assert result is not None
        assert "variant" in result
        if result.get("variant"):
            assert "pharmacogenomics" in result["variant"]

    async def test_get_variant_evidences(self, client: OpenTargetsClient):
        result = await self.variant_api.get_variant_evidences(client, TEST_VARIANT_ID_1, size=1)
        assert result is not None
        assert "variant" in result
        if result.get("variant"):
            assert "evidences" in result["variant"]
            if result["variant"]["evidences"]:
                assert "rows" in result["variant"]["evidences"]