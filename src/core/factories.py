from factory import DjangoModelFactory, fuzzy, Iterator, SubFactory

from core.models import Player, Match


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
