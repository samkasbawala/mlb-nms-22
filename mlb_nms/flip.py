from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass
from math import floor
from typing import Any, List, Dict
from tqdm import tqdm
import requests

from mlb_nms.min_sell_values import MLB_CARD_QUICK_SELL_VALUES, REST_QUICK_SELL_VALUES

API = "https://mlb22.theshow.com/apis"


@dataclass
class Card:
    """An MLB the Show Item abstracted into a Python class"""

    name: str
    _type: str
    best_sell_price: int
    best_buy_price: int
    img: str
    rarity: str
    ovr: int

    @property
    def profit(self) -> int:

        # If either of these values are 0, that means no one is selling or buying
        # We shouldn't consider these cards, and the profit should be considered 0
        if self.best_buy_price == 0 or self.best_sell_price == 0:
            return 0

        if self._type == "mlb_card":
            return self.__mlb_card_profit()
        else:
            return self.__other_card_profit()

    def __mlb_card_profit(self) -> int:
        """Returns the profit of an mlb_card

        Returns:
            int: the profit from flipping the card based on the current market
        """

        return floor(
            max(self.best_sell_price, MLB_CARD_QUICK_SELL_VALUES.get(self.ovr, 5)) * 0.9
            - self.best_buy_price
        )

    def __other_card_profit(self) -> int:
        """Returns the profit of any other type of item in MLB the Show 22

        Returns:
            int: the profit from flipping the card based on the current market
        """

        return floor(
            max(self.best_sell_price, REST_QUICK_SELL_VALUES[self.rarity]) * 0.9
            - self.best_buy_price
        )

    def __repr__(self) -> str:
        return (
            f"Card(name={self.name}, _type={self._type}, "
            f"best_sell_price={self.best_sell_price}, "
            f"best_buy_price={self.best_buy_price}, profit={self.profit})"
        )


def get_cards(_type: str = "mlb_card", max_buy_price: int = 1000001) -> List[Card]:
    """Function returns a list of Card objects after sending a request to the API. User
    can filter the search based on the type of card and the max amount the user is
    willing to spend on a given card.

    Args:
        _type (str, optional): The type of item that you want to try and flip. The
            possible values are "mlb_card", "stadium", "equipment", "sponsorship", or
            "unlockable". Defaults to "mlb_card".

        max_buy_price (int, optional): This is the max amount of stubs you are willing
            to spend on a given card. Based on the current sell now value.
            Defaults to 1000001.

    Returns:
        List[Card]: list of Card objects matching the search criteria
    """

    # Create the url to get all listings on the marketplace w/search criteria
    listings_url = (
        f"{API}/listings.json?type={_type}&max_best_buy_price={max_buy_price}"
    )

    # Get the total number of pages that we need to parse through
    request = requests.get(listings_url)
    request_json: Dict[Any, Any] = request.json()
    total_pages: int = int(request_json["total_pages"])

    # List to hold all of the Card objects on the pages that we want
    cards: List[Card] = []

    # Call requests to the pages using threads, tqdm to monitor progess
    with tqdm(total=total_pages, desc="Processesing...") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:

            # Use map to kick off threads, need to pass in pbar, url, and page
            results = executor.map(
                __get_cards_on_page,
                [pbar] * total_pages,
                [listings_url] * total_pages,
                list(range(1, total_pages + 1)),
            )

            # Concat results
            for result in results:
                cards.extend(result)

    return cards


def __get_cards_on_page(pbar: tqdm, listings_url: str, page: int) -> List[Card]:
    """Helper function to get all the cards on a particular page. Should not be called
    explicitly by the user.

    Args:
        pbar (tqdm): pbar object that is being shared by the other threads.
        listings_url (str): The base listing url with the original search criteria.
        page (int): The page we will be searching on.

    Returns:
        List[Card]: A list of cards abstracted to Card objects on the current page.
    """

    # Json of the current page
    request_page = requests.get(f"{listings_url}&page={page}")
    request_page_json = request_page.json()

    # Extract the list of listings
    listings_page: List[Dict[str, Any]] = request_page_json["listings"]

    cards: List[Card] = []

    # Create a Card object for all the cards on the page
    for listing in listings_page:
        card = Card(
            name=listing["listing_name"],
            _type=listing["item"]["type"].lower(),
            best_sell_price=int(listing["best_sell_price"]),
            best_buy_price=int(listing["best_buy_price"]),
            img=listing["item"]["img"],
            rarity=listing["item"]["rarity"].lower(),
            ovr=int(listing["item"].get("ovr", 0)),
        )

        # Append to list
        cards.append(card)

    # Update progress bar
    pbar.update()

    return cards


def get_flips(cards: List[Card], min_profit: int) -> List[Card]:
    """Takes in a list of Card objects and returns a sorted list of cards that will
    return a profit if flipped.

    Args:
        cards (List[Card]): List of Card objects

    Returns:
        List[Card]: list of Card objects
    """

    # Get cards that will return a profit when flipped
    cards_w_profit = [card for card in cards if card.profit > min_profit]
    return sorted(cards_w_profit, key=lambda x: x.profit, reverse=True)
