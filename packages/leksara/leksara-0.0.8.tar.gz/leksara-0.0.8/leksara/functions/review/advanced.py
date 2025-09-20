"""Advanced review mining: rating, elongation, acronym, slang, contraction, normalization."""

import re
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# buat stemmer sekali saja (hemat waktu)
_factory = StemmerFactory()
_STEMMER = _factory.create_stemmer()

def replace_rating(text):
    pass

def shorten_elongation(text: str, max_repeat: int = 2) -> str:
    """Kurangi pengulangan karakter hingga maksimal `max_repeat` kemunculan.

    Contoh: mantuuulll -> mantul (dengan max_repeat=1 atau 2 sesuai preferensi)
    
    TODO: Implementasi fungsi ini oleh kontributor selanjutnya.
    """
    if max_repeat < 1:
        raise ValueError("max_repeat must be >= 1")

    # Regex: (.)\1{n,} menangkap karakter yang diulang lebih dari n kali
    else:
        pattern = re.compile(r"(.)\1{" + str(max_repeat) + r",}")
        text = pattern.sub(lambda m: m.group(1) * max_repeat, text)

    return text

def replace_acronym(text):
    pass

def remove_acronym(text):
    pass

def normalize_slangs(text):
    pass

def expand_contraction(text):
    pass

# Deteksi placeholder whitelist (Private Use Area) agar tidak di-stem
def _is_masked_whitelist_token(token: str) -> bool:
    return any(0xE000 <= ord(ch) <= 0xF8FF for ch in token)

def _is_bracket_token(token: str) -> bool:
    return len(token) >= 2 and token.startswith("[") and token.endswith("]")

def word_normalization(
    text: str,
    *,
    method: str = "stem",
    word_list=None,
    mode: str = "keep",
) -> str:
    """Normalisasi kata dengan stemming/lemmatization.

    Args:
        text: input string
        method: "stem" (default, pakai Sastrawi), "lemma" (future).
        word_list: daftar kata spesial (list[str])
        mode: 
            - "keep": jangan stem kata dalam word_list
            - "only": hanya stem kata dalam word_list
    """
    if not isinstance(text, str):
        return text

    if word_list is None:
        word_list = []

    word_set = {w.lower() for w in word_list}
    words = text.split()
    out = []

    if method == "stem":
        if mode == "keep":
            for w in words:
                # Lindungi placeholder whitelist dan token bracket
                if _is_masked_whitelist_token(w) or _is_bracket_token(w):
                    out.append(w)
                else:
                    out.append(w if w.lower() in word_set else _STEMMER.stem(w))
        elif mode == "only":
            for w in words:
                if _is_masked_whitelist_token(w) or _is_bracket_token(w):
                    out.append(w)
                else:
                    out.append(_STEMMER.stem(w) if w.lower() in word_set else w)
        else:
            raise ValueError("mode harus 'keep' atau 'only'")
    else:
        # kalau nanti ada lemmatizer lain
        out = words

    return " ".join(out)
