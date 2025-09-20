"""CartBoard schema and creator for text frames."""

from dataclasses import dataclass
import pandas as pd

COLUMNS = [
    "original_text", "refined_text", "rating",
    "pii_flag", "non_alphabetical_flag", "lang_mix_flag"
]

@dataclass
class CartBoard:
    @staticmethod
    def new(df=None):
        if df is None:
            return pd.DataFrame({c: [] for c in COLUMNS})
        # pastikan kolom minimal ada
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = None
        return df[COLUMNS]

