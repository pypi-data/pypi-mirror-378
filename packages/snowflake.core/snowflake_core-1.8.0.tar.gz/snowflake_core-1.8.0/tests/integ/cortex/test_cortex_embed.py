#
# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
#
import pytest

from snowflake.core._root import Root


pytestmark = [pytest.mark.skip_gov]


def test_embed(root: Root):
    resp = root.cortex_embed_service.embed("e5-base-v2", ["foo", "bar"])

    assert len(resp.data) == 2
    assert resp.model == "e5-base-v2"
    assert resp.usage.total_tokens >= 0
