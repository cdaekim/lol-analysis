from collections import defaultdict
from itertools import combinations

# update dictionary that counts # of times champion is selected
def update_champ_counts(champ_counts, teams):
    for a in teams:
        champ_counts[a] += 1

# update dictionary that counts the instances of all possible champion pairs
def update_champ_pair_counts (champ_pair_counts, teams):
    for (a, b) in combinations (teams, 2):
        champ_pair_counts[(a, b)] += 1
        champ_pair_counts[(b, a)] += 1
        
# update dictionary holding number of time the pair wins a game        
def update_champ_pair_wins(champ_pair_wins, teams):
    for (a, b) in combinations (teams, 2):
        if teams[5] == 1:
            champ_pair_wins[(a, b)] += 1
            champ_pair_wins[(b, a)] += 1


def filter_rules(champ_pair_counts, champ_counts, size, conf_threshold, sup_threshold):
    """
    Calculates support, confidence, lift for champion pairs and filters based on thresholds.

    Parameters
    ----------
    champ_pair_counts : defaultdict(int)
        Dictionary counting number of distinct pair occurrences.
    champ_counts : defaultdict(int)
        Dictionary counting number of individual champion occurrences.
    size : int
        len of dataframe from process_data method
    conf_threshold : float
        Confidence threshold (0–1) for filtering champion pairs.
    sup_threshold : float
        Support threshold (0–100) for filtering champion pairs.

    Returns
    -------
    results 
        - 'confidence': Dict of champion pairs with confidence values above `conf_threshold`.
        - 'lifts': Dict of champion pairs with lift values (only if confidence > `conf_threshold` and lift > 1).
        - 'supports': Dict of champion pairs with support values above `sup_threshold`.

    Notes
    -------
    Confidence measures how likely champion A is picked when champion B is picked (P(A|B)).
    Lift measures the strength of association between champion pair selection.
    Support measures how frequently a pair occurs in the dataset.
    """
    supports = {}
    confidence = {}
    lifts = {}
    

    for (a, b), pair_count in champ_pair_counts.items():
        # Support calculation
        support_ab = pair_count / size * 100
        if support_ab >= sup_threshold:
            supports[(a, b)] = support_ab

        # Confidence calculations
        conf_ab = pair_count / champ_counts[a] * 100
        conf_ba = pair_count / champ_counts[b] * 100

        # Lift calculation
        lift_ab = (pair_count / size) / ((champ_counts[a] / size) * (champ_counts[b] / size))


        # Filter based on confidence threshold
        if conf_ab >= conf_threshold:
            confidence[(a, b)] = conf_ab
            if lift_ab > 1:
                lifts[(a, b)] = lift_ab
        if conf_ba >= conf_threshold:
            confidence[(b, a)] = conf_ba
            if lift_ab > 1:
                lifts[(b, a)] = lift_ab

    return supports, confidence, lifts


def mine_rules(allTeams, withWins, sup_threshold, conf_threshold):
    champ_pair_counts = defaultdict(int)
    champ_counts = defaultdict(int)
    champ_pair_wins = defaultdict(int)
    size = len(allTeams)

    for teams in allTeams:
        update_champ_pair_counts(champ_pair_counts, teams)
        update_champ_counts(champ_counts, teams)
    
    for teams in withWins:
        update_champ_pair_wins(champ_pair_wins, teams)
    
    supports, confidence, lifts = filter_rules(champ_pair_counts, champ_counts, size, conf_threshold, sup_threshold)

    return supports, confidence, lifts,champ_pair_counts, champ_pair_wins