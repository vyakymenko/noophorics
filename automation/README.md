# Automation

Half of the research cycle may be automated. The other half may not, and the
line is [in CONTRIBUTING](../CONTRIBUTING.md#automation-what-may-be-looped):
**execution versus interpretation.**

Everything here is the execution half.

| file | what it does |
|---|---|
| [`loop.py`](loop.py) | runs pre-registered experiments from a committed queue |
| [`watch.py`](watch.py) | reports state changes in a run already in flight |
| [`notify.py`](notify.py) | delivers a message to Telegram, or to stdout |
| [`queue.json`](queue.json) | the queue. Human-authored; the loop never writes it |
| `self-transfer.jsonl` | what each iteration believed it was doing, recorded before it ran |

## What the loop cannot do, by construction

- **Choose what to run.** The queue is committed, read once at start, and an
  edit mid-flight cannot redirect a running loop.
- **Run a command that has no pre-registration.** An entry whose prereg file
  does not exist is refused before anything starts.
- **Take a shell string.** Commands are argv lists. A shell string in a
  committed queue is an injection surface for anyone who can open a pull
  request.
- **Touch a pre-registration, PRINCIPIA, `theory/` or RETRACTIONS.** Checked
  before the loop starts *and* after every run; a run that leaves one modified
  stops the loop rather than warning about it.
- **Interpret anything.** It emits gate values against their thresholds, void
  reasons quoted from the runner, and effect sizes with their p-values. It never
  says whether a result is good.

The reason for the last one is not fastidiousness. An agent that generates a
hypothesis, designs the test, writes the prompts, runs it and rules on whether
it passed is a machine for confirming its own priors at speed. It does not
violate the pre-registration norm — every hypothesis is still committed before
its data — which is exactly why the norm alone does not protect against it. The
commit order stays honest while the independence that made the order meaningful
quietly disappears.

## The loop is an instance of its own subject

A long-running loop is a chain of **self-transfers**: each iteration hands its
understanding to the next through the narrow channel of a queue entry and a
commit message. That is [Problem 9](../theory/open-problems.md), and
[L5](../theory/laws.md#l5) predicts self-transfer should exhibit *maximal*
phantom agreement — an agent has every reason to believe its own summary
preserved what mattered.

So each entry records an `expect` field **before** it runs, and the ledger keeps
it beside what the run actually produced. The loop does not compute `Φ` from
that and does not act on it. Computing it is a measurement, and measurements
here are made by people.

## The bot reports and does not listen

`notify.py` has no polling loop, no webhook, and no command handling. A bot that
accepts instructions from a chat is remote code execution on the machine running
the experiments, and the thing that is actually wanted — knowing that a run
voided at 3am — needs none of it.

Setup, with the token supplied by you and never by this repository:

```bash
export NOOPHORICS_TG_TOKEN='...'   # from @BotFather
export NOOPHORICS_TG_CHAT='...'    # your numeric chat id
python3 automation/notify.py --test
```

Neither variable is written to disk, logged, or committed, and the module
redacts the token from its own error messages. **With either absent it prints to
stdout instead**, which is a fully supported mode: the loop must be useful
without a bot and must never require one.

## Watching a run already in flight

```bash
python3 automation/watch.py experiments/E-002b-phantom-agreement-ladder --total 627
```

Reports transitions, not a stream — deciles of progress, the runner
disappearing, a results file appearing, a void. Silence means nothing changed,
which is what makes it bearable overnight.

It exists because a gate that fires into an empty room is only half a gate.
E-001b would have burned thirty hours before crashing, and E-002's gate fired
and then waited for someone to look.

---

*This document is licensed CC BY 4.0.*
