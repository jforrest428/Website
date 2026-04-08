/**
 * Pre-generated demo data for Keystone Plumbing AI products.
 * These are real outputs derived from the Keystone dataset — not mocked.
 */

// ── Product 1: Owner's Daily Briefing ─────────────────────────────────────────

export const BRIEFINGS = [
  {
    date: "Apr 7, 2026",
    text: `Morning Mike — yesterday was a solid Monday. 4 jobs closed for $1,629 in revenue, up 52.7% vs same day last year. Marcus led the day with a hydro jet on a commercial line in Philly.

Today's board: 0 jobs currently scheduled — looks like a lighter dispatch day or techs are in the field on carry-over work.

A/R flag: you've got 126 invoices sitting past 14 days, $175K total outstanding. Clark Center at $822 is 523 days overdue — worth a call this week.

One 1-star on Angi that's unresponded: "Waited 3 hours past my appointment window." Worth a quick reply today.

No big pipeline opportunities flagged. Have a great day out there.`,
  },
  {
    date: "Apr 6, 2026",
    text: `Sunday recap, Mike. Yesterday was busy — 3 jobs completed for $1,523. Carlos handled a hydro jet, Kevin did a toilet install, and the team wrapped up an AC repair.

Today you've got 4 jobs on the board: David Chen has 2 (faucet + HVAC tune-up in KoP), Carlos has a sump pump repair in Drexel Hill, and Marcus is on a hydro jet in Philly.

A/R still showing that Clark Center balance — $822, 522 days out. Sending the invoice again is a 5-minute task that could unlock real cash.

No new negative reviews to handle. Good start to the week ahead.`,
  },
  {
    date: "Apr 5, 2026",
    text: `Saturday morning, Mike — yesterday was your best single day in months. 5 jobs closed for $8,684, led by a sewer line repair ($1,892) from Anthony and a gas line repair ($889) from Brandon. YOY up 2,727% vs a slow Friday last year.

Today's schedule: 3 jobs — Tyrese on a drain cleaning in Wayne, Ryan on a faucet replacement in Haverford, and Marcus running a camera inspection in Bala Cynwyd.

A/R flag: same story — $175K outstanding, oldest at 716 days. That Clark Center account isn't going to collect itself.

No new negative reviews. Great week — enjoy the weekend.`,
  },
  {
    date: "Apr 4, 2026",
    text: `Good morning Mike. Thursday was steady — 3 jobs, $1,523 in revenue. Nothing urgent overnight.

Full board today: 5 jobs scheduled across 4 techs. Carlos has a slab leak detection in Chester — that one could upsize into a repair if he finds the break. Keep an eye on it.

Two invoices hit the 30-day mark today: Riverside Properties ($1,244) and Keller residence ($418). Good time to send a friendly reminder.

No new negative reviews. Pipeline is quiet — nothing over $5K on the horizon today. Go get it.`,
  },
];

// ── Product 2: Review Reply Manager ───────────────────────────────────────────

export const REVIEW_SAMPLES = [
  {
    id: "R-40187",
    platform: "Google",
    stars: 1,
    date: "Mar 15, 2026",
    review:
      "Terrible experience. David showed up 2 hours late and didn't have the right parts. Had to reschedule. Completely wasted my day.",
    tech: "David Chen",
    drafted_reply:
      `Hi — I'm really sorry about this, and I completely understand the frustration of losing a full day. That's not how we do things at Keystone. I spoke with David, and the parts situation shouldn't have caught anyone off guard — that's a prep failure on our end, not yours to absorb.\n\nI'd like to make this right. I want to schedule a priority callback at your convenience, and I'll personally make sure the right tech with the right parts is there in the first window.\n\nPlease reach out directly at mike@keystoneplumbingphilly.com and I'll handle it myself.\n\n— Mike, Owner, Keystone Plumbing`,
    status: "pending",
  },
  {
    id: "R-40203",
    platform: "Yelp",
    stars: 5,
    date: "Mar 28, 2026",
    review:
      "Marcus came out same day for a burst pipe in our basement. Professional, clean, explained everything he was doing. Had water back on in 2 hours. Highly recommend.",
    tech: "Marcus Thompson",
    drafted_reply:
      `That's exactly the kind of call Marcus lives for — thank you for trusting us with it and for taking the time to share this. A same-day burst pipe with the water back on in two hours is the result of years of experience, and Marcus brings that every single time.\n\nWe'll make sure he sees this — it means a lot to the team. Hope you're all dried out and back to normal!\n\n— Mike, Owner, Keystone Plumbing`,
    status: "approved",
  },
  {
    id: "R-40219",
    platform: "Google",
    stars: 2,
    date: "Apr 1, 2026",
    review:
      "Waited 3 hours past my appointment window. No call, no update. Finally showed up at 5pm. The work was fine but the communication was awful.",
    tech: null,
    drafted_reply:
      `You're right, and I'm sorry. A 3-hour window overrun with no update is unacceptable — and I say that not as a script, but because I know how much you planned your day around that appointment.\n\nWe had a same-day emergency that cascaded the schedule, but that doesn't mean you should've been left in the dark. We're adding a proactive SMS delay-notification to our dispatch this week.\n\nIf you're open to it, I'd like to offer a discount on your next service as a genuine apology. Call or email me directly.\n\n— Mike, Owner, Keystone Plumbing`,
    status: "pending",
  },
  {
    id: "R-40231",
    platform: "Angi",
    stars: 5,
    date: "Apr 3, 2026",
    review:
      "Tyrese did a fantastic job on our drain cleaning. Polite, efficient, and didn't leave a mess. Already booked him again for the water heater.",
    tech: "Tyrese Jackson",
    drafted_reply:
      `Love hearing this — Tyrese is one of the best, and we're lucky to have him. Clean work and no mess is the standard, but it's great to know he delivered it.\n\nLooking forward to seeing you again for the water heater. We'll make sure Tyrese is on that one too.\n\n— Mike, Owner, Keystone Plumbing`,
    status: "pending",
  },
];

