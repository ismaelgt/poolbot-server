from .models import Match, Player


def resync_player_match_counts():
    """Iterate over each player, count their win and loss count, then save this
    denormalized data onto the respective player instance.
    """

    players = Player.objects.all()
    for player in players:
        player.total_win_count = Match.objects.filter(winner=player).count()
        player.total_loss_count = Match.objects.filter(loser=player).count()
        player.save()
