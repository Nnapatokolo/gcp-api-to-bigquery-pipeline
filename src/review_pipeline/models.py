from dataclasses import dataclass
from datetime import datetime


@dataclass
class Review:
    """
    Represents a validated customer review.

    Every Review object must contain:
    - A review ID
    - A valid timestamp
    - A customer ID
    - An order reference
    - Review text
    - A rating between 1 and 5
    """

    review_id: str
    posted_at: str
    customer_id: str
    order_reference: str
    review_text: str
    rating: int

    def __post_init__(self) -> None:
        """
        Validate the Review immediately after it is created.

        Raises:
            ValueError: If any required field is missing or invalid.
        """
        self.review_id = self.review_id.strip()
        self.posted_at = self.posted_at.strip()
        self.customer_id = self.customer_id.strip()
        self.order_reference = self.order_reference.strip()
        self.review_text = self.review_text.strip()

        if not self.review_id:
            raise ValueError("Review ID must not be empty.")

        if not self.posted_at:
            raise ValueError(
                f"Review {self.review_id}: posted_at must not be empty."
            )

        if not self.customer_id:
            raise ValueError(
                f"Review {self.review_id}: customer_id must not be empty."
            )

        if not self.order_reference:
            raise ValueError(
                f"Review {self.review_id}: order_reference must not be empty."
            )

        if not 1 <= self.rating <= 5:
            raise ValueError(
                f"Review {self.review_id}: rating must be between 1 and 5."
            )

        self._validate_timestamp()

    def _validate_timestamp(self) -> None:
        """
        Confirm that posted_at contains a valid ISO 8601 timestamp.
        """
        normalized_timestamp = self.posted_at.replace("Z", "+00:00")

        try:
            datetime.fromisoformat(normalized_timestamp)
        except ValueError as error:
            raise ValueError(
                f"Review {self.review_id}: "
                f"posted_at is not a valid ISO timestamp: {self.posted_at}"
            ) from error  