from dataclasses import dataclass
from typing import Optional

from achi.types.blockchain_format.sized_bytes import bytes32
from achi.types.blockchain_format.vdf import VDFInfo, VDFProof
from achi.util.streamable import Streamable, streamable


@dataclass(frozen=True)
@streamable
class SignagePoint(Streamable):
    cc_vdf: Optional[VDFInfo]
    cc_proof: Optional[VDFProof]
    rc_vdf: Optional[VDFInfo]
    rc_proof: Optional[VDFProof]
    timelord_reward_puzzle_hash: Optional[bytes32]
