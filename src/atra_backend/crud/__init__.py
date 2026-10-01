"""CRUD module."""

from atra_backend.crud.candle_crud import (
    count_candles,
    create_candle,
    create_candles,
    delete_candle,
    get_candle,
    get_candles,
    get_latest_candle,
    update_candle,
)
from atra_backend.crud.validation_crud import (
    count_validation_results,
    create_validation_result,
    create_validation_results,
    delete_validation_result,
    get_validation_result,
    get_validation_results,
    get_validation_results_for_candle,
)

__all__ = [
    # Candle CRUD
    "get_candle",
    "get_candles",
    "get_latest_candle",
    "create_candle",
    "create_candles",
    "update_candle",
    "delete_candle",
    "count_candles",
    # Validation CRUD
    "get_validation_result",
    "get_validation_results",
    "get_validation_results_for_candle",
    "create_validation_result",
    "create_validation_results",
    "delete_validation_result",
    "count_validation_results",
]
