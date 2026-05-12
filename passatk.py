import math

def calculate_pass_at_k(n, c, k):
    """
    n: Anzahl der gesamten Versuche bzw. generierten Code-Samples (unterschiedliche Varianten) (z.B. 10)
    c: Anzahl der korrekten Versuche, die den Unittests bestehen (z.B. 3)
    k: Anzahl der betrachteten Versuche, die gemessen werden sollen (z.B. 5)
    """
    if n - c < k:
        return f"Die Wahrscheinlichkeit für Pass@{k} mit n={n}, c={c}, k={k} = 100% (Alle korrekten Versuche passen in die Top-{k})"
    
    # Kombinatorik: 1 - (n-c über k) / (n über k)
    def combinations(n, k):
        return math.comb(n, k)
    
    pass_at = 1.0 - (combinations(n - c, k) / combinations(n, k))

    return f"Die Wahrscheinlichkeit für Pass@{k} mit n={n}, c={c}, k={k} = {pass_at * 100:.2f}%"

# Beispiel
if __name__ == "__main__":
    p_at_5 = calculate_pass_at_k(10, 3, 5)
    print(p_at_5)