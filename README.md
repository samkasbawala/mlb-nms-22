# MLB NMS 22
Hey all!
This is a quick python package that uses the Mlb the Show 22 API in order to find good deals on the market.
The idea is that we can compare the Buy Now and Sell Now price to see if we can flip the card for a profit.

In the MLB the Show videogames, there is a 10% tax on sales made in the marketplace.
This means that in order to make a profit when flipping a card, you need to sell card at least 10% higher than the price you bought the card for.

So for example, say you bought a card for 900 stubs.
in order to make a profit when selling the card, you need to sell the card at at least 1000 stubs in order to break even.
When you sell the card at 1000 stubs, the market will incur its 10% tax, leaving you with .9 * 1000 = 900 stubs, the same number you bought the card for.

Again, for example, if you sell a card 1001 stubs, you will get back .9 * 1000 = 900.9 stubs.
For the purposes of this tool, we will assume the game rounds down if the 10% tax ever results in a float value.
So selling the card at 1001 stubs will still yield a 900 stub return.
You will need to sell the card at 1002 stubs in order to get 901 stubs back, a 1 stub profit.

# Installation
This package requires Python 3.7+ and requires both pip and git to be installed on your machine.
To install, simply run
```
pip install git+https://github.com/samkasbawala/mlb-nms-22.git
```

# Usage
This package can be used as both a CLI tool and as a python package in your own projects.
Once the package is installed, you can run it from the command line by simply typing:
```
mlb-nms
```
To get any help regarding the optional parameters, type:
```
mlb-nms --help
```
The tool will display a table of results sorted in descending order with respect to profit.

## Optional Parameters
### `type`
Must be one of the following (`mlb_card`, `stadium`, `equipment`, `sponsorship`, `unlockable`).
By default, it is set to `mlb_card` if no value is supplied.
```
mlb-nms --type sponsorship
```

### `max_buy`
The max amount of stubs you are willing to spend on a card.
This value is determined by the sell now value on the marketplace.
All cards more expensive than this value will not be returned.
By default, this is set to `1000001`, which is the highest amount in the game.
```
mlb-nms --max_buy 25000
```

### `min_profit`
The minimum profit you wish to get back after flipping a card.
By default, this is set to `200`.
Any cards that do not yield a profit of at least the specified value will not be shown in the results table.
**NOTE: too low of a value might display too many options to see depending on your terminal settings.**
```
mlb-nms --min_profit 500
```

# Todo
As of right now, there are no test cases.
These should really be added to ensure that the logic is sound.