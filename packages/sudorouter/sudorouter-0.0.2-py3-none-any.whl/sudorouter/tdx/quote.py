import struct
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional, Union


class BinaryReader:
    def __init__(self, bytes: bytes):
        self.bytes = bytes
        self.index = 0

    def length(self) -> int:
        return max(len(self.bytes) - self.index, 0)

    def read_bytes(self, n: int) -> bytes:
        if n > self.length():
            return b""
        idx = self.index + n
        bs = self.bytes[self.index : idx]
        self.index = idx
        return bs

    def read_uint16(self) -> int:
        return struct.unpack("<H", self.read_bytes(2))[0]

    def read_uint32(self) -> int:
        return struct.unpack("<L", self.read_bytes(4))[0]

    def read_uint64(self) -> int:
        return struct.unpack("<Q", self.read_bytes(8))[0]


class TeeType(Enum):
    sgx = 0x00000000
    tdx = 0x00000081


@dataclass
class SgxQuoteHeader:
    version: int
    att_key_type: int
    tee_type: TeeType
    reserved: int
    vendor_id: bytes
    user_data: bytes

    @classmethod
    def read_from(cls, reader: BinaryReader) -> "SgxQuoteHeader":
        return SgxQuoteHeader(
            version=reader.read_uint16(),
            att_key_type=reader.read_uint16(),
            tee_type=TeeType(reader.read_uint32()),
            reserved=reader.read_uint32(),
            vendor_id=reader.read_bytes(16),
            user_data=reader.read_bytes(20),
        )


@dataclass
class SgxReport2Body:
    tee_tcb_svn: bytes
    mr_seam: bytes
    mr_signer_seam: bytes
    seam_attributes: int
    td_attributes: int
    x_fam: int
    mr_td: bytes
    mr_config_id: bytes
    mr_owner: bytes
    mr_owner_config: bytes
    rt_mr: List[bytes]
    report_data: bytes

    @classmethod
    def read_from(cls, reader: BinaryReader) -> "SgxReport2Body":
        return SgxReport2Body(
            tee_tcb_svn=reader.read_bytes(16),
            mr_seam=reader.read_bytes(48),
            mr_signer_seam=reader.read_bytes(48),
            seam_attributes=reader.read_uint64(),
            td_attributes=reader.read_uint64(),
            x_fam=reader.read_uint64(),
            mr_td=reader.read_bytes(48),
            mr_config_id=reader.read_bytes(48),
            mr_owner=reader.read_bytes(48),
            mr_owner_config=reader.read_bytes(48),
            rt_mr=[reader.read_bytes(48) for _ in range(4)],
            report_data=reader.read_bytes(64),
        )


@dataclass
class SgxReport2BodyV15:
    tee_tcb_svn: bytes
    mr_seam: bytes
    mr_signer_seam: bytes
    seam_attributes: int
    td_attributes: int
    x_fam: int
    mr_td: bytes
    mr_config_id: bytes
    mr_owner: bytes
    mr_owner_config: bytes
    rt_mr: List[bytes]
    report_data: bytes
    tee_tcb_svn2: bytes
    mr_service_td: bytes

    @classmethod
    def read_from(cls, reader: BinaryReader) -> "SgxReport2BodyV15":
        return SgxReport2BodyV15(
            tee_tcb_svn=reader.read_bytes(16),
            mr_seam=reader.read_bytes(48),
            mr_signer_seam=reader.read_bytes(48),
            seam_attributes=reader.read_uint64(),
            td_attributes=reader.read_uint64(),
            x_fam=reader.read_uint64(),
            mr_td=reader.read_bytes(48),
            mr_config_id=reader.read_bytes(48),
            mr_owner=reader.read_bytes(48),
            mr_owner_config=reader.read_bytes(48),
            rt_mr=[reader.read_bytes(48) for _ in range(4)],
            report_data=reader.read_bytes(64),
            tee_tcb_svn2=reader.read_bytes(16),
            mr_service_td=reader.read_bytes(48),
        )


@dataclass
class EnclaveReport:
    cpu_svn: bytes
    misc_select: int
    reserved1: bytes
    attributes: bytes
    mr_enclave: bytes
    reserved2: bytes
    mr_signer: bytes
    reserved3: bytes
    isv_prod_id: int
    isv_svn: int
    reserved4: bytes
    report_data: bytes

    @classmethod
    def read_from(cls, reader: BinaryReader) -> Tuple["EnclaveReport", bytes]:
        idx_start = reader.index
        report = EnclaveReport(
            cpu_svn=reader.read_bytes(16),
            misc_select=reader.read_uint32(),
            reserved1=reader.read_bytes(28),
            attributes=reader.read_bytes(16),
            mr_enclave=reader.read_bytes(32),
            reserved2=reader.read_bytes(32),
            mr_signer=reader.read_bytes(32),
            reserved3=reader.read_bytes(96),
            isv_prod_id=reader.read_uint16(),
            isv_svn=reader.read_uint16(),
            reserved4=reader.read_bytes(60),
            report_data=reader.read_bytes(64),
        )
        idx_end = reader.index
        return report, reader.bytes[idx_start:idx_end]