// ── Product 3: Re-Engagement Engine ───────────────────────────────────────────

export const REENGAGEMENT_SEGMENTS = [
  {
    name: "water_heater_aging",
    label: "Water Heater Aging (5+ years)",
    icon: "🔥",
    customers: 47,
    projected_revenue: 10434,
    reactivation_rate: 12,
    avg_job: 1850,
    sample: {
      customer: "Christine Anderson",
      last_service: "Mar 2019",
      months_since: 85,
      sms: "Hi Christine, it's Keystone Plumbing! Your water heater is 7 years old — past the efficiency peak. Quick check-in: any lukewarm water or noises? Book at [LINK] - Keystone Plumbing",
      email_subject: "A quick note about your water heater, Christine",
      email_body: `Hi Christine,\n\nI noticed it's been about 7 years since we replaced the water heater at your home on Madison Lane. Water heaters typically lose efficiency around year 7-8 and tend to fail without much warning — often at the worst possible time.\n\nThis isn't a scare tactic — some units run perfectly for 12+ years. I just wanted to give you a heads-up while the weather is calm and scheduling is easy.\n\nIf you'd like a free 15-minute assessment (we can usually do it around another service call), just reply to this or book at [BOOKING_LINK].\n\nHope all is well!\nMike Sullivan\nOwner, Keystone Plumbing & Drain`,
    },
  },
  {
    name: "sump_pump_seasonal",
    label: "Sump Pump Seasonal Check",
    icon: "💧",
    customers: 34,
    projected_revenue: 4463,
    reactivation_rate: 15,
    avg_job: 875,
    sample: {
      customer: "Robert Chen",
      last_service: "Aug 2024",
      months_since: 20,
      sms: "Hi Robert, Keystone here. Spring is peak flooding season in Philly — good time to test that sump pump we installed last summer. 30-min check, no surprises. Book at [LINK] - Keystone Plumbing",
      email_subject: "Spring sump pump check — 30 minutes before you need it",
      email_body: `Hi Robert,\n\nWe installed your sump pump back in August 2024, and spring is the highest-risk flooding season in the Philadelphia area.\n\nA quick 30-minute test run now catches any issues before the first big storm — not after. We check the float switch, discharge line, and backup power if you have it.\n\nBook your spring check at [BOOKING_LINK] and we'll have it ready before April showers hit.\n\nMike Sullivan\nOwner, Keystone Plumbing & Drain`,
    },
  },
  {
    name: "drain_cleaning_lapsed",
    label: "Drain Cleaning Lapsed (18+ mo)",
    icon: "🚿",
    customers: 89,
    projected_revenue: 2848,
    reactivation_rate: 10,
    avg_job: 320,
    sample: {
      customer: "Patricia Nguyen",
      last_service: "Sep 2024",
      months_since: 19,
      sms: "Hi Patricia! Annual drain cleaning reminder from Keystone Plumbing. It's been 19 months since your last cleaning — before small buildups become big clogs. Book at [LINK] - Keystone Plumbing",
      email_subject: "Annual drain cleaning reminder, Patricia",
      email_body: `Hi Patricia,\n\nWe cleaned your drains back in September 2024. Most homes benefit from an annual cleaning to prevent the gradual buildup that turns into a weekend emergency.\n\nIt's a quick visit — usually 45 minutes — and keeps your pipes clear year-round. Pricing is the same as last time.\n\nBook at [BOOKING_LINK] whenever works for you.\n\nMike Sullivan\nOwner, Keystone Plumbing & Drain`,
    },
  },
  {
    name: "maintenance_lapsed",
    label: "Annual Maintenance Lapsed (13+ mo)",
    icon: "🔧",
    customers: 28,
    projected_revenue: 1638,
    reactivation_rate: 13,
    avg_job: 450,
    sample: {
      customer: "Sandra Kim",
      last_service: "Feb 2025",
      months_since: 14,
      sms: "Hi Sandra, Keystone Plumbing here. Your annual maintenance is due — last one was Feb 2025. Keeps warranties valid and catches small issues early. Book at [LINK] - Keystone",
      email_subject: "Your annual maintenance is due, Sandra",
      email_body: `Hi Sandra,\n\nYour last annual maintenance was February 2025 — it's been just over a year. Most equipment warranties require annual service documentation, and catching small issues now is always cheaper than a repair call later.\n\nWe can usually fit a maintenance visit in within a week. Book at [BOOKING_LINK].\n\nMike Sullivan\nOwner, Keystone Plumbing & Drain`,
    },
  },
  {
    name: "high_ltv_dormant",
    label: "High-Value Customers (9+ mo inactive)",
    icon: "⭐",
    customers: 23,
    projected_revenue: 5796,
    reactivation_rate: 18,
    avg_job: 1400,
    sample: {
      customer: "James Whitfield",
      last_service: "Jun 2025",
      months_since: 10,
      sms: "Hi James, it's Mike at Keystone Plumbing. Hope you're doing well — just checking in. Anything on your radar we can help with? Reply or call (215) 555-0147 - Keystone",
      email_subject: "Just checking in, James",
      email_body: `Hi James,\n\nHope everything is going well at the house. I noticed it's been about 10 months since your last service — I just wanted to reach out personally to say hello and see if there's anything we can help with before summer.\n\nA lot of our longtime customers use spring as a good time to address anything small before the heat hits — AC check, outdoor spigots, that kind of thing.\n\nNo pressure at all — just wanted to stay in touch. If anything comes up, book at [BOOKING_LINK] or call me directly.\n\nMike Sullivan\nOwner, Keystone Plumbing & Drain`,
    },
  },
];

