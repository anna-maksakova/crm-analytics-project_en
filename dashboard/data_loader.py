"""
Загрузка данных из parquet.
Кеш через functools.lru_cache — данные читаются один раз при старте.
"""
from functools import lru_cache
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"


@lru_cache(maxsize=1)
def load_deals() -> pd.DataFrame:
    """Очищенные сделки. Кешируется при первом вызове."""
    return pd.read_parquet(DATA_DIR / "deals_clean.parquet")


@lru_cache(maxsize=1)
def load_calls() -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / "calls_clean.parquet")


@lru_cache(maxsize=1)
def load_spend() -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / "spend_clean.parquet")


def filter_deals(
    deals: pd.DataFrame,
    date_range: tuple | None = None,
    sources: list | None = None,
    products: list | None = None,
) -> pd.DataFrame:
    """Применить глобальные фильтры к Deals.

    Используется во всех табах. Пустой список или None = без фильтра.
    """
    df = deals
    if date_range and date_range[0] and date_range[1]:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df = df[df["Created Time"].between(start, end)]
    if sources:
        df = df[df["Source"].isin(sources)]
    if products:
        df = df[df["Product"].isin(products)]
    return df
