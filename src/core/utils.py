def format_matches_to_show_form(matches, player):
    """Return a string in a `W L L W` format for a given player."""
    return ' '.join(
        ['W' if match.winner == player else 'L' for match in matches]
    )


def form_cache_key(player):
    """Return the cache key for the per player form cache."""
    return "form_{slack_id}".format(slack_id=player.slack_id)
