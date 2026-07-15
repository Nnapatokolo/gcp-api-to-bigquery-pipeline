from models import Review

review = Review(
    review_id="review-001",
    posted_at="2026-07-01T09:30:00Z",
    customer_id="customer-101",
    order_reference="order-5001",
    review_text="Delivery was fast.",
    rating=5,
)

print(review)
print(review.review_text)
print(review.rating)