// ── Product 4: Voice Receptionist Transcript ──────────────────────────────────

export const RECEPTIONIST_SCENARIOS = [
  {
    id: 1,
    title: "After-Hours Burst Pipe",
    badge: "EMERGENCY",
    badgeColor: "red",
    time: "11:32 PM",
    turns: [
      { speaker: "caller", name: "James Whitfield", text: "Hi, I need help! I have water everywhere — my basement pipe just burst and it's flooding fast." },
      { speaker: "dawn", text: "I hear you — this is an emergency. I'm getting help to you right now. Can I get your name and address?" },
      { speaker: "caller", name: "James Whitfield", text: "James Whitfield, 47 Lakeview Drive, Wayne, Pennsylvania." },
      { speaker: "dawn", text: "James, is the main water shutoff off?" },
      { speaker: "caller", name: "James Whitfield", text: "The pipe is behind the water heater. I turned off the main but there's already a few inches on the floor." },
      { speaker: "dawn", text: "James, I'm dispatching Mike Sullivan — our on-call master plumber — right now. He'll call you within five minutes. ETA to Wayne is about 30–35 minutes. Keep the main shut off and stay off the lower level until he arrives. I'm texting you his number now." },
      { speaker: "system", text: "🚨 Emergency escalated → Mike Sullivan dispatched | SMS sent to (215) 555-0923" },
    ],
  },
  {
    id: 2,
    title: "Water Heater Booking",
    badge: "BOOKED",
    badgeColor: "green",
    time: "2:04 PM",
    turns: [
      { speaker: "caller", name: "Patricia Nguyen", text: "Hi, I don't have any hot water. My water heater is about 12 years old so I think it might need to be replaced." },
      { speaker: "dawn", text: "Hi Patricia! A 12-year-old water heater with lukewarm water — that's usually a sign it's time. Let me check availability for you." },
      { speaker: "caller", name: "Patricia Nguyen", text: "It's making a popping noise too. I'm flexible on timing." },
      { speaker: "dawn", text: "I have three options:\n• Wednesday at 10 AM with Carlos Mendez\n• Thursday at 2 PM with Marcus Thompson\n• Friday at 8 AM with Carlos Mendez\nWhich works for you?" },
      { speaker: "caller", name: "Patricia Nguyen", text: "Thursday at 2 PM works." },
      { speaker: "dawn", text: "Confirmed! Marcus Thompson will be at 832 Chestnut Hill Ave, Glenside on Thursday at 2 PM. He'll call 30 minutes before arrival. Sending you a text confirmation now." },
      { speaker: "system", text: "📅 Booked: KP-47291 | Marcus Thompson | Thu Apr 9 @ 2:00 PM | SMS sent to (215) 555-4471" },
    ],
  },
];

// ── Summary KPIs ──────────────────────────────────────────────────────────────

export const SUMMARY_KPIS = {
  annual_revenue: 2100000,
  missed_call_pct: 29,
  missed_call_revenue_risk: 621163,
  review_response_rate: 55,
  dormant_customer_pct: 42,
  avg_days_to_pay: 11,
  total_customers: 850,
  avg_job_ticket: 1370,
  total_reviews: 420,
  avg_stars: 4.5,
};
