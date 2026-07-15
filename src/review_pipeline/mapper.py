"""
Convert raw review dictionaries into Review objects.
"""

from typing import Any

from review_pipeline.models import Review


def map_review(review_data: dict[str, Any]) -> Review:
    """
    Convert one raw review dictionary into a Review object.

    Args:
        review_data: Raw review data loaded from JSON.

    Returns:
        A populated Review object.
    """
    return Review(
        review_id=str(review_data.get("id", "")),
        posted_at=str(review_data.get("postedAt", "")),
        customer_id=str(review_data.get("userId", "")),
        order_reference=str(review_data.get("orderNumber", "")),
        review_text=str(review_data.get("review", "")),
        rating=int(review_data.get("rating", 0)),
    )