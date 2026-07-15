"""
GCP API to BigQuery Incremental Pipeline.

This first version reads synthetic customer reviews from a local JSON file.
Later versions will retrieve data from an API and load it into BigQuery.
"""

import argparse
import json
from pathlib import Path
from typing import Any


def load_reviews_from_file(file_path: str) -> list[dict[str, Any]]:
    """
    Read customer reviews from a JSON file.

    Args:
        file_path: Path to the JSON file containing review records.

    Returns:
        A list of review dictionaries.

    Raises:
        FileNotFoundError: If the supplied file does not exist.
        ValueError: If the JSON structure is not valid for this project.
        json.JSONDecodeError: If the file does not contain valid JSON.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"The file does not exist: {file_path}")

    if not path.is_file():
        raise ValueError(f"The supplied path is not a file: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError("The JSON file must contain a JSON object.")

    reviews = payload.get("items")

    if not isinstance(reviews, list):
        raise ValueError("The JSON file must contain an 'items' list.")

    return reviews


def display_reviews(reviews: list[dict[str, Any]]) -> None:
    """
    Print the reviews in a readable format.

    Args:
        reviews: List of review dictionaries.
    """
    print(f"\nNumber of reviews loaded: {len(reviews)}\n")

    for position, review in enumerate(reviews, start=1):
        print(f"Review {position}")
        print(f"  Review ID: {review.get('id', 'Not provided')}")
        print(f"  Posted at: {review.get('postedAt', 'Not provided')}")
        print(f"  Customer: {review.get('userId', 'Not provided')}")
        print(f"  Order: {review.get('orderNumber', 'Not provided')}")
        print(f"  Rating: {review.get('rating', 'Not provided')}")
        print(f"  Review: {review.get('review', 'Not provided')}")
        print("-" * 60)


def parse_arguments() -> argparse.Namespace:
    """
    Read command-line arguments supplied by the user.

    Returns:
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Read customer reviews from a local JSON file."
    )

    parser.add_argument(
        "--source-file",
        required=True,
        help="Path to the JSON file containing customer reviews.",
    )

    return parser.parse_args()


def main() -> int:
    """
    Run the local review-file pipeline.

    Returns:
        Zero when the program completes successfully.
    """
    args = parse_arguments()

    try:
        reviews = load_reviews_from_file(args.source_file)
        display_reviews(reviews)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"Pipeline failed: {error}")
        return 1

    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())