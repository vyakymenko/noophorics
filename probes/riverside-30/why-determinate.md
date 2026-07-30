# Why each key is determined by the source, not by judgment

Written by the measure's author before adjudication. The requirement it
answers: if the argument is "the natural reading is", the probe is defective.

## T01

**Rules engaged:** 2.1 (Standard = 10 days), 1.2 (counting), 1.3 (no move needed)

2.1 fixes the length at 10 days because the drill is not on the Register. 1.2 states the period begins the day after D and ends on D+n and that D is never counted, so 5 March + 10 = 15 March; the '14 March' option is the only alternative an inclusive count could produce and 1.2 forecloses it in terms. 1.3 moves a due date only if it is closed, and 1.1 lists March Sundays as 2, 9, 16, 23, 30, so 15 March is open and unmoved.

## T02

**Rules engaged:** 2.1, 1.2, 1.3 (forward move off a closed day), 1.1

6 March + 10 = 16 March under 1.2. 1.1 lists 16 March as a Sunday, hence closed. 1.3 directs that a computed due date falling on a closed day moves forward to the next open day, and states the move applies at most once; 17 March is open under 1.1, so the move terminates there. The spec supplies both the closure list and the move direction, so no calendar knowledge or discretion is required.

## T03

**Rules engaged:** 2.1 (Restricted = 5 days), 1.1 (holiday), 1.3

2.1 names 'tile saw' on the Restricted Register, fixing a 5-day loan. 10 April + 5 = 15 April under 1.2. 1.1 declares 15 April the single holiday and therefore closed, so 1.3 moves the date to the next open day. 1.1 lists April Sundays as 6, 13, 20, 27, so 16 April is open and 1.3's at-most-once move ends there. Every input (Register membership, closure, move rule) is stated.

## T04

**Rules engaged:** 2.2 (both caps), 2.1 (classification)

2.2 sets two independent caps and says a checkout breaching either is refused. Greg already has 3 open loans, so a fourth breaches the 3-loan cap. The second option is excluded by 2.1: the hand plane is not on the Register, so it is Standard, and Greg's Restricted count stays at 1, which 2.2 permits. Only one cap is breached and the spec names it, so the reason as well as the outcome is fixed.

## T05

**Rules engaged:** 2.1 (Register), 2.3 (new-member bar), 1.2 (counting), 2.2

2.1 puts 'pressure washer' on the Register. 2.3 bars a Restricted loan where registration is fewer than 30 days before the checkout date, measured per 1.2: 20 March to 16 April is 27 days. The verdict is insensitive to any off-by-one dispute, since 27 or 28 are both fewer than 30. The Restricted-cap option is excluded because 2.2 permits 1 Restricted item and Hana has none out, so 2.3 is the only operative bar and 2.3's final sentence blocks any curing rule.

## T06

**Rules engaged:** 1.5 (overdue counting), 1.4 (closed-day return credit), 6.2 (grace), 6.1

1.5 makes 15 March overdue day 1 and 16 March overdue day 2. 16 March is a Sunday under 1.1, but 1.4 states the return box is available on closed days and that a closed-day deposit is credited to that date, which forecloses the reading that the return counts on the next open day (which would be overdue day 3 and trigger a charge). 6.2 then states in terms that an item returned on overdue day 1 or 2 carries no late fee.

## T07

**Rules engaged:** 1.5, 6.2 (grace forfeited), 6.1 ($1/day Standard)

1.5 makes 18 March overdue day 4 (15, 16, 17, 18 March). 6.2's second sentence covers returns on overdue day 3 or later and says the charge runs for every overdue day through the return date, 'days 1 and 2 included' — which excludes the $2 reading that charges only days 3 and 4. 6.1 sets $1 per overdue day for a Standard item (2.1: not on the Register), giving 4 x $1.

## T08

**Rules engaged:** 1.5, 6.4 (forfeit), 6.1, 6.2

1.5 makes 2 April overdue day 1, so overdue day 30 is 1 May and the item was still out at the end of that day. 6.4 declares it forfeit and states that accrued late fees 'are then cancelled and replaced by' a flat $75, which excludes $107 (fees plus charge) and $32 (32 days of accrual). 6.4 also states no further fee accrues and that returning the item afterwards does not remove the $75, so the 3 May return changes nothing.

## T09

**Rules engaged:** 1.5 (overdue days, including closed days), 6.4 (forfeit threshold)

