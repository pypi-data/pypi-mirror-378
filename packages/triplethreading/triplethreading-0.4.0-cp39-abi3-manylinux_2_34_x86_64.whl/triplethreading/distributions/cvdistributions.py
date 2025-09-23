import secrets

def uniform(a: float = 0.0, b: float = 1.0) -> float:
    u = secrets.randbits(53) / (1 << 53)
    return a + (b - a) * u
