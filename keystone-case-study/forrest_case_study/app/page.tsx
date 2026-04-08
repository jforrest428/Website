import { Download, ArrowRight, Phone, TrendingUp, Clock, Star, Users } from "lucide-react";
import Link from "next/link";

// ── Data ──────────────────────────────────────────────────────────────────────

const PAIN_POINTS = [
  {
    stat: "29%",
    label: "of calls go unanswered",
    icon: Phone,
    dollar: "$48K–$72K lost revenue per year",
    color: "red",
  },
  {
    stat: "55%",
    label: "negative review response rate",
    icon: Star,
    dollar: "Local SEO suppressed — costs ~$30K+ in organic traffic",
    color: "orange",
  },
  {
    stat: "42%",
    label: "of customers are dormant",
    icon: Users,
    dollar: "$30K–$60K in recoverable annual revenue sitting untouched",
    color: "orange",
  },
  {
    stat: "11 days",
    label: "average time to get paid",
    icon: Clock,
    dollar: "$175K in outstanding A/R — 6% still unpaid at 30+ days",
    color: "red",
  },
];

const PRODUCTS = [
  {
    number: "01",
    emoji: "📞",
    title: "24/7 AI Voice Receptionist",
    tagline: "Stop losing $50,000 a year to missed calls.",
    how: `A Claude-powered agent answers every inbound call — first ring, 24/7, whether the office line is busy or it's 2am on a Sunday. It identifies the issue, triages emergencies immediately, and books appointments directly from live technician availability. After booking, it texts a confirmation with the tech name, appointment time, and a direct callback number.

Emergency calls (burst pipe, sewage backup, no heat, gas smell) are escalated instantly to the on-call tech with a one-tap callback — not routed to voicemail.

The agent uses real tool calls: it reads the schedule to surface available slots, writes the booking to the job log, and sends the SMS — all before the caller hangs up.`,
    roi: [
      { label: "Answer rate", before: "71%", after: "100%" },
      { label: "After-hours answered", before: "31%", after: "100%" },
      { label: "Recovered revenue (est.)", before: "—", after: "$40K–$65K/yr" },
      { label: "Office staff hours freed", before: "0", after: "8–12 hrs/wk" },
    ],
    demo_label: "Run the call demo",
    demo_note: "Runs a real Claude agent with live tool calls: get_available_slots, book_appointment, send_sms_confirmation, escalate_to_oncall.",
  },
  {
    number: "02",
    emoji: "⭐",
    title: "Review Reply & Reputation Manager",
    tagline: "Every review answered. Every customer recovered.",
    how: `Claude monitors all 420 reviews across Google, Yelp, Angi, BBB, and Facebook. Within 30 minutes of a new review, it drafts a personalized reply that references the specific job, names the tech if mentioned, addresses the complaint directly (never defensively), and offers a concrete make-right on 1–2 star reviews.

Replies queue for one-click owner approval — the owner never has to write from scratch.

The pattern analyzer groups negative reviews by technician and surfaces any tech with 2+ mentions. In Keystone's dataset, David Chen has 3 negative mentions in the last 90 days — the system flags this proactively for coaching.`,
    roi: [
      { label: "Response rate", before: "55%", after: "100%" },
      { label: "Response time (avg)", before: "3–7 days", after: "< 1 hour" },
      { label: "Organic call lift (est.)", before: "—", after: "8–15%" },
      { label: "Owner time per week", before: "2–3 hrs", after: "10 min" },
    ],
    demo_label: "Try the approval UI",
    demo_note: "The Streamlit UI shows the full review queue with AI-drafted replies and one-click approval.",
  },
  {
    number: "03",
    emoji: "💬",
    title: "Customer Re-Engagement Engine",
    tagline: "There's $25,000 sitting in your customer list. Let's go get it.",
    how: `Every week, Claude segments the 850-customer list into five re-engagement buckets based on service type and recency: water heater installs over 5 years old, sump pump installs before last winter, drain cleaning customers over 18 months lapsed, annual maintenance overdue, and high-LTV customers with no job in 9+ months.

For each customer in each segment, Claude writes a personalized SMS (≤160 chars) and email that references their specific service date and job type — friendly, specific, not salesy.

The dashboard shows segment sizes, projected recovered revenue, and sample messages for any segment. A 12% average reactivation rate across 221 dormant customers projects $25,180 in recoverable revenue.`,
    roi: [
      { label: "Dormant customers identified", before: "0 (manual)", after: "221 segmented" },
      { label: "Reactivation rate (est.)", before: "—", after: "8–15%" },
      { label: "Projected annual recovery", before: "—", after: "$25K–$45K" },
      { label: "Time to generate 221 messages", before: "Never done", after: "< 10 min" },
    ],
    demo_label: "View the dashboard",
    demo_note: "The Streamlit dashboard shows all 5 segments with projected revenue and sample AI-written outreach.",
  },
  {
    number: "04",
    emoji: "📱",
    title: "Owner's Daily Briefing",
    tagline: "Run your shop from a text message.",
    how: `Every morning at 6am, Claude pulls from the jobs, invoices, calls, and reviews datasets and writes a plain-English SMS in 180 words or fewer. It covers yesterday's revenue vs the same day last year, today's full technician schedule, any invoices over 14 days overdue, any negative reviews that need attention, and any high-value jobs in the pipeline.

No dashboard. No login. The owner opens their phone and knows what matters in 60 seconds.

The briefing viewer shows the last 30 days of messages in an iMessage-style interface — a compelling demo for any service-business owner who spends 45 minutes every morning stitching together information from five different systems.`,
    roi: [
      { label: "Morning ops review time", before: "45 min", after: "< 5 min" },
      { label: "A/R issues caught early", before: "Reactive", after: "Daily flag" },
      { label: "Negative reviews caught", before: "When owner remembers", after: "24-hr window" },
      { label: "Revenue impact (indirect)", before: "—", after: "2–5% of top line" },
    ],
    demo_label: "See today's briefing",
    demo_note: "Open the iMessage viewer to see real AI-generated briefings from Keystone's actual dataset.",
  },
];