1.5 makes 23 April overdue day 1 and states overdue days run consecutively and include closed days, so no closure-skipping reading is available; 21 May is overdue day 29. 6.4 fixes forfeit at the end of overdue day 30, which is 22 May, a date after the one asked about. Overdue status is established by 1.5 (not returned by the end of the effective due date), so the first option fails and the second is one day premature.

## T10

**Rules engaged:** 1.3 (move) combined with 3.2 (window measured on the effective due date)

This is the interaction case. 6 March + 10 = 16 March, a Sunday under 1.1, so 1.3 makes the effective due date 17 March. 1.3's final sentence says all later computations, naming renewal windows expressly, use the effective date 'never the unmoved date'. The window under 3.2 is therefore 15, 16, 17 March, and 14 March falls outside it, so 3.2 denies. Measured against the unmoved 16 March the window would be 14-16 March and the request would be admitted, so the two readings genuinely diverge — and 1.3 resolves the divergence by its own terms rather than by inference.

## T11

**Rules engaged:** 1.3, 3.2 (window), 3.1 (term counted from the due date, then moved)

10 March + 10 = 20 March, open under 1.1, so the effective due date is 20 March and the 3.2 window is 18-20 March, admitting the 19 March request. No other denial ground in 3.3-3.6 is triggered on the stated facts. 3.1 counts the new period from the current effective due date, not the request date, giving 30 March, and then directs that the result be 'moved if necessary under 1.3'. 1.1 lists 30 March as a Sunday, so the move is mandatory and lands on 31 March, which 1.1 leaves open.

## T12

**Rules engaged:** 6.3 (suspension threshold), 4.2 (void hold, no revival), 4.4

6.3 makes Member 96 suspended on 4 April because $22 is '$20 or more'. 4.2 states that a hold placed while suspended is void, 'never enters the queue', and — the clause that settles the case — 'does not become valid if the suspension later ends', so the 6 April payment is expressly irrelevant. With no valid hold standing, 4.4 sends the item to the open shelf. The first option is the correctly computed collection period for a valid hold (4.3), so the case turns solely on validity, which 4.2 decides.

## T13

**Rules engaged:** 7.2 (deemed same-date order) combined with 3.5 (holds bar renewal)

The 3.2 window is 18-20 May, so the request is admissible and everything turns on whether a hold stood at its moment. The facts state no times, which is exactly 7.2's trigger ('the facts do not establish their order'), and 7.2's deemed sequence puts hold placements before renewal requests. Member 455's hold is valid under 4.2 (balance $0, so not suspended under 6.3), so at the deemed moment of the request a valid hold stands and 3.5 denies. Member 120 is not in a Build Project, so 5.2 is unavailable to cure 3.5.

## T14

**Rules engaged:** 7.2 (stated order governs), 3.5 ('at that moment'), 7.3, 3.1

7.2's final sentence gives the stated order priority over the deemed order, so the request precedes the hold. 3.5 bars a renewal only where a hold stands 'at that moment', and 7.3 states each request is judged on the facts at its own moment, which forecloses treating the later hold as retroactively defeating the grant. The term follows 3.1: 20 May + 10 = 30 May, which 1.1 leaves open (May Sundays are 4, 11, 18, 25), so no 1.3 move applies and 31 May is excluded.

## T15

**Rules engaged:** 7.2 (deemed order) combined with 6.3 (suspension ends on falling below $20), 6.5, 3.2, 3.1

No times are recorded, so 7.2 applies and places payments first in the deemed sequence. 6.5 states payments reduce the balance on the date made, giving $18, and 6.3 states suspension ceases 'the moment it falls below $20', so Priya is not suspended when the request is judged and 6.3's bar on renewing does not bite. 3.2's window includes the effective due date itself, so 8 April is admissible; 3.3-3.6 are all satisfied on the stated facts. 3.1 gives 8 April + 10 = 18 April, open under 1.1, so no 1.3 move.

## T16

**Rules engaged:** 4.3 (4-day collection period and its closed-day extension), 1.2, 1.1, 1.6

4.3 sets a 4-day period from the shelving date counted under 1.2, so the days are 1-4 May and the last day is 4 May. 1.1 lists 4 May as a Sunday, and 4.3 states that if the last day is closed the period 'runs instead to the next open day', which is 5 May. The extension clause is what distinguishes the options, and it is explicit rather than inferred. 1.6 permits collection on 5 May because 1.1 makes it an open day.

## T17

**Rules engaged:** 4.1 (queue by date, not by member number), 4.3 (lapse, re-shelving the following day, fresh period), 1.2, 1.1

