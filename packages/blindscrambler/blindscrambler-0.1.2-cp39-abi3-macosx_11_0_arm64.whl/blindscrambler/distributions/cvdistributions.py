# Metadata:
# Author: Syed Raza
# email: sar0033@uah.edu

# use python secrets to make a normally distributed random samples
import secrets

def uniform(a: float = 0.0, b: float = 1.0) -> float:
    """
    Cryptographically secure sample
    """
    # 53 random bits gives 53-bit precision double
    u = secrets.randbits(53) / (1 << 53) # in [0, 1)

    return a + (b - a) * u