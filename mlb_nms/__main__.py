import argparse
from tabulate import tabulate
from typing import List, Optional, Sequence

from mlb_nms.flip import Card, get_cards, get_flips


def main(argv: Optional[Sequence[str]] = None) -> int:

    # Parser ---------------------------------------------------------------------------
    parser = argparse.ArgumentParser()

    # Optional arguments ---------------------------------------------------------------
    # Type of card
    parser.add_argument(
        "--type",
        choices=("mlb_card", "stadium", "equipment", "sponsorship", "unlockable"),
        type=str,
        default="mlb_card",
        help=("Specify the type of item to search for. (default: %(default)s)"),
    )

    # Max stubbs willing to spend
    parser.add_argument(
        "--max_buy",
        type=int,
        default=1000001,
        help=(
            "The max amount of stubbs you are willing to spend on a given card. Based "
            "on the current sell now value. (default: %(default)s)"
        ),
    )

    # Min profit
    parser.add_argument(
        "--min_profit",
        type=int,
        default=200,
        help=(
            "The minimum profit amount you want to make from flipping. Too low of a "
            "value might cause not all of the results to show up in your terminal "
            "(default: %(default)s)"
        ),
    )

    args = parser.parse_args(argv)

    # Get the cards and display them ---------------------------------------------------
    cards = get_cards(args.type, args.max_buy)
    flips = get_flips(cards, args.min_profit)

    # Separate progress bar from results
    print()
    __show_results(flips)

    return 0


def __show_results(cards: List[Card]) -> None:
    """Helper function to show the results from the call to the API

    Args:
        cards (List[Card]): List of cards
    """
    results = [
        [
            card.name,
            card.best_sell_price,
            card.best_buy_price,
            card.rarity,
            card.ovr,
            card.profit,
        ]
        for card in cards
    ]

    print(
        tabulate(
            results,
            headers=[
                "Item Name",
                "Best Sell Price",
                "Best Buy Price",
                "Rarity",
                "Overall",
                "Profit",
            ],
            tablefmt="orgtbl",
        )
    )


if __name__ == "__main__":
    exit(main())