4.1 orders valid holds by placement date and confines the member-number rule to holds placed on the same date, so Member 214 (5 March) precedes Member 87 (7 March) and the lower-number tie-break never engages. Member 214's period runs 13-16 March; 16 March is a Sunday under 1.1, so 4.3 extends it to 17 March, and the hold lapses at the end of that day. 4.3 then re-shelves 'the following day', 18 March, with a fresh 4-day period counted from that day: 19-22 March. 1.1 leaves 22 March open (23 March is a Sunday), so no further extension applies.

## T18

**Rules engaged:** 6.3 (suspension at $20 or more) combined with 4.2 (void) and 4.1 (same-date tie-break)

This is the second interaction case. 4.1's same-date tie-break ranks by member number, lower first, which alone would give the item to Member 96. But 4.1 orders 'valid holds', and 6.3 makes Member 96 suspended on 4 April at $22, so 4.2 makes his hold void and states it 'never enters the queue' — it is therefore never a candidate for the tie-break. Member 512's hold is valid, so 4.3 shelves the item for him and 4.4 does not apply. Neither rule alone produces this outcome.

## T19

**Rules engaged:** 6.3 (bar on collecting; periods keep running) combined with 4.3 (lapse)

6.3 makes her suspended at $26 and bars a suspended member from collecting from the hold shelf. The rule then states expressly that 'Collection periods keep running during suspension', which forecloses the tolling reading that the bar pauses the clock. 4.3's period is 6-9 May; 9 May is open under 1.1, so no extension applies and the hold lapses at the end of 9 May, before the 10 May payment. The third option is excluded by the plain 4-day count in 4.3 read with 1.2.

## T20

**Rules engaged:** 7.2 (deemed order puts returns before checkouts) combined with 2.2 (both caps), 2.3

No times are recorded, so 7.2 governs and its deemed sequence places returns before checkouts. At the moment of the checkout Quinn therefore has 2 open loans and 0 Restricted items, so neither limit in 2.2 is breached: the chainsaw is his 3rd loan and 1st Restricted item, both at the caps rather than beyond them ('at most 3' and 'at most 1'). 2.3 is inapplicable because he registered three years ago. Under the reverse order both options 2 and 3 would be live, so 7.2 is doing the work and it does so explicitly.

## T21

**Rules engaged:** 2.1, 1.2, 1.3, 3.2 (window edge, one day out)

14 April + 10 = 24 April, which 1.1 leaves open (April Sundays 6, 13, 20, 27; holiday 15), so the effective due date is 24 April with no 1.3 move. 3.2 defines the window as exactly three dates — the effective due date and the two immediately before it, so 22, 23 and 24 April. 21 April is one day outside, and 3.2 says a request outside the window is denied. No Override is available because Rafi is not enrolled in a Build Project (5.1).

## T22

**Rules engaged:** 1.6 (online requests on any date), 3.2 (window may include closed days), 3.1

7 March + 10 = 17 March, open under 1.1, so the effective due date is 17 March and the 3.2 window is 15, 16, 17 March. 3.2 defines the window by dates, not by open days, and 1.6 states in terms that renewal requests are made online 'on any date, open or closed', which forecloses the first option; 1.6 restricts only checkouts and collections to open days. 3.1 counts 10 days from 17 March, giving 27 March, which 1.1 leaves open, so no 1.3 move and 26 March is excluded.

## T23

**Rules engaged:** 2.1 (Register), 3.3 (Restricted renewal limit), 5.1 (no Override without enrolment)

2.1 puts 'scaffold tower' on the Register, so 3.3's Restricted limit of one renewal applies and this request is the second. 3.3 states a request beyond the limit is denied. The request is inside the 3.2 window (14-16 May) and nothing in 3.4-3.6 bites, so 3.3 is the sole and sufficient ground. 5.2 could otherwise cure a 3.3 denial, but 5.1 confines the Override to members enrolled in a registered Build Project and Tomas is not, so the Override is unavailable. Option 2 is the correctly computed 5-day term and option 3 the 7-day Override term, both unreachable.

## T24

**Rules engaged:** 3.2 (window), 5.1-5.2 (Override cures 3.2), 7.1(d) over (e), 5.4 (7-day term from the due date)

