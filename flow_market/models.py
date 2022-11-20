from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)


class Constants(BaseConstants):
    name_in_url = "flow_market"
    players_per_group = 6
    num_rounds = 14


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    buyer_quiz1 = models.StringField(
        label="Suppose you want to buy 400 units in 100 seconds. Suppose you set up your low price, high price, and max rate so that you are executing your buy order at a rate of 2 units per second. If nothing else changes in the market, are you going to acquire the 400 units that you want?",
        choices=["Yes", "No"],
    )
    buyer_quiz2 = models.StringField(
        label="If you send a buy order with a high price of $15 per unit and a max rate of 5 units per second. If the current price is $16 per unit, what is the rate at which you would execute your order?",
        choices=["0 unit per second", "5 units per second"],
    )
    buyer_quiz3 = models.StringField(
        label="Suppose you send a buy order with a low price of $10 per unit and a max rate of 5 units per second. If the current price is $9 per unit, what is the rate at which you would execute your order?",
        choices=["0 unit per second", "5 units per second"],
    )
    buyer_quiz4 = models.StringField(
        label="Let us say you have bought 300 units up to the second 110, and you paid, on average, $10 per unit. Suppose you do not have any other transaction in the trading round. What is your profit for the round?",
        choices=[
            "(12 - 10) * 500 = 1000",
            "(12 - 10) * 300 = 600",
            "(10 - 0) * 300 = 3000",
            "(12 - 0) * 500 = 6000",
        ],
    )
    buyer_quiz5 = models.StringField(
        label="Suppose you bought 500 units up to the second 110, and you paid, on average, $10 per unit. Suppose you do not have any other transaction in the trading round. What is your profit for the round?",
        choices=[
            "(12 - 10) * 500 = 1000",
            "(12 - 10) * 300 = 600",
            "(10 - 0) * 300 = 3000",
            "(12 - 0) * 500 = 6000",
        ],
    )
    buyer_quiz6 = models.StringField(
        label="Suppose you bought 600 units up to the second 110, and you paid, on average, $10 per unit. Suppose you do not have any other transaction in the trading round. What is your profit for the round?",
        choices=[
            "(12 - 10) * 600 + (0 - 10) * 100 = 200",
            "(12 - 10) * 500 + (0 - 10) * 100 = 0",
            "(12 - 0) * 600 + (0 - 10) * 600 = 1200",
            "(12 - 0) * 500 + (0 - 10) * 100 = 5000",
        ],
    )
    seller_quiz1 = models.StringField(
        label="Suppose you want to sell 600 units in 100 seconds. Suppose you set up your low price, high price, and max rate so that you are executing your sell order at a rate of 6 units per second. If nothing else changes in the market, are you going to sell the 600 units that you want?",
        choices=["Yes", "No"],
    )
    seller_quiz2 = models.StringField(
        label="If you send a sell order with a low price equal to $10 per unit and a max rate of 6 units per second. If the current price is $8 per unit, what is the rate at which you would execute your order?",
        choices=["0 unit per second", "6 units per second"],
    )
    seller_quiz3 = models.StringField(
        label="Suppose you send a sell order with a high price of $14 per unit and a max rate of 6 units per second. If the current price is $17 per unit, what is the rate at which you would execute your order?",
        choices=["0 unit per second", "6 units per second"],
    )
    seller_quiz4 = models.StringField(
        label="Let us say you have sold 300 units up to the second 110 at an average price of $10 per unit. Suppose you do not have any other transaction in the trading round. What is your profit for the round?",
        choices=[
            "(10 - 8) * 500 = 1000",
            "(10 - 8) * 300 = 600",
            "(10 - 0) * 300 = 3000",
            "(8 - 0) * 500 = 4000",
        ],
    )
    seller_quiz5 = models.StringField(
        label="Suppose you have sold 500 units up to the second 110 at an average price of $10 per unit. Suppose you do not have any other transaction in the trading round. What is your profit for the round?",
        choices=[
            "(10 - 8) * 500 = 1000",
            "(10 - 8) * 300 = 600",
            "(10 - 0) * 300 = 3000",
            "(8 - 0) * 500 = 4000",
        ],
    )
    seller_quiz6 = models.StringField(
        label="Suppose you have sold 600 units up to the second 110 at an average price of $10 per unit. Suppose you do not have any other transaction in the trading round. What is your profit for the round?",
        choices=[
            "(10 - 8) * 600 + (10 - 20) * 100 = 200",
            "(10 - 8) * 500 + (10 - 20) * 100 = 0",
            "(0 - 8) * 600 + (10 - 0) * 600 = 1200",
            "(0 - 8) * 500 + (10 - 0) * 600 = 2000",
        ],
    )
