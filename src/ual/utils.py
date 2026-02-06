import hashlib
import time

def generate_message_id(sender_id: str) -> str:
    timestamp = str(time.time())
    raw = f"{sender_id}:{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def compute_semantic_hash(content_bytes: bytes) -> str:
    """计算内容的语义哈希"""
    return hashlib.sha256(content_bytes).hexdigest()[:16]

def sign_message(content: bytes, private_key: str = "dummy_key") -> bytes:
    """
    模拟签名
    实际应用中应使用 Ed25519 或 RSA
    """
    return hashlib.sha256(content + private_key.encode()).digest()

def verify_signature(content: bytes, signature: bytes, public_key: str = "dummy_key") -> bool:
    """验证签名"""
    expected = hashlib.sha256(content + public_key.encode()).digest()
    return expected == signature
