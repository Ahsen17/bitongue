import re
from unicodedata import normalize

__all__ = ("Normalizer",)


class Normalizer:
    r"""Normalize text into a canonical comparable form.

    The pipeline is: casefold, replace non-word runs (``\W_``) with a
    single space, collapse whitespace, then apply NFKC normalization.

    Note:
        NFKC runs last, so compatibility decompositions can re-introduce
        non-word characters (e.g. ``㈱`` becomes ``(株)``). This ordering
        is documented behavior rather than an accident.
    """

    @staticmethod
    def normalize(*document: str) -> list[str]:
        """Normalize each input string.

        Args:
            document: Strings to normalize.

        Returns:
            One normalized string per input, in input order.
        """

        result: list[str] = []

        for text in document:
            text = re.sub(r"[\W_]+", " ", text.casefold())
            text = re.sub(r"\s+", " ", text).strip()
            text = normalize("NFKC", text)

            result.append(text)

        return result
