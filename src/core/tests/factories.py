from datetime import timedelta

from factory import DjangoModelFactory, fuzzy, Iterator, SubFactory

from core.models import Player, Match, Season


class PlayerFactory(DjangoModelFactory):
    class Meta:
        model = Player

    slack_id = fuzzy.FuzzyText(length=20)


class MatchFactory(DjangoModelFactory):
    class Meta:
        model = Match

    winner = SubFactory(PlayerFactory)
    loser = SubFactory(PlayerFactory)
    channel = '1234567890'


class SeasonFactory(DjangoModelFactory):
    class Meta:
        model = Season

    start_date = fuzzy.FuzzyDate()
    end_date = factory.LazyAttribute(lambda o: o.start_date + timdelta(days=10))
    active = False