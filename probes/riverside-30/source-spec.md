# RIVERSIDE-30 — source specification

Authored 2026-07-30 by an agent blind to the hypotheses this measure would
serve. Every key was adjudicated by three independent readers working from
this text alone; see `ADJUDICATION.md`.

---

RIVERSIDE TOOL LIBRARY — LOAN, RENEWAL, HOLD AND PENALTY POLICY

1. CALENDAR AND COUNTING

1.1 All dates fall in March, April or May of one year; those months have 31, 30 and 31 days. The library is closed on Sundays and on one holiday, 15 April. Sundays fall on 2, 9, 16, 23 and 30 March; 6, 13, 20 and 27 April; 4, 11, 18 and 25 May. Every other date is an open day. No two closed dates are consecutive.

1.2 Periods in days are counted in calendar days, including closed days. A period of n days from date D begins on D+1 and ends on D+n; D is never counted. "Fewer than n days before date X" is measured the same way.

1.3 A computed due date is the checkout date plus the loan length (1.2). If it falls on a closed day it moves forward to the next open day. The result is the EFFECTIVE DUE DATE; by 1.1 the move applies at most once. All later computations (renewal windows, renewal terms, overdue days, fees) use the effective due date, never the unmoved date.

1.4 An item is returned on the date it is handed to staff or dropped in the return box, which is available on closed days; a closed-day deposit is credited to that date.

1.5 An item is OVERDUE if not returned by the end of its effective due date. Overdue day 1 is the day after that date; overdue days run consecutively and include closed days.

1.6 Renewal requests, hold placements and payments are made online, on any date, open or closed. Checkouts and collections are made in person and only on open days.

2. LOANS

2.1 Standard items have a 10-day loan; Restricted items have a 5-day loan. An item is Restricted if and only if it is on the Restricted Register: chainsaw, tile saw, pressure washer, concrete mixer, scaffold tower. All other items are Standard.

2.2 A member may have at most 3 loans open at once, at most 1 of them Restricted. A checkout breaching either limit is refused.

2.3 A member whose registration date is fewer than 30 days before the checkout date may not borrow a Restricted item. No other rule lifts this bar.

3. RENEWALS

3.1 A renewal extends the loan by one further period of the item's class (10 days Standard, 5 Restricted), counted under 1.2 from the loan's current effective due date, never from the request date, then moved if necessary under 1.3.

3.2 The RENEWAL WINDOW is the effective due date and the two dates immediately before it. A request outside the window is denied.

3.3 A Standard loan may be renewed at most twice, a Restricted loan at most once. A request beyond that limit is denied.

3.4 A request is denied if, at the moment it is made, the member has any OTHER item overdue.

3.5 A request is denied if one or more valid holds stand on the item at that moment.

3.6 A request is denied if the loan being renewed is itself overdue at that moment.

4. HOLDS

4.1 A hold may be placed on an item on loan. Valid holds queue by placement date; two placed on the same date rank by member number, lower first.

4.2 A hold placed by a member suspended (6.3) at that moment is VOID: it never enters the queue, and does not become valid if the suspension later ends.

4.3 An item carrying a valid hold is shelved on its return date for the first member in the queue. That member's COLLECTION PERIOD is 4 days from the shelving date (1.2); if its last day is closed it runs instead to the next open day. If the item is not collected by the end of that period the hold lapses, and the item is shelved the following day for the next member in the queue, with a fresh 4-day period counted from that day.

4.4 If no valid hold stands on it, the item goes to the open shelf, available to anyone.

4.5 A hold-shelf item is not a loan; the loan begins on collection.

5. PROJECT OVERRIDE

5.1 A member enrolled in a registered Build Project may invoke the Project Override. A loan carries at most one invocation, successful or not.

5.2 A valid invocation grants a renewal that Rule 3.2, 3.3 or 3.5 would otherwise deny.

5.3 The Override does not cure a denial under 3.4 or 3.6, cannot be invoked by a suspended member (6.3), and does not lift 2.2 or 2.3.

5.4 A renewal granted by Override runs 7 days for every item class, counted under 1.2 from the loan's current effective due date, moved if necessary under 1.3. It counts against the limits in 3.3.

6. FEES, SUSPENSION AND FORFEIT

6.1 Late fees accrue at $1 per overdue day for a Standard item, $4 for a Restricted item.

6.2 GRACE. An item returned on overdue day 1 or 2 carries no late fee. One returned on overdue day 3 or later is charged for every overdue day through the return date, days 1 and 2 included.

6.3 A member is SUSPENDED whenever their unpaid balance is $20 or more, and ceases to be the moment it falls below $20. A suspended member may not check out, renew, place a hold (4.2), collect from the hold shelf, or invoke the Override. Collection periods keep running during suspension.

6.4 An item still out at the end of overdue day 30 is FORFEIT. Late fees accrued on it are then cancelled and replaced by a flat $75 replacement charge; no further fee accrues, and returning the item afterwards does not remove the $75.

6.5 Late fees post to the balance on the return date, or for a forfeit on the forfeit date. Payments reduce it on the date made.

7. PRECEDENCE AND SAME-DATE ORDER

7.1 Where rules conflict, this order governs, highest first: (a) 2.3; (b) 6.3; (c) 3.4 and 3.6; (d) the Project Override, 5.2; (e) every other renewal and hold rule. A valid Override therefore beats 3.2, 3.3 and 3.5, but yields to (a), (b) and (c).

7.2 Where several events fall on the same date and the facts do not establish their order, they are deemed to occur thus: payments, returns, collections, hold placements, checkouts, renewal requests. Where the facts do establish an order, that order governs.

7.3 A denial is final for the request it answers. A member may request again later; each request is judged on the facts at its own moment.
