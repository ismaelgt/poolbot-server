from math import pow

def format_matches_to_show_form(matches, player):
    """Return a string in a `W L L W` format for a given player."""
    return ' '.join(
        ['W' if match.winner == player else 'L' for match in matches]
    )

def form_cache_key(player):
    """Return the cache key for the per player form cache."""
    return "form_{slack_id}".format(slack_id=player.slack_id)

def calculate_elo(a, b, result):
    """Returns the two players elos as an array [a, b].
    Result is +1 for a victory, -1 for b victory, and 0 for draw.
    """
    K = 32
    E = 400

    def escore(elo):
        return pow(10, elo / E)

    def ratio(a_, b_):
        return a_ / (a_ + b_)

    a_s = escore(a)
    b_s = escore(b)

    a_r = ratio(a_s, b_s);
    b_r = ratio(b_s, a_s);

    a_n = .5 if result == 0 else 1 if result > 0 else 0
    b_n = .5 if result == 0 else 1 if result < 0 else 0

    return [
        a + K * (a_n - a_r),
        b + K * (b_n - b_r)
    ]
