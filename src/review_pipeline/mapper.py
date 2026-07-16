"""
Convert raw review dictionaries into validated Review objects.
"""

from typing import Any

from review_pipeline.models import Review


def parse_rating(value: Any) -> int:
    """
    Convert a raw rating value into an integer.

    Args:
        value: Rating value received from the source data.

    Returns:
        The rating as an integer.

    Raises:
        ValueError: If the rating cannot be converted to an integer.
    """
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Rating must be a whole number. Received: {value!r}"
        ) from error


def map_review(review_data: dict[str, Any]) -> Review:
    """
    Convert one raw review dictionary into a validated Review object.

    Args:
        review_data: Raw review data loaded from JSON.

    Returns:
        A validated Review object.
    """
    return Review(
        review_id=str(review_data.get("id", "")),
        posted_at=str(review_data.get("postedAt", "")),
        customer_id=str(review_data.get("userId", "")),
        order_reference=str(review_data.get("orderNumber", "")),
        review_text=str(review_data.get("review", "")),
        rating=parse_rating(review_data.get("rating", 0)),
    )