import hashlib
from datetime import datetime, timezone
from typing import Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

from .quote import SgxQuote, parse_quote


def verify_raw_quote(quote_raw: bytes) -> SgxQuote:
    quote = parse_quote(quote_raw)
    verify_quote(quote)
    return quote


def verify_quote(quote: SgxQuote):
    pck_cert = parse_pck_cert(quote.signature_data.data.data)

    pck_cert_public_key: ec.EllipticCurvePublicKey = pck_cert.public_key()
    pck_cert_public_key.verify(
        signature=signature_to_der(quote.signature_data.data.qe_report_signature),
        data=quote.signature_data.data.qe_report_signed,
        signature_algorithm=ec.ECDSA(hashes.SHA256()),
    )

    hasher = hashlib.sha256()
    hasher.update(quote.signature_data.attestation_key)
    hasher.update(quote.signature_data.data.qe_auth_data.data)
    if hasher.digest() != quote.signature_data.data.qe_report.report_data[:32]:
        raise ValueError(
            "qe report data does not match with value of sha256 calculated over the concatenation of ecdsa attestation key and qe authenticated data"
        )

    ec.EllipticCurvePublicNumbers(
        x=int.from_bytes(quote.signature_data.attestation_key[:32], byteorder="big"),
        y=int.from_bytes(quote.signature_data.attestation_key[32:], byteorder="big"),
        curve=ec.SECP256R1(),
    ).public_key().verify(
        signature=signature_to_der(quote.signature_data.signature),
        data=quote.signed,
        signature_algorithm=ec.ECDSA(hashes.SHA256()),
    )


_root_ca = x509.load_pem_x509_certificate(
    b"-----BEGIN CERTIFICATE-----\nMIICjzCCAjSgAwIBAgIUImUM1lqdNInzg7SVUr9QGzknBqwwCgYIKoZIzj0EAwIw\naDEaMBgGA1UEAwwRSW50ZWwgU0dYIFJvb3QgQ0ExGjAYBgNVBAoMEUludGVsIENv\ncnBvcmF0aW9uMRQwEgYDVQQHDAtTYW50YSBDbGFyYTELMAkGA1UECAwCQ0ExCzAJ\nBgNVBAYTAlVTMB4XDTE4MDUyMTEwNDUxMFoXDTQ5MTIzMTIzNTk1OVowaDEaMBgG\nA1UEAwwRSW50ZWwgU0dYIFJvb3QgQ0ExGjAYBgNVBAoMEUludGVsIENvcnBvcmF0\naW9uMRQwEgYDVQQHDAtTYW50YSBDbGFyYTELMAkGA1UECAwCQ0ExCzAJBgNVBAYT\nAlVTMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEC6nEwMDIYZOj/iPWsCzaEKi7\n1OiOSLRFhWGjbnBVJfVnkY4u3IjkDYYL0MxO4mqsyYjlBalTVYxFP2sJBK5zlKOB\nuzCBuDAfBgNVHSMEGDAWgBQiZQzWWp00ifODtJVSv1AbOScGrDBSBgNVHR8ESzBJ\nMEegRaBDhkFodHRwczovL2NlcnRpZmljYXRlcy50cnVzdGVkc2VydmljZXMuaW50\nZWwuY29tL0ludGVsU0dYUm9vdENBLmRlcjAdBgNVHQ4EFgQUImUM1lqdNInzg7SV\nUr9QGzknBqwwDgYDVR0PAQH/BAQDAgEGMBIGA1UdEwEB/wQIMAYBAf8CAQEwCgYI\nKoZIzj0EAwIDSQAwRgIhAOW/5QkR+S9CiSDcNoowLuPRLsWGf/Yi7GSX94BgwTwg\nAiEA4J0lrHoMs+Xo5o/sX6O9QWxHRAvZUGOdRQ7cvqRXaqI=\n-----END CERTIFICATE-----\n"
)


def parse_pck_cert(pck_chain_pem: bytes) -> x509.Certificate:
    chain = x509.load_pem_x509_certificates(pck_chain_pem)
    if len(chain) != 3:
        raise ValueError("invalid pck chain length")
    pck_cert, intermediate_cert, root_cert = chain[0], chain[1], chain[2]
    if root_cert != _root_ca:
        raise ValueError("invalid root cert")

    now = datetime.now(timezone.utc)
    verify_cert(intermediate_cert, root_cert, None, now)
    verify_cert(pck_cert, intermediate_cert, "Intel SGX PCK Certificate", now)
    return pck_cert


def verify_cert(cert: x509.Certificate, parent: x509.Certificate, common_name: Optional[str], now: datetime):
    common_name_attrs = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    if len(common_name_attrs) == 0:
        raise ValueError("common name not found")
    if common_name is not None and common_name_attrs[0].value != common_name:
        raise ValueError(
            f"invalid subject common name, expected {common_name}, actual {common_name_attrs[0].value}"
        )
    if cert.version != x509.Version.v3:
        raise ValueError(f"invalid version, expected v3, actual {cert.version}")
    if cert.signature_algorithm_oid != x509.SignatureAlgorithmOID.ECDSA_WITH_SHA256:
        raise ValueError(
            f"invalid signature algorithm, expected ECDSAWithSHA256, actual {cert.signature_algorithm_oid._name}"
        )
    if cert.public_key_algorithm_oid != x509.PublicKeyAlgorithmOID.EC_PUBLIC_KEY:
        raise ValueError(
            f"invalid public key algorithm, expected ECDSA, actual {cert.public_key_algorithm_oid._name}"
        )
    if not isinstance(cert.public_key().curve, ec.SECP256R1):
        raise ValueError(
            f"invalid cert public key curve, expected P-256, actual {cert.public_key().curve.name}"
        )

    if cert.issuer != parent.subject:
        raise ValueError(f"issuer name does not match subject from issuing cert")
    if now < cert.not_valid_before_utc:
        raise ValueError("cert is not yet valid")
    if now > cert.not_valid_after_utc:
        raise ValueError("cert is expired")

    parent_public_key: ec.EllipticCurvePublicKey = parent.public_key()
    parent_public_key.verify(cert.signature, cert.tbs_certificate_bytes, cert.signature_algorithm_parameters)


def signature_to_der(signature: bytes) -> bytes:
    return encode_dss_signature(
        r=int.from_bytes(signature[:32], byteorder="big"),
        s=int.from_bytes(signature[32:], byteorder="big"),
    )
