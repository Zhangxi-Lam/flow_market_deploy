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
    quiz1 = models.IntegerField(label="What is 2 + 2?")
    quiz2 = models.StringField(
        label="What is the capital of Canada?",
        choices=["Ottawa", "Toronto", "Vancouver"],
    )