// ── Components ────────────────────────────────────────────────────────────────

function Header() {
  return (
    <header className="bg-navy-950 text-white py-5 px-6 sticky top-0 z-50 border-b border-navy-800">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <Link href="https://forrestanalyticsgroup.com" className="font-bold text-sm tracking-tight hover:text-orange-400 transition-colors">
          Forrest Analytics Group
        </Link>
        <nav className="hidden md:flex items-center gap-6 text-sm text-navy-300">
          <a href="#pain-points" className="hover:text-white transition-colors">The Problem</a>
          <a href="#products" className="hover:text-white transition-colors">The Solutions</a>
          <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
          <a href="#cta" className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg font-semibold transition-colors">
            Book Audit
          </a>
        </nav>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="bg-navy-900 text-white py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-1.5 text-orange-400 text-sm font-medium mb-6">
          Case Study · Service Business AI
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold leading-tight mb-6 text-balance">
          How we&apos;d rebuild a $2.1M plumbing company with AI — a Keystone Plumbing case study.
        </h1>
        <p className="text-xl text-navy-200 mb-8 leading-relaxed max-w-3xl">
          Four working AI products, built on 850 real customers, 2,400 jobs, and 420 reviews.
          Voice receptionist, reputation manager, re-engagement engine, and daily briefing — each
          grounded in real operational data and real ROI math.
        </p>
        <div className="flex flex-wrap gap-4">
          <a href="#pain-points" className="bg-orange-500 hover:bg-orange-600 text-white font-semibold px-6 py-3 rounded-xl transition-colors flex items-center gap-2">
            See the case study <ArrowRight className="w-4 h-4" />
          </a>
          <a
            href="/data/Keystone_Plumbing_Sample_Dataset.xlsx"
            download
            className="bg-navy-800 hover:bg-navy-700 text-white font-semibold px-6 py-3 rounded-xl transition-colors flex items-center gap-2 border border-navy-700"
          >
            <Download className="w-4 h-4" /> Download the dataset
          </a>
        </div>
      </div>
    </section>
  );
}

