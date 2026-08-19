# What a reader-facet study on `MERIDIAN-IX32` would actually require

**Written 2026-08-19, after [retraction 16](../../RETRACTIONS.md) and
[prior-art §11](../../theory/prior-art.md).** No new measurement is claimed here;
this is the design note the two-reader run turned out to need.

## Why this file exists

Generalizability theory's answer to "is this property the measure's or the
reader's?" is not an argument. It is a **D-study over a population of readers**,
and Brennan's sentence is why nothing cheaper works:

> "in any generalizability analysis there must be at least one random facet for
> the analysis to be meaningful. If all facets were fixed, then no generalization
> is involved, and all error variances are zero, be definition."

Every characterization this measure carries was estimated with the reader fixed
at `gpt-oss:120b`. Adding `qwen3.5:35b` did not make the reader facet random. It
made it a fixed facet with **two** levels, which is enough to notice a difference
and not enough to estimate a variance.

## The three things standing in the way, in order of cost

### 1. The two readers are not measured to the same depth — ~14 hours

`gpt-oss` has **four** sender passes on all 32 probes; `qwen` has **one**. A
minimum over four draws is smaller for free, which is exactly how retraction 16's
headline statistic manufactured itself. Any future margin comparison is invalid
until this is equalised.

Three further `qwen` sender-only passes: `3 × 32 × 10 = 960` calls at the
measured **53.5 s/call** ≈ **14.3 hours**.

```bash
for n in 2 3 4; do
  python3 experiments/E-001c-fluency-length-controlled/headroom_check.py \
    --probes probes/meridian-ix16/probes.json \
    --model qwen3.5:35b --draws 10 --sender-only \
    --out probes/meridian-ix16/gate-qwen$n.json
done
```

This is a prerequisite, not a study. It buys the right to compare, nothing more.

### 2. The comparison must be conditioned — free, but it changes the analysis

[Dorans & Holland (1992)](../../theory/prior-art.md) require matching on the
attribute measured before any per-item difference between readers may be called
differential functioning. The two readers differ by a fitted **2.20 logits** of
overall ability on this measure. Every per-probe comparison made so far was
unconditioned, which makes it *impact*.

The conditioned form is standard and costs no elicitation: fit reader ability and
probe difficulty jointly, then test for a reader × probe interaction as a
departure from that fit. Run on the data already on disk it gives deviance
**10.54 on 8 df, `p = 0.229`** — no interaction required. Any future claim of a
reader-specific probe has to beat that null, and must be stated as beating it.

### 3. Two readers cannot estimate a variance component — the real blocker

A rater facet needs enough levels to have a variance. Two does not. Both local
models are also already **declared subjects** in
[EXPOSURE.md](../../EXPOSURE.md), and `bge-m3` is an embedding model and cannot
answer probes, so the machine in the room holds no third reader.

What a third and fourth reader would settle, and nothing else can:

- whether `X11` and `X26` are lost by *readers in general* or by these two;
- whether the seven `gpt-oss`-only probes are reader-specific at all, once
  ability is conditioned out;
- the actual quantity of interest — what fraction of this measure's divergence
  variance sits on the reader facet rather than the probe facet.

**Ordering, stated plainly:** (2) is free and should precede any further claim;
(1) is 14 hours and is a prerequisite to comparing margins; (3) is the study, and
it cannot start on this hardware.

## What must not be done instead

**Not** more messages on the two existing readers. That sharpens the estimate of
a design whose reader facet is fixed, which Brennan's sentence says has zero
error variance over readers however much data is added to it. More briefs answer
a different question — how much per-message variance there is — and this line has
already established that it is large and unpredictable from a brief's register,
length or cell.

**Not** a third reader chosen because it is cheap. Cost asymmetry is severe —
`gpt-oss` runs at 5.8 s/call against `qwen`'s 53.5, a factor of nine — and
picking readers by price selects on exactly the axis (capability, and therefore
ability on this measure) that the study is trying to hold constant.

---

*This document is licensed CC BY 4.0.*
