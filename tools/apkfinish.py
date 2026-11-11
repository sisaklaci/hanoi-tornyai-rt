#!/usr/bin/env python3
"""Align (4-byte, stored entries) and sign an APK with APK Signature Scheme v2 (RSA-2048/SHA-256).
usage: apkfinish.py in.apk out.apk keydir
"""
import hashlib, os, struct, sys, zipfile, datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

STORE = ('resources.arsc', '.png', '.so')

def align(src, dst):
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, 'w') as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            zi = zipfile.ZipInfo(info.filename, date_time=(2026, 11, 11, 0, 0, 0))
            zi.external_attr = info.external_attr
            stored = info.filename == 'resources.arsc' or info.filename.endswith(STORE[1:]) or info.compress_type == zipfile.ZIP_STORED
            zi.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
            if stored:
                off = zout.fp.tell() + 30 + len(zi.filename.encode())
                pad = (-off) % 4
                zi.extra = b'\0' * pad
            zout.writestr(zi, data)

def lp(b):  # uint32 length-prefixed
    return struct.pack('<I', len(b)) + b

def load_key(keydir):
    kp, cp = os.path.join(keydir, 'key.pem'), os.path.join(keydir, 'cert.der')
    if not os.path.exists(kp):
        os.makedirs(keydir, exist_ok=True)
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Sisak Laszlo'),
                          x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'helmetsoft.com'),
                          x509.NameAttribute(NameOID.COUNTRY_NAME, 'HU')])
        now = datetime.datetime(2026, 11, 1, tzinfo=datetime.timezone.utc)
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
                .serial_number(x509.random_serial_number()).not_valid_before(now)
                .not_valid_after(now + datetime.timedelta(days=365 * 30)).sign(key, hashes.SHA256()))
        open(kp, 'wb').write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        open(cp, 'wb').write(cert.public_bytes(serialization.Encoding.DER))
    key = serialization.load_pem_private_key(open(kp, 'rb').read(), None)
    return key, open(cp, 'rb').read()

def chunk_digest(sections):
    digs = []
    for s in sections:
        for i in range(0, len(s), 1 << 20):
            c = s[i:i + (1 << 20)]
            digs.append(hashlib.sha256(b'\xa5' + struct.pack('<I', len(c)) + c).digest())
    return hashlib.sha256(b'\x5a' + struct.pack('<I', len(digs)) + b''.join(digs)).digest()

def sign(path, out, keydir):
    data = open(path, 'rb').read()
    eocd = data.rfind(b'PK\x05\x06')
    cd_size, cd_off = struct.unpack('<II', data[eocd + 12:eocd + 20])
    contents, cd, eo = data[:cd_off], data[cd_off:cd_off + cd_size], data[eocd:]
    key, cert = load_key(keydir)
    digest = chunk_digest([contents, cd, eo])
    ALGO = 0x0103  # RSASSA-PKCS1-v1_5 with SHA2-256
    signed_data = lp(lp(struct.pack('<I', ALGO) + lp(digest))) + lp(lp(cert)) + lp(b'')
    sig = key.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())
    pub = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    signer = lp(signed_data) + lp(lp(struct.pack('<I', ALGO) + lp(sig))) + lp(pub)
    v2 = lp(lp(signer))
    pair = struct.pack('<Q', len(v2) + 4) + struct.pack('<I', 0x7109871a) + v2
    size = len(pair) + 8 + 16
    block = struct.pack('<Q', size) + pair + struct.pack('<Q', size) + b'APK Sig Block 42'
    new_eo = eo[:16] + struct.pack('<I', cd_off + len(block)) + eo[20:]
    open(out, 'wb').write(contents + block + cd + new_eo)

if __name__ == '__main__':
    tmp = sys.argv[2] + '.aligned'
    align(sys.argv[1], tmp)
    sign(tmp, sys.argv[2], sys.argv[3])
    os.remove(tmp)
    print('signed', sys.argv[2])
