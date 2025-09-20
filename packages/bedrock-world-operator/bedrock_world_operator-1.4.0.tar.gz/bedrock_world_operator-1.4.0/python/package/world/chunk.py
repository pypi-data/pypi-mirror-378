import numpy
from dataclasses import dataclass, field
from .constant import RANGE_INVALID, RANGE_OVERWORLD
from ..internal.symbol_export_chunk import (
    chunk_biome,
    chunk_biomes,
    chunk_block,
    chunk_blocks,
    chunk_compact,
    chunk_equals,
    chunk_highest_filled_sub_chunk,
    chunk_set_biome,
    chunk_set_biomes,
    chunk_set_block,
    chunk_set_blocks,
    chunk_set_sub,
    chunk_set_sub_chunk,
    chunk_sub,
    chunk_sub_chunk,
    new_chunk as nc,
    release_chunk,
)
from ..world.define import QuickChunkBlocks, Range
from ..world.sub_chunk import SubChunk


@dataclass
class ChunkBase:
    """ChunkBase is the base implement of a Minecraft chunk."""

    _chunk_id: int = -1
    _chunk_range: Range = field(
        default_factory=lambda: Range(
            RANGE_INVALID.start_range, RANGE_INVALID.end_range
        )
    )

    def __del__(self):
        if self._chunk_id >= 0 and release_chunk is not None:
            release_chunk(self._chunk_id)

    def is_valid(self) -> bool:
        """
        is_valid check current chunk is valid or not.

        If not valid, it means the chunk actually not exist,
        not only Python but also in Go.

        Try to use an invalid chunk is not allowed,
        and any operation will be terminated.

        Returns:
            bool: Whether the chunk is valid or not.
        """
        return (
            self._chunk_id >= 0
            and self._chunk_range.end_range >= self._chunk_range.start_range
        )