function CompanyProfile() {
  return (
    <section className="py-14 px-6 border-b border-navy-100">
      <div className="max-w-4xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
          <div className="md:col-span-2">
            <h2 className="text-2xl font-bold text-navy-900 mb-4">The Company</h2>
            <p className="text-navy-600 leading-relaxed mb-4">
              <strong className="text-navy-800">Keystone Plumbing &amp; Drain</strong> is a fictional
              Philadelphia-area plumbing and light-HVAC company built as a representative sample of
              the service businesses Forrest Analytics Group targets for AI implementation.
            </p>
            <p className="text-navy-600 leading-relaxed">
              The accompanying dataset contains two years of realistic operational data:
              850 customers, 2,400 jobs, 2,266 invoices, 3,200 inbound calls, and 420 reviews.
              Every AI product in this case study is built on top of that data — nothing is mocked or
              simulated at the data layer.
            </p>
          </div>
          <div className="bg-navy-50 rounded-2xl p-5 text-sm">
            <div className="font-bold text-navy-900 mb-3">Company Profile</div>
            {[
              ["Location", "Philadelphia metro — Main Line & Western Suburbs"],
              ["Founded", "2014"],
              ["Headcount", "8 technicians, 5 trucks, 2 office staff"],
              ["Annual Revenue", "~$2.1M"],
              ["Customer Mix", "75% residential · 15% commercial · 10% property mgmt"],
              ["Services", "Plumbing, drain, water heaters, sewer, sump pumps, light HVAC"],
            ].map(([k, v]) => (
              <div key={k} className="flex flex-col gap-0.5 mb-2.5">
                <span className="text-xs uppercase tracking-wide text-navy-400 font-semibold">{k}</span>
                <span className="text-navy-700">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function PainPoints() {
  return (
    <section id="pain-points" className="py-16 px-6 bg-navy-950 text-white">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-3">Four pain points. Four dollar amounts.</h2>
        <p className="text-navy-300 mb-10 text-lg">
          We pulled these from Keystone&apos;s real dataset. Every service business in the country
          has a version of each one.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PAIN_POINTS.map((p) => {
            const Icon = p.icon;
            return (
              <div key={p.stat} className="bg-navy-800 border border-navy-700 rounded-2xl p-6">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    p.color === "red" ? "bg-red-500/10" : "bg-orange-500/10"
                  }`}>
                    <Icon className={`w-6 h-6 ${p.color === "red" ? "text-red-400" : "text-orange-400"}`} />
                  </div>
                  <div>
                    <div className="text-3xl font-extrabold text-white">{p.stat}</div>
                    <div className="text-navy-300 text-sm mb-2">{p.label}</div>
                    <div className={`text-sm font-medium ${p.color === "red" ? "text-red-400" : "text-orange-400"}`}>
                      {p.dollar}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function ProductSection({ product, index }: { product: typeof PRODUCTS[0]; index: number }) {
  const isEven = index % 2 === 0;
  return (
    <section id={`product-${product.number}`} className={`py-20 px-6 ${isEven ? "bg-white" : "bg-navy-50"}`}>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <span className="text-4xl">{product.emoji}</span>
          <div>
            <div className="text-xs uppercase tracking-widest text-navy-400 font-semibold mb-1">
              Product {product.number}
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-navy-900">{product.title}</h2>
          </div>
        </div>
        <p className="text-xl font-semibold text-orange-600 mb-6">{product.tagline}</p>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
          {/* How it works */}
          <div className="md:col-span-3">
            <h3 className="text-sm uppercase tracking-widest font-semibold text-navy-400 mb-3">How It Works</h3>
            {product.how.split("\n\n").map((para, i) => (
              <p key={i} className="text-navy-600 leading-relaxed mb-4">{para}</p>
            ))}

            {/* Demo embed placeholder */}
            <div className="mt-6 bg-navy-900 rounded-2xl p-5 border border-navy-700">
              <div className="text-white font-semibold mb-1">▶ {product.demo_label}</div>
              <p className="text-navy-400 text-sm mb-3">{product.demo_note}</p>
              <div className="text-xs text-navy-500 bg-navy-800 rounded-lg p-3 font-mono">
                # Run locally:<br />
                {product.number === "01" && "python products/04_voice_receptionist/scripted_demo.py"}
                {product.number === "02" && "streamlit run products/02_review_reply/app.py"}
                {product.number === "03" && "streamlit run products/03_reengagement/app.py"}
                {product.number === "04" && "streamlit run products/01_daily_briefing/app.py"}
              </div>
            </div>
          </div>

          {/* ROI table */}
          <div className="md:col-span-2">
            <h3 className="text-sm uppercase tracking-widest font-semibold text-navy-400 mb-3">ROI Impact</h3>
            <div className="bg-white border border-navy-200 rounded-2xl overflow-hidden shadow-sm">
              <div className="grid grid-cols-3 bg-navy-800 text-white text-xs font-semibold px-4 py-2.5">
                <span>Metric</span>
                <span className="text-center">Before</span>
                <span className="text-center text-orange-400">After AI</span>
              </div>
              {product.roi.map((row) => (
                <div key={row.label} className="grid grid-cols-3 text-xs px-4 py-3 border-b border-navy-100 last:border-0">
                  <span className="text-navy-600 font-medium">{row.label}</span>
                  <span className="text-center text-navy-400">{row.before}</span>
                  <span className="text-center text-orange-600 font-semibold">{row.after}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Architecture() {
  return (
    <section id="architecture" className="py-20 px-6 bg-navy-950 text-white">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-3">How it all fits together</h2>
        <p className="text-navy-300 mb-10">
          One dataset. One API. Four products that can run independently or as a unified operating system.
        </p>

        {/* Architecture diagram */}
        <div className="bg-navy-800 rounded-2xl p-6 border border-navy-700 font-mono text-sm">
          <pre className="text-navy-200 overflow-x-auto whitespace-pre">{`
  ┌─────────────────────────────────────────────┐
  │   Keystone_Plumbing_Sample_Dataset.xlsx      │
  │   850 customers · 2,400 jobs · 420 reviews   │
  └──────────────────┬──────────────────────────┘
                     │
              shared/data_loader.py
                     │
          ┌──────────┼──────────────┐
          ▼          ▼              ▼
   jobs()     reviews()      customers()
   invoices() calls()        technicians()
          │          │              │
          └──────────┼──────────────┘
                     │
           shared/claude_client.py
           (retry + cache + logging)
                     │
              claude-sonnet-4-6
                     │
     ┌───────────────┼────────────────────┐
     ▼               ▼                    ▼
  Daily          Review              Re-Engagement
  Briefing       Manager             Engine
  6am SMS        Reply queue         5 segments
  (180 words)    + patterns          SMS + email
                 (1-click approve)   + revenue proj
     │               │                    │
     └───────────────┼────────────────────┘
                     │
           Voice Receptionist
           Tool use: get_slots()
           book_appointment()
           escalate_to_oncall()
           send_sms_confirmation()
                     │
             call_log.jsonl
`}</pre>
        </div>

        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {[
            { label: "Backend", value: "Python 3.11 + FastAPI" },
            { label: "AI Model", value: "Claude claude-sonnet-4-6" },
            { label: "Frontend", value: "Next.js 14 + Tailwind" },
            { label: "UI", value: "Streamlit (approval flows)" },
          ].map(({ label, value }) => (
            <div key={label} className="bg-navy-800 rounded-xl p-4 border border-navy-700">
              <div className="text-navy-400 text-xs uppercase tracking-wide mb-1">{label}</div>
              <div className="text-white font-semibold">{value}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Cta() {
  return (
    <section id="cta" className="py-20 px-6 bg-orange-500">
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-extrabold text-white mb-4">
          How many calls did your shop miss last month?
        </h2>
        <p className="text-orange-100 text-xl mb-8 leading-relaxed">
          We&apos;ll pull the number in 15 minutes. Free call audit for service businesses in PA/NJ/DE.
          No pitch. Just data.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="https://forrestanalyticsgroup.com"
            className="bg-white text-orange-600 hover:bg-orange-50 font-bold px-8 py-4 rounded-xl text-lg shadow-sm transition-colors flex items-center justify-center gap-2"
            target="_blank" rel="noopener"
          >
            <TrendingUp className="w-5 h-5" /> Book a Free 15-Min Audit
          </a>
          <a
            href="/data/Keystone_Plumbing_Sample_Dataset.xlsx"
            download
            className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-8 py-4 rounded-xl text-lg transition-colors flex items-center justify-center gap-2 border border-orange-400"
          >
            <Download className="w-5 h-5" /> Download the Dataset
          </a>
        </div>
        <p className="text-orange-200 text-sm mt-6">
          Built in Philly. Built for service businesses like yours.
          <br />
          <a href="https://forrestanalyticsgroup.com" className="underline hover:text-white" target="_blank" rel="noopener">
            forrestanalyticsgroup.com
          </a>
        </p>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="bg-navy-950 text-navy-400 py-8 px-6">
      <div className="max-w-4xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 text-sm">
        <p>© 2026 Forrest Analytics Group LLC. All rights reserved.</p>
        <p>Keystone Plumbing &amp; Drain is a fictional company created for demonstration purposes.</p>
      </div>
    </footer>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────
export default function CaseStudyPage() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <CompanyProfile />
        <PainPoints />
        <section id="products">
          {PRODUCTS.map((product, i) => (
            <ProductSection key={product.number} product={product} index={i} />
          ))}
        </section>
        <Architecture />
        <Cta />
      </main>
      <Footer />
    </>
  );
}
