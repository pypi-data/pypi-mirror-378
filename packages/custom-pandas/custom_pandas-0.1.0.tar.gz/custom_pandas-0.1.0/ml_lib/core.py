import numpy as np
import pandas as pd

# 1️⃣ Candidate Elimination (CE)
def CE(X, y):
    s = X[0].copy()  # Initial specific hypothesis
    g = [["?"]*len(X[0]) for _ in range(len(X[0]))]  # Initial general hypothesis

    print("=== Candidate Elimination (CE) ===")
    print("Initial S:", s)
    print("Initial G:", g)

    for i, x in enumerate(X):
        if y[i] == "Yes":
            for j in range(len(s)):
                if s[j] != x[j]:
                    s[j] = "?"
            g = [gi for gi in g if all(gi[j] == "?" or gi[j] == s[j] for j in range(len(s)))]
        else:
            for j in range(len(s)):
                if s[j] != x[j]:
                    g[j][j] = s[j]

        print(f"\nAfter example {i+1} ({x}, {y[i]}):")
        print("S:", s)
        print("G:", g)

    print("\nFinal S:", s)
    print("Final G:", g)
    return s, g


# 2️⃣ Find-S
def FindS(X, y):
    s = X[0].copy()
    print("=== Find-S ===")
    print("Initial S:", s)
    for i, x in enumerate(X):
        if y[i] == "Yes":
            for j in range(len(s)):
                if s[j] != x[j]:
                    s[j] = "?"
        print(f"After example {i+1} ({x}, {y[i]}): S={s}")
    print("Final S:", s)
    return s


# 3️⃣ FOIL Gain example
def FOIL_gain(df, target_col):
    print("=== FOIL Gain ===")
    total_entropy = 0
    from math import log2

    # calculate total entropy
    counts = df[target_col].value_counts()
    total = sum(counts)
    for count in counts:
        p = count/total
        total_entropy -= p * log2(p)
    print(f"Total Entropy of {target_col}: {total_entropy}")

    # just printing each column's "information" as example
    for col in df.columns:
        if col == target_col:
            continue
        print(f"Column: {col}")
    return total_entropy


# 4️⃣ Simple example function: print basic stats of dataset
def dataset_stats(df):
    print("=== Dataset Stats ===")
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("Head of dataset:")
    print(df.head())