The 3.2 window is 18-20 March, so 16 March is outside and 3.2 would deny. 5.2 states a valid invocation grants a renewal that Rule 3.2 'would otherwise deny', and 7.1 ranks the Override at (d), above all other renewal rules at (e), so the conflict is resolved in the text rather than by inference. The invocation is valid: Uma is enrolled (5.1), it is the first on this loan (5.1), she is not suspended at $0 (6.3, 5.3), she has no other item overdue (3.4) and this loan is not overdue on 16 March (3.6). 5.4 fixes the term at 7 days 'for every item class' counted from the current effective due date, giving 20 + 7 = 27 March, open under 1.1; option 2 is the error of counting 7 days from the request date.

## T25

**Rules engaged:** 3.4 (other item overdue), 5.3 and 7.1(c) (Override does not cure 3.4)

The bench vice is overdue under 1.5 (not returned by the end of 19 April), so at the moment of the request Vik has another item overdue and 3.4 denies. 5.3 states in terms that the Override 'does not cure a denial under 3.4', and 7.1 independently ranks 3.4 at (c), above the Override at (d). Two separate clauses therefore reach the same result. Every other ground is clear: 25 April is the effective due date so the 3.2 window is satisfied, no hold stands, and the loan itself is not overdue. Option 2 is the 7-day Override term and option 3 the 10-day term, both blocked.

## T26

**Rules engaged:** 1.5, 3.6 (loan itself overdue), 5.3 and 7.1(c) (Override does not cure 3.6)

1.5 makes 5 May overdue day 3 on this loan, so 3.6 denies. 5.3 states the Override does not cure a denial under 3.6, and 7.1 ranks 3.6 at (c) above the Override at (d), so the Override's reach is settled by the text. 3.2 would also deny (the window closed on 2 May), but that ground is one the Override could cure under 5.2, which is why 3.6 is the operative rule; both routes converge on DENIED, so the verdict does not depend on which is applied first.

## T27

**Rules engaged:** 3.5 (hold bars renewal), 5.2 and 7.1(d) (Override prevails over 3.5), 5.4

Member 620's hold is valid (balance $0, so not suspended under 6.3, so 4.2 does not void it), and 3.5 would therefore deny. 5.2 names Rule 3.5 among those a valid invocation overcomes, and 7.1 places the Override at (d) above every other hold and renewal rule at (e), so the third party's hold does not defeat it. The invocation is valid on every condition in 5.1 and 5.3: enrolled, first on this loan, not suspended, no other item overdue, this loan not overdue on 11 May (due 12 May). 5.4 gives 12 + 7 = 19 May, open under 1.1; option 3 is the 10-day term.

## T28

**Rules engaged:** 2.1 (Register), 3.3 (Restricted limit), 5.2 (Override cures 3.3), 5.4 (7 days for every class)

2.1 puts 'concrete mixer' on the Register, so 3.3 caps renewals at one and would deny this second request. 5.2 names Rule 3.3 among those a valid invocation overcomes, and 7.1(d) ranks the Override above it. The invocation satisfies 5.1 and 5.3 on the stated facts. 5.4 then fixes the term at 7 days 'for every item class', which excludes applying the 5-day Restricted period: 20 + 7 = 27 May, open under 1.1. Option 2 is exactly what the 5-day route yields after a 1.3 move off Sunday 25 May, and 5.4's 'every item class' forecloses it.

## T29

**Rules engaged:** 6.3 (threshold is '$20 or more'), 5.3 and 7.1(b) (suspension blocks the Override), 3.5

6.3 sets the suspension threshold at '$20 or more', so exactly $20 makes Zeb suspended; the boundary is stated rather than left to inference, and no payment that day means 7.2's ordering is irrelevant. 6.3 bars a suspended member from renewing at all, and 5.3 states the Override 'cannot be invoked by a suspended member', with 7.1 ranking 6.3 at (b) above the Override at (d). With no valid invocation available, Member 700's hold independently denies under 3.5. Three routes converge on DENIED.

## T30

**Rules engaged:** 5.1 (one invocation per loan, successful or not), 5.2 ('valid invocation'), 3.5 (hold), 3.3

5.1 states a loan 'carries at most one invocation, successful or not', and this loan already carried one on 10 April, so the second invocation is not available. 5.2 confers its curing effect only on a 'valid invocation', so 3.5 stands unrelieved: Member 480's hold is valid (balance $0, so 4.2 does not void it) and 3.5 denies. Nothing else would have denied — the request is inside the 3.2 window (15-17 April, and 1.6 permits requests on closed days such as 15 April), and 3.3 permits a Standard loan two renewals, with 5.4 counting the first against that limit, so this second renewal is within the cap. The verdict therefore rests squarely on 5.1's exhaustion clause. Option 2 is the Override term and option 3 the 10-day term after a 1.3 move off Sunday 27 April.
