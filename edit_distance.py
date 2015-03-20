import numpy as np

def calculate_edit_distance(source, target):
    if len(source) < len(target):
        return calculate_edit_distance(target, source)

    # Now that we now that source is always bigger than target
    if len(target) == 0:
        return len(source)

    # tuple() is called to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # A dynamic algorithm is used, but with the added optimization
    # that we only need the last two rows of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows langer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

