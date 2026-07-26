# Part 3 — AI Assistants vs. PulseFeed's Rate Limiter

Companion code for Part 3 of *Data Structures and Algorithms in Python: Beyond the
Cheat Sheet*. Part 2 shipped a hand-written, lazy-refill `TokenBucket` rate limiter
for PulseFeed. This part hands the exact same spec and test suite to three AI coding
assistant prompting conditions in isolation (no shared context, no knowledge of each
other or of Parts 1–2's lessons), and then actually measures — not estimates — what
each one shipped, next to the real Part 2 baseline.

## What's here

```
baseline_part2/               The actual, human-authored TokenBucket from Part 2
                               (github.com/krpraveen0/pulsefeed-dsa-course,
                               part-02-building-pulsefeed-trending-engine), copied
                               here unmodified as the non-AI reference point.

spec_only/                    Candidate 1: given only the spec + test file, nothing
                               else.

explicit_o1/                  Candidate 2: explicitly instructed "make allow() run
                               in O(1) time."

optimize_for_production/      Candidate 3: instructed "optimize this for a
                               production service" -- shipped __slots__ and a
                               threading.Lock around allow().

benchmark.py                  The measurement harness. Loads each candidate's
                               rate_limiter.py from its own subprocess (so no
                               module state, GC pressure, or import side effects
                               leak between candidates), and for each one measures:
                                 - TokenBucket(...) construction cost (single-shot
                                   and mean of 5,000)
                                 - real wall-clock time per allow() call across
                                   100 / 1,000 / 10,000 / 100,000 sequential calls
                                   on one instance
                                 - real instance memory footprint at each call
                                   count, via sys.getsizeof() (both raw, and a
                                   corrected "total" number that adds the separate
                                   __dict__ object's size for non-slotted classes,
                                   so __slots__ vs __dict__ instances are compared
                                   fairly) and tracemalloc peak bytes allocated
                                   during the call loop
                                 - a focused 10,000-call x 5-repeat comparison
                                   aimed specifically at whether
                                   optimize_for_production's threading.Lock or
                                   __slots__ produce measurable real overhead

results.json                  Raw measured output from the most recent benchmark.py
                               run (all four implementations, this machine).

results.md                    The same results, formatted as markdown tables.

*/test_rate_limiter.py        Each candidate directory (including baseline_part2)
                               carries the identical pytest suite handed to the AI
                               assistants as the acceptance spec -- all four pass it.
```

Each of the four candidate directories is intentionally self-contained: every
`test_rate_limiter.py` does `from rate_limiter import TokenBucket`, so tests are run
from inside that specific directory (see below), never importing across candidates.
This mirrors how the harness itself isolates them — one subprocess, one module, no
cross-contamination.

## Running it

Requires Python 3.9+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run each candidate's own test suite (they cannot be run together — every candidate
defines its own `rate_limiter` module):

```bash
for d in baseline_part2 spec_only explicit_o1 optimize_for_production; do
  echo "=== $d ==="
  (cd "$d" && pytest -q)
done
```

Reproduce the benchmark numbers in `results.md` / `results.json` yourself:

```bash
python3 benchmark.py
```

This prints a full report to stdout and (re)writes `results.json` and `results.md`
in this directory. It takes a few seconds — each of the four candidates runs
100+1,000+10,000+100,000 `allow()` calls plus a 5-repeat, 10,000-call focused
comparison, each in its own subprocess.

## What the numbers actually show

All four implementations are algorithmically O(1) time / O(1) space per `allow()`
call — none of the three AI candidates shipped an accumulating-timestamp-list or
similar hidden-linear-scan bug that Part 2's correctness-only test suite wouldn't
catch. But "all O(1)" does not mean "measured identically":

- **Memory**: `optimize_for_production`'s `__slots__` instance has a genuinely
  smaller real footprint than the three `__dict__`-backed instances (72 bytes vs.
  152 bytes, instance object + its `__dict__` combined) — the one place a candidate's
  extra engineering effort clearly paid off.
- **Time**: that same candidate is consistently ~60–70% slower per `allow()` call
  than the other three, on this machine, across every call count measured and
  reproducible across repeated runs — the cost of acquiring/releasing a
  `threading.Lock` on every single-threaded call, a real tradeoff for thread-safety
  that a single-threaded benchmark doesn't need but a production service handling
  concurrent requests would.
- **The other three** (`baseline_part2`, `spec_only`, `explicit_o1`) land within a
  narrow, overlapping band of each other — not perfectly identical, but not the kind
  of order-of-magnitude gap you'd expect from an actual complexity bug.

See `results.md` for the exact measured numbers this run produced on this machine.

## Article

Part 3: "I Asked One AI to Build the Same Rate Limiter Three Ways — Only One Prompt
Got the Complexity Right" (link once published).
