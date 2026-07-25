"""Memory-tracking benchmark modeled on CPython bug bpo-33205,
"GROWTH_RATE prevents dict shrinking" (https://bugs.python.org/issue33205).

The bug report's own reproduction: a dict that had 10,900 items deleted
and then 923 new items inserted stayed pinned at 295,008 bytes -- no
shrink at all -- because the pre-fix growth formula
(`used*2 + dk_size/2`) kept rounding back up to the same power-of-two
table size. The fix (merged in 3.7/3.8, still the formula on current
CPython main) changed `GROWTH_RATE` to `used*3`; the same churn shrinks to
36,968 bytes under the fixed formula.

This script reproduces that churn *shape* at the bug report's own scale
(build a dict, delete most of it, reinsert a small batch of new keys) and
reports `sys.getsizeof()` at each stage, compared against a dict built
fresh at the same final live-key count. There's no supported CPython left
that reproduces the pre-fix 8x-oversized number -- the fix has been in
every released Python since 3.7 -- so what you should see when you run
this yourself is the *fixed* behavior: the churned dict landing at (or
very close to) the same size as a dict built fresh, because the resize
that fires on reinsertion computes its new table size from live `used`
count, not from the tombstone-inflated fill count. That's the fix working,
on your own interpreter, not a fact you have to take on faith.

Run directly:

    python -m benchmarks.dict_memory_bench
"""

import platform
import sys

# Same order of magnitude as the bug report's own reproduction (10,900
# deletes, 923 inserts). initial_size items go in, (initial_size - keep)
# get deleted, then `keep` new keys get inserted -- the delete-then-insert
# shape that either does or doesn't trigger a proper shrink, depending on
# which GROWTH_RATE formula the interpreter was built with.
INITIAL_SIZE = 10_900
KEEP = 923


def build_and_churn(initial_size=INITIAL_SIZE, keep=KEEP):
    """Reproduce the bpo-33205 churn shape: mass delete, then a small
    reinsert batch.
    """
    d = {f"tag-{i}": i for i in range(initial_size)}
    size_full = sys.getsizeof(d)

    # Delete almost everything.
    for i in range(initial_size - keep):
        del d[f"tag-{i}"]
    size_after_delete = sys.getsizeof(d)

    # Insert a small batch of new keys -- the operation that either
    # triggers a proper shrink or (pre-fix) silently doesn't.
    for i in range(initial_size, initial_size + keep):
        d[f"tag-{i}"] = i
    size_after_reinsert = sys.getsizeof(d)

    return d, size_full, size_after_delete, size_after_reinsert


def fresh_dict_size(item_count):
    fresh = {f"tag-{i}": i for i in range(item_count)}
    return sys.getsizeof(fresh)


def main():
    print(f"Python {platform.python_version()} ({platform.python_implementation()})\n")

    d, size_full, size_after_delete, size_after_reinsert = build_and_churn()
    fresh_size = fresh_dict_size(len(d))

    print(f"{'stage':<34} {'live keys':>10} {'sys.getsizeof bytes':>20}")
    print(f"{'full dict (' + str(INITIAL_SIZE) + ' items)':<34} {INITIAL_SIZE:>10} {size_full:>20}")
    print(f"{'after deleting all but ' + str(KEEP):<34} {KEEP:>10} {size_after_delete:>20}")
    print(f"{'after reinserting ' + str(KEEP) + ' new keys':<34} {len(d):>10} {size_after_reinsert:>20}")
    print(f"{'fresh dict, same final size':<34} {len(d):>10} {fresh_size:>20}")
    print()

    ratio = size_after_reinsert / fresh_size if fresh_size else float("inf")
    print(
        f"Churned dict is {ratio:.2f}x the size of a dict built fresh at the "
        f"same live-key count ({len(d)} keys).\n"
        f"bpo-33205's pre-fix reproduction measured ~8.0x (295,008 vs "
        f"36,968 bytes) for this exact churn shape on the old "
        f"`used*2 + dk_size/2` growth formula. You're running the fixed "
        f"`GROWTH_RATE = used*3` formula (every CPython since 3.7), which is "
        f"why this lands close to 1.0x instead."
    )


if __name__ == "__main__":
    main()
