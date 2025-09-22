#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the chunker types."""

from deckling.transforms.chunker.base import BaseChunk, BaseChunker, BaseMeta
from deckling.transforms.chunker.hierarchical_chunker import (
    DocChunk,
    DocMeta,
    HierarchicalChunker,
)
from deckling.transforms.chunker.page_chunker import PageChunker