class Chunk(ChunkBase):
    """
    Chunk is a segment in the world
    with a size of 16x16x256 blocks.

    A chunk contains multiple sub chunks
    and stores other information such as
    biomes.
    """

    def __init__(self):
        super().__init__()

    def biome(self, x: int, y: int, z: int) -> int:
        """biome returns the biome ID at a specific column in the chunk.

        Args:
            x (int): The relative x position of this column. Must in a range of 0-15.
            y (int): The y position of this column.
                     Must in a range of -64~319 (Overworld), 0-127 (Nether) and 0-255 (End).
            z (int): The relative z position of this column. Must in a range of 0-15.

        Returns:
            int: The biome ID of this column.
                 If the current chunk is not found, then return -1.
        """
        return chunk_biome(self._chunk_id, x, y, z)

    def biomes(self) -> QuickChunkBlocks:
        """
        biomes returns all biome IDs for each blocks in this chunk.

        It is highly suggested you use this instead of c.biome(...)
        if you are trying to query the biome ID of so many blocks from
        this chunk.

        Returns:
            QuickChunkBlocks:
                All biome IDs for each blocks in this chunks.

                Note that this implement doesn't do further check due to this is aims to
                increase biome ID query/set speed, and you should take responsibility for
                any possible error.

                Here we listed all possible errors that we have not checked.
                    - Current chunk has an invalid range
                    - Underlying blocks list is empty
        """
        return QuickChunkBlocks(
            chunk_biomes(self._chunk_id),
            self._chunk_range.start_range,
            self._chunk_range.end_range,
        )

    def block(self, x: int, y: int, z: int, layer: int) -> int:
        """Block returns the runtime ID of the block at a given x, y and z in a chunk at the given layer.

        Args:
            x (int): The relative x position of this block. Must in a range of 0-15.
            y (int): The y position of this block.
                     Must in a range of -64~319 (Overworld), 0-127 (Nether) and 0-255 (End).
            z (int): The relative z position of this block. Must in a range of 0-15.
            layer (int): The layer to find this block.

        Returns:
            int: Return the block runtime ID of target block.
                 If the current chunk is not found, then return -1.
                 Note that if no sub chunk exists at the given y, the block is assumed to be air.
        """
        return chunk_block(self._chunk_id, x, y, z, layer)

    def blocks(self, layer: int) -> QuickChunkBlocks:
        """
        blocks returns all blocks (block runtime IDs) whose in the
        target layer of this chunk.

        It is highly suggested you use this instead of c.block(...)
        if you are trying to query so many blocks from this chunk.

        Args:
            layer (int): The layer of the blocks in this chunk that you want to find.

        Returns:
            QuickChunkBlocks:
                All blocks of the target layer in this chunk if the current chunk exists.
                If the target layer does not exist, then you get a chunk full of air.

                Note that this implement doesn't do further check due to this is aims to
                increase block query/set speed, and you should take responsibility for
                any possible error.

                Here we listed all possible errors that we have not checked.
                    - Current chunk has an invalid range
                    - Underlying blocks list is empty
        """
        return QuickChunkBlocks(
            chunk_blocks(self._chunk_id, layer),
            self._chunk_range.start_range,
            self._chunk_range.end_range,
        )

    def compact(self):
        """
        compact compacts the chunk as much as possible,
        getting rid of any sub chunks that are empty,
        and compacts all storages in the sub chunks to
        occupy as little space as possible.

        compact should be called right before the chunk
        is saved to optimize the storage space.

        Raises:
            Exception: When failed to compact.
        """
        err = chunk_compact(self._chunk_id)
        if len(err) > 0:
            raise Exception(err)

    def equals(self, another_chunk: ChunkBase) -> bool:
        """equals returns if the chunk passed is equal to the current one.

        Args:
            another_chunk (ChunkBase): The chunk passed.

        Returns:
            bool: The compare result.
                  Return True for the contents of two chunks is the same.
                  Return False for current chunk or another_chunk is not found.
        """
        result = chunk_equals(self._chunk_id, another_chunk._chunk_id)
        return result == 1

    def highest_filled_sub_chunk(self) -> int:
        """
        highest_filled_sub_chunk returns the index of
        the highest sub chunk in the chunk that has any
        blocks in it.

        0 is returned if no sub chunks have any blocks.

        Returns:
            int: The index of the highest sub chunk in the chunk that has any blocks in it.
                 If no sub chunks have any block, then return 0.
                 Additionally, if the current chunk is not found, then return -1.
        """
        return chunk_highest_filled_sub_chunk(self._chunk_id)

    def range(self) -> Range:
        """Range returns the Range of the Chunk as passed to new_chunk.

        Returns:
            Range: The Y range that player could build in of this chunk.
                   If the current chunk is valid, then return RANGE_INVALID.
        """
        return self._chunk_range

    def set_biome(self, x: int, y: int, z: int, biome_id: int):
        """set_biome sets the biome ID at a specific column in the chunk.

        Args:
            x (int): The relative x position of this column. Must in a range of 0-15.
            y (int): The y position of this column.
                     Must in a range of -64~319 (Overworld), 0-127 (Nether) and 0-255 (End).
            z (int): The relative z position of this column. Must in a range of 0-15.
            biome_id (int): The biome ID want to set.

        Raises:
            Exception: When failed to set biome ID.
        """
        err = chunk_set_biome(self._chunk_id, x, y, z, biome_id)
        if len(err) > 0:
            raise Exception(err)

    def set_biomes(self, biome_ids: QuickChunkBlocks):
        """
        set_biomes sets the biome IDs for each block in this chunk.

        It is highly suggested you use this instead of c.set_biome(...)
        if you are trying to modify the biome ID of so many blocks in
        this chunk.

        Note that this implement will not check the underlying blocks list is valid
        or not due to this is aims to increase block query/set speed, and you should
        take responsibility for any possible error.

        Args:
            biome_ids (QuickChunkBlocks): The biome IDs for each block in this chunk that you want to overwrite.

        Raises:
            Exception: When failed to set blocks.
        """
        err = chunk_set_biomes(self._chunk_id, biome_ids.blocks)
        if len(err) > 0:
            raise Exception(err)

    def set_block(
        self, x: int, y: int, z: int, layer: int, block_runtime_id: int | numpy.uint32
    ):
        """
        set_block sets the runtime ID of a block at
        a given x, y and z in a chunk at the given layer.

        If no sub chunk exists at the given y,
        a new sub chunk is created and the block is set.

        Args:
            x (int): The relative x position of this block. Must in a range of 0-15.
            y (int): The y position of this block.
                     Must in a range of -64~319 (Overworld), 0-127 (Nether) and 0-255 (End).
            z (int): The relative z position of this block. Must in a range of 0-15.
            layer (int): The layer that this blocks in.
            block_runtime_id (int | numpy.uint32): The result block that this block will be.

        Raises:
            Exception: When failed to set block.
        """
        err = chunk_set_block(self._chunk_id, x, y, z, layer, block_runtime_id)  # type: ignore
        if len(err) > 0:
            raise Exception(err)

    def set_blocks(self, layer: int, blocks: QuickChunkBlocks):
        """
        set_blocks sets the whole chunk blocks in layer by given block runtime IDs.

        It is highly suggested you use this instead of c.set_block(...) if you are
        trying to modify so many blocks to this chunk.

        Note that this implement will not check the underlying blocks list is valid
        or not due to this is aims to increase block query/set speed, and you should
        take responsibility for any possible error.

        Args:
            layer (int): The layer of the blocks in this chunk that you want to overwrite.
            blocks (QuickChunkBlocks): The blocks in the target layer of this chunk that you want to overwrite.

        Raises:
            Exception: When failed to set blocks.
        """
        err = chunk_set_blocks(self._chunk_id, layer, blocks.blocks)
        if len(err) > 0:
            raise Exception(err)

    def sub(self) -> list[SubChunk]:
        """
        sub returns a list of all sub chunks present in the chunk.

        Note that after editing those sub chunks,
        you just only need to save this chunk,
        but not need to save the modified sub chunks.

        Returns:
            list[SubChunk]: All sub chunks present in the chunk.
                            If the current chunk is not found,
                            or this chunk has no sub chunk, then return an empty list.
        """
        result = []
        for i in chunk_sub(self._chunk_id):
            s = SubChunk()
            s._sub_chunk_id = i
            result.append(s)
        return result

    def set_sub(self, sub_chunks: list[SubChunk]):
        """
        set_sub overwrite the sub chunks of this chunk.

        The length of sub_chunks could less or bigger
        than the sub chunk counts of this whole chunk.

        For Overworld, len(sub_chunks) = (319 - (-64) + 1) >> 4 = 24,
        and for Nether, len(sub_chunks) = (127 - 0 + 1) >> 4 = 8,
        and for End, len(sub_chunks) = (255 - 0 + 1) >> 4 = 16.

        If sub_chunks is not enough, then only the given part will be modified,
        if len(sub_chunks) is more than expected, then the unexpected part will be not used.

        For example, if len(sub_chunks) = 27 and this is a chunk in Overworld,
        then only sub_chunks[0:24] will be used, and sub_chunks[24:27] will be lost.

        Args:
            sub_chunks (list[SubChunk]): Those sub chunks that you want to overwrite to this chunk.

        Raises:
            Exception: When failed to set those sub chunks of this chunk.
        """
        err = chunk_set_sub(self._chunk_id, [i._sub_chunk_id for i in sub_chunks])
        if len(err) > 0:
            raise Exception(err)

    def sub_chunk(self, y: int) -> SubChunk:
        """
        sub_chunk finds the correct sub chunk in the Chunk by a y position.

        Note that after editing this sub chunk,
        you just only need to save this chunk,
        but not need to save the modified sub chunks.

        Args:
            y (int): The y position of this block.
                     Must in a range of -64~319 (Overworld), 0-127 (Nether) and 0-255 (End).

        Returns:
            SubChunk: If the current chunk is not found, then return an invalid sub chunk.
                      Otherwise, return the target sub chunk.
                      Note that you could use s.is_valid() to check whether the sub chunk is valid or not.
        """
        s = SubChunk()
        s._sub_chunk_id = chunk_sub_chunk(self._chunk_id, y)
        return s

    def set_sub_chunk(self, sub_chunk: SubChunk, index: int):
        """
        set_sub_chunk set the a sub chunk of this chunk.

        index is refer to the sub chunk Y index of this sub chunk,
        and the index should bigger than -1.

        For example, for a block in Overworld and place at (x, 24, z), its sub chunk Y pos will be 24>>4 (1).
        However, this is not the index of this sub chunk, we need to do other compute to get the index:
            index = (24>>4) - (self.range().start_range >> 4)
                  = 1 - (-64 >> 4)
                  = 1 - (-4)
                  = 5

        Args:
            sub_chunk (SubChunk): _description_
            index (int): _description_

        Raises:
            Exception: _description_
        """
        err = chunk_set_sub_chunk(self._chunk_id, sub_chunk._sub_chunk_id, index)
        if len(err) > 0:
            raise Exception(err)

    def sub_index(self, y: int) -> int:
        """
        sub_index returns the sub chunk index matching the y position passed.

        index is refer to the sub chunk Y index of this sub chunk,
        and the index should bigger than -1.

        For example, for a block in Overworld and place at (x, 24, z), its sub chunk Y pos will be 24>>4 (1).
        However, this is not the index of this sub chunk, we need to do other compute to get the index:
            ```
            index = (24>>4) - (self.range().start_range >> 4)
                  = 1 - (-64 >> 4)
                  = 1 - (-4)
                  = 5
            ```

        Args:
            y (int): The relative y position of this block.
                     Must in a range of -64~319 (Overworld), 0-127 (Nether) and 0-255 (End).

        Returns:
            int: The index of the y position.
                 If the current sub chunk is not found, then return -1.
        """
        return (y - self._chunk_range.start_range) >> 4

    def sub_y(self, index: int) -> int:
        """
        sub_y returns the sub chunk Y value matching the index passed.
        Note that y is in a range of -64~319 (Overworld), 0-127 (Nether) and 0-255 (End).

        index is refer to the sub chunk Y index of this sub chunk,
        and the index should bigger than -1.

        For example, for a block in Overworld and place at (x, 24, z), its sub chunk Y pos will be 24>>4 (1).
        However, this is not the index of this sub chunk, we need to do other compute to get the index:
            ```
            index = (24>>4) - (self.range().start_range >> 4)
                  = 1 - (-64 >> 4)
                  = 1 - (-4)
                  = 5
            ```

        Therefore, this function use `(index << 4) + self.range().start_range` to get the sub Y value of given index.
        However, we suggest you to use the function here, instead of compute the value by yourself.

        Additionally, the returned Y value is likely a block Y position, but not sub chunk Y position.

        Args:
            index (int): The given index that used to compute the value of y.

        Returns:
            int: The y position who could match the given index.
                 If the current sub chunk is not found, then return -1.
        """
        return (index << 4) + self._chunk_range.start_range


def new_chunk(r: Range = RANGE_OVERWORLD) -> Chunk:
    """NewChunk initialises a new chunk who full of air and returns it, so that it may be used.

    Args:
        r (Range, optional): The Y range of this chunk could reach. Defaults to RANGE_OVERWORLD.

    Returns:
        Chunk: A new chunk.
    """
    c = Chunk()
    start_range, end_range, chunk_id = nc(r.start_range, r.end_range)
    c._chunk_range = Range(start_range, end_range)
    c._chunk_id = chunk_id
    return c
