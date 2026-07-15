from dataclasses import dataclass


@dataclass
class Review:
    """
    Represents a customer review after it has been extracted
    from the source system.
    """

    review_id: str
    posted_at: str
    customer_id: str
    order_reference: str
    review_text: str
    rating: int