@dataclass
class QeAuthData:
    parsed_data_size: int
    data: bytes

    @classmethod
    def read_from(cls, reader: BinaryReader) -> "QeAuthData":
        parsed_data_size = reader.read_uint16()
        data = reader.read_bytes(parsed_data_size)
        return QeAuthData(parsed_data_size=parsed_data_size, data=data)


@dataclass
class QeReportCertificationData:
    qe_report: EnclaveReport
    qe_report_signed: bytes
    qe_report_signature: bytes
    qe_auth_data: QeAuthData
    type: int
    parsed_data_size: int
    data: bytes

    @classmethod
    def read_from(cls, reader: BinaryReader) -> "QeReportCertificationData":
        qe_report, qe_report_signed = EnclaveReport.read_from(reader)
        qe_report_signature = reader.read_bytes(64)
        qe_auth_data = QeAuthData.read_from(reader)
        type = reader.read_uint16()
        parsed_data_size = reader.read_uint32()
        data = reader.read_bytes(parsed_data_size)
        return QeReportCertificationData(
            qe_report=qe_report,
            qe_report_signed=qe_report_signed,
            qe_report_signature=qe_report_signature,
            qe_auth_data=qe_auth_data,
            type=type,
            parsed_data_size=parsed_data_size,
            data=data,
        )


@dataclass
class Ecdsa256BitQuoteV4AuthData:
    signature: bytes
    attestation_key: bytes
    type: int
    parsed_data_size: int
    data: QeReportCertificationData

    @classmethod
    def read_from(cls, reader: BinaryReader) -> "Ecdsa256BitQuoteV4AuthData":
        signature = reader.read_bytes(64)
        attestation_key = reader.read_bytes(64)
        type = reader.read_uint16()
        parsed_data_size = reader.read_uint32()

        idx = reader.index
        data = QeReportCertificationData.read_from(reader)
        if reader.index - idx != parsed_data_size:
            raise ValueError(f"invalid data size, expected {parsed_data_size}, actual {reader.index - idx}")

        return Ecdsa256BitQuoteV4AuthData(
            signature=signature,
            attestation_key=attestation_key,
            type=type,
            parsed_data_size=parsed_data_size,
            data=data,
        )


class ReportBodyType(Enum):
    sgx_enclave = 1
    tdx_10 = 2
    tdx_15 = 3


@dataclass
class SgxQuote:
    header: SgxQuoteHeader
    type: Optional[ReportBodyType]
    size: Optional[int]
    report_body: Union[SgxReport2Body, SgxReport2BodyV15]
    signed: bytes
    signature_data_len: int
    signature_data: Ecdsa256BitQuoteV4AuthData


def parse_quote(quote_raw: bytes) -> SgxQuote:
    if len(quote_raw) == 0:
        raise ValueError("quote bytes is empty")
    reader = BinaryReader(quote_raw)
    header = SgxQuoteHeader.read_from(reader)
    if header.att_key_type != 2:
        raise ValueError(f"unsupported attestation key type {header.att_key_type}")
    intel_qe_vendor_id = b"\x93\x9A\x72\x33\xF7\x9C\x4C\xA9\x94\x0A\x0D\xB3\x95\x7F\x06\x07"
    if header.vendor_id != intel_qe_vendor_id:
        raise ValueError(f"invalid vendor id, expected {intel_qe_vendor_id}, actual {header.vendor_id}")

    if header.version == 4:
        type = None
        size = None
        report_body = SgxReport2Body.read_from(reader)
    elif header.version == 5:
        type = ReportBodyType(reader.read_uint16())
        size = reader.read_uint32()
        idx = reader.index
        if type == ReportBodyType.tdx_10:
            if header.tee_type != TeeType.tdx:
                raise ValueError("conflicting tee type and body type")
            report_body = SgxReport2Body.read_from(reader)
        elif type == ReportBodyType.tdx_15:
            if header.tee_type != TeeType.tdx:
                raise ValueError("conflicting tee type and body type")
            report_body = SgxReport2BodyV15.read_from(reader)
            pass
        else:
            raise ValueError(f"unsupported quote v5 body type {type}")
        if reader.index - idx != size:
            raise ValueError(f"invalid body size, expected {size}, actual {reader.index - idx}")
    else:
        raise ValueError(f"unsupported quote version {header.version}")

    signed = quote_raw[: reader.index]
    signature_data_len = reader.read_uint32()

    idx = reader.index
    signature_data = Ecdsa256BitQuoteV4AuthData.read_from(reader)
    if reader.index - idx != signature_data_len:
        raise ValueError(
            f"invalid signature data size, expected {signature_data_len}, actual {reader.index - idx}"
        )
    if signature_data.type != 6:  # PCK_ID_QE_REPORT_CERTIFICATION_DATA
        raise ValueError(f"unsupported certification data type {signature_data.type}")
    if signature_data.data.type < 1 or signature_data.data.type > 5:
        raise ValueError(f"unsupported qe report certification data type {signature_data.data.type}")
    return SgxQuote(
        header=header,
        type=type,
        size=size,
        report_body=report_body,
        signed=signed,
        signature_data_len=signature_data_len,
        signature_data=signature_data,
    )
