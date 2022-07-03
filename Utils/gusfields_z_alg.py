#!/usr/bin/python3.10
def z_alg(pat: list[int]) -> list[int | None]:
    """
    Gusfield's Z-algorithm.
    Finds all the occurrences of substrings in 'pat' matching the prefix (of itself). Runs in linear time.
    :return: an array where the index is the longest substring of 'pat' at position z[index] (or is the size of the
    z-box)
    :time complexity: O(n) where n is the length of 'pat'
    """

    pat_len = len(pat)
    z: list[int | None] = [None] * pat_len

    if pat_len == 0 or pat_len == 1:
        return z

    l = r = None

    # base case (Z_2)
    z[1] = 0
    idx = 1
    while idx <= pat_len:
        if idx >= pat_len or pat[idx - 1] != pat[idx]:
            if z[1] > 0:
                l = 1
                r = z[1]
            elif z[1] == 0:
                l = r = 0
            else:
                raise Exception('Base case invariant broken')
            break
        z[1] += 1
        idx += 1

    # general case
    k = 2
    while k < pat_len:
        # Case 1: k > r
        if k > r:
            z[k] = j = 0
            q = k
            while q <= pat_len:
                if q >= pat_len or pat[q] != pat[j]:
                    if z[k] > 0:
                        l = k
                        r = q - 1
                    elif z[k] == 0:
                        pass
                    else:
                        raise Exception('General case 1 (k > r) invariant broken')
                    break
                z[k] += 1
                j += 1
                q += 1

        # Case 2: k <= r
        elif k <= r:
            if z[k - l] < r - k + 1:
                z[k] = z[k - l]
            elif z[k - l] > r - k + 1:
                z[k] = r - k + 1
            else:
                for _ in range(k, pat_len):
                    r += 1
                    if r == pat_len or pat[r - k] != pat[r]:
                        z[k] = r - k
                        l = k
                        r -= 1
                        break

        k += 1

    return z


if __name__ == "__main__":
    print(z_alg(list(map(ord, "$a;rystny"))))
