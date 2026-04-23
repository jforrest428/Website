"use client";

import { useState } from "react";
import {
  Phone, Calendar, Wrench, Droplets, Flame, Wind, ShowerHead, Waves,
  Star, Check, ArrowRight, Menu, X
} from "lucide-react";
import BriefingModal from "./components/BriefingModal";
import ReviewModal from "./components/ReviewModal";
import ReengagementModal from "./components/ReengagementModal";
import ReceptionistModal from "./components/ReceptionistModal";

// ── Navigation ─────────────────────────────────────────────────────────────────
function Nav() {
  const [open, setOpen] = useState(false);
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-navy-900/95 backdrop-blur-sm border-b border-navy-800">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-orange-500 rounded-lg flex items-center justify-center">
            <Wrench className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="text-white font-bold text-sm leading-tight">Keystone Plumbing</div>
            <div className="text-orange-400 text-xs">& Drain</div>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-6 text-sm">
          <a href="#services" className="text-navy-300 hover:text-white transition-colors">Services</a>
          <a href="#ai-demo" className="text-navy-300 hover:text-white transition-colors">AI Tools</a>
          <a href="#reviews" className="text-navy-300 hover:text-white transition-colors">Reviews</a>
          <a href="tel:2155550147" className="btn-primary text-sm py-2 px-4">
            <Phone className="w-4 h-4" /> (215) 555-0147
          </a>
        </div>
        <button className="md:hidden text-white" onClick={() => setOpen(!open)}>
          {open ? <X /> : <Menu />}
        </button>
      </div>
      {open && (
        <div className="md:hidden bg-navy-900 border-t border-navy-800 px-4 py-4 flex flex-col gap-4">
          <a href="#services" className="text-navy-200" onClick={() => setOpen(false)}>Services</a>
          <a href="#ai-demo" className="text-navy-200" onClick={() => setOpen(false)}>AI Tools</a>
          <a href="tel:2155550147" className="btn-primary justify-center">
            <Phone className="w-4 h-4" /> (215) 555-0147
          </a>
        </div>
      )}
    </nav>
  );
}

// ── Hero ───────────────────────────────────────────────────────────────────────
function Hero() {
  return (
    <section className="relative bg-navy-900 text-white pt-32 pb-24 overflow-hidden">
      <div className="absolute inset-0 opacity-5" style={{
        backgroundImage: "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
        backgroundSize: "32px 32px"
      }} />
      <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-orange-500/10 to-transparent" />
      <div className="relative max-w-6xl mx-auto px-4">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-1.5 text-orange-400 text-sm font-medium mb-6">
            <span className="w-1.5 h-1.5 bg-orange-400 rounded-full animate-pulse" />
            Available 24/7 — AI-Powered Dispatch
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold leading-tight mb-6">
            Philadelphia&apos;s Trusted Plumber<br />
            <span className="text-orange-400">Since 2014.</span>
          </h1>
          <p className="text-xl text-navy-200 mb-8 max-w-xl leading-relaxed">
            Keystone Plumbing &amp; Drain serves the Main Line and western suburbs.
            Licensed master plumbers. Emergency response. Fair, upfront pricing.
          </p>
          <div className="flex flex-wrap gap-4">
            <a href="tel:2155550147" className="btn-primary text-base py-3.5 px-8">
              <Phone className="w-5 h-5" /> Call Now — (215) 555-0147
            </a>
            <a href="#ai-demo" className="btn-outline text-base py-3.5 px-8">
              <Calendar className="w-5 h-5" /> Book Online
            </a>
          </div>
          <div className="mt-10 flex flex-wrap gap-6 text-sm text-navy-300">
            {["Licensed & Insured", "Same-Day Emergency", "Free Estimates", "Serving 25+ Towns"].map(item => (
              <span key={item} className="flex items-center gap-1.5">
                <Check className="w-4 h-4 text-orange-400" /> {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ── Trust Bar ──────────────────────────────────────────────────────────────────
function TrustBar() {
  return (
    <div className="bg-orange-500 text-white py-4">
      <div className="max-w-6xl mx-auto px-4 flex flex-wrap justify-center md:justify-between gap-4 text-sm font-semibold">
        <span>📍 Main Line &amp; Western Suburbs, PA</span>
        <span>⭐ 4.5 Stars · 420+ Reviews</span>
        <span>🔧 8 Licensed Technicians · 5 Trucks</span>
        <span>🕐 24/7 Emergency Dispatch</span>
      </div>
    </div>
  );
}

// ── Services ───────────────────────────────────────────────────────────────────
const SERVICES = [
  { icon: Droplets,   label: "Plumbing Repairs",  desc: "Leaks, burst pipes, fixtures, remodels" },
  { icon: Waves,      label: "Drain Cleaning",     desc: "Hydro jetting, snaking, camera inspection" },
  { icon: Flame,      label: "Water Heaters",      desc: "Install, repair, tankless upgrades" },
  { icon: Wrench,     label: "Sewer Services",     desc: "Line repair, inspection, repiping" },
  { icon: ShowerHead, label: "Sump Pumps",         desc: "Install, repair, battery backup" },
  { icon: Wind,       label: "Light HVAC",         desc: "Boiler repair, furnace, AC tune-ups" },
];

function Services() {
  return (
    <section id="services" className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="section-heading">Everything Under One Roof</h2>
          <p className="section-sub mx-auto text-center">
            From a dripping faucet to a full sewer replacement — one call, one company, one crew you can trust.
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
          {SERVICES.map(({ icon: Icon, label, desc }) => (
            <div key={label} className="card hover:shadow-md transition-shadow group cursor-pointer">
              <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-orange-100 transition-colors">
                <Icon className="w-6 h-6 text-orange-500" />
              </div>
              <h3 className="font-bold text-navy-900 mb-1">{label}</h3>
              <p className="text-sm text-navy-500">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ── AI Demo Strip ──────────────────────────────────────────────────────────────
const AI_PRODUCTS = [
  {
    id: "receptionist",
    emoji: "📞",
    title: "24/7 AI Receptionist",
    tagline: "Answers every call. Books every job.",
    description: "Never miss a call again. Our AI answers 24/7, diagnoses the issue, books the appointment, and texts a confirmation — all before the caller hangs up.",
    cta: "Hear a live call demo",
  },
  {
    id: "reviews",
    emoji: "⭐",
    title: "Review Reply Manager",
    tagline: "Every review answered in minutes.",
    description: "Our AI drafts personalized, on-brand responses to every Google, Yelp, and Angi review. Owner approves with one tap. Flags problem patterns by tech.",
    cta: "See a sample reply",
  },
  {
    id: "reengagement",
    emoji: "💬",
    title: "Re-Engagement Engine",
    tagline: "$25K+ sitting in your customer list.",
    description: "AI segments dormant customers by service type and timing, writes personalized SMS and email outreach, and projects recovered revenue week over week.",
    cta: "See the dashboard",
  },
  {
    id: "briefing",
    emoji: "📱",
    title: "Owner's Daily Briefing",
    tagline: "Run your shop from a text message.",
    description: "Every morning at 6am, the owner gets a 60-second SMS with yesterday's revenue, today's schedule, open A/R, and any reputation issues. No dashboard. No login.",
    cta: "See today's briefing",
  },
];

function AiDemoStrip({ onOpen }: { onOpen: (id: string) => void }) {
  return (
    <section id="ai-demo" className="py-20 bg-navy-950">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-14">
          <div className="inline-block bg-orange-500/10 border border-orange-500/20 rounded-full px-4 py-1.5 text-orange-400 text-sm font-medium mb-4">
            Powered by AI · Built by Forrest Intelligence
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            The Keystone AI Operating System
          </h2>
          <p className="text-navy-300 text-lg max-w-2xl mx-auto">
            Four AI tools working together — running the parts of the business that used to fall through the cracks.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {AI_PRODUCTS.map((product) => (
            <div
              key={product.id}
              className="bg-navy-800 border border-navy-700 rounded-2xl p-6 hover:border-orange-500/40 transition-all group"
            >
              <div className="flex items-start justify-between mb-4">
                <span className="text-3xl">{product.emoji}</span>
                <span className="text-xs bg-navy-700 text-navy-300 rounded-full px-3 py-1">Live Demo</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-1">{product.title}</h3>
              <p className="text-orange-400 text-sm font-medium mb-3">{product.tagline}</p>
              <p className="text-navy-300 text-sm leading-relaxed mb-5">{product.description}</p>
              <button
                onClick={() => onOpen(product.id)}
                className="flex items-center gap-2 text-orange-400 hover:text-orange-300 font-semibold text-sm transition-colors"
              >
                {product.cta} <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
        <p className="text-center text-navy-500 text-sm mt-8">
          These tools run on{" "}
          <span className="text-navy-300">real operational data</span> from Keystone&apos;s 850-customer dataset.
          Built by{" "}
          <a href="https://forrestintelligence.com" className="text-orange-400 hover:underline" target="_blank" rel="noopener">
            Forrest Intelligence
          </a>.
        </p>
      </div>
    </section>
  );
}

// ── Testimonials ───────────────────────────────────────────────────────────────
const TESTIMONIALS = [
  {
    name: "Brian & Carol Holloway",
    location: "Wayne, PA",
    stars: 5,
    text: "Keystone has handled everything at our house for three years. What's different now is the AI. I got a text at 6am telling me exactly what was on the schedule. I didn't have to call to check in. I booked the last appointment at 11pm through what I thought was a person — turned out it was their AI. It knew the right questions and had someone out the next morning.",
  },
  {
    name: "Sandra Kim",
    location: "Property Manager, Norristown, PA",
    stars: 5,
    text: "I manage six units and used to play phone tag for a week every time something came up. Now I get a response under 5 minutes no matter when I call. They also replied to my one-star Google review from 2 years ago — a real, thoughtful response. That's who I give my business to.",
  },
];

function Testimonials() {
  return (
    <section id="reviews" className="py-20 bg-navy-50">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="section-heading">What Our Customers Say</h2>
          <p className="section-sub mx-auto text-center">Real reviews from Philadelphia-area homeowners and property managers.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {TESTIMONIALS.map((t) => (
            <div key={t.name} className="card">
              <div className="flex gap-0.5 mb-4">
                {Array.from({ length: t.stars }).map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-orange-400 text-orange-400" />
                ))}
              </div>
              <p className="text-navy-700 leading-relaxed mb-4 italic">&ldquo;{t.text}&rdquo;</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-navy-200 rounded-full flex items-center justify-center text-navy-700 font-bold">
                  {t.name[0]}
                </div>
                <div>
                  <div className="font-semibold text-navy-900 text-sm">{t.name}</div>
                  <div className="text-navy-400 text-xs">{t.location}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ── CTA Band ───────────────────────────────────────────────────────────────────
function CtaBand() {
  return (
    <section className="bg-orange-500 py-16">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Need a plumber today?</h2>
        <p className="text-orange-100 text-lg mb-8">We answer every call 24/7. No voicemail. No waiting.</p>
        <div className="flex flex-wrap justify-center gap-4">
          <a href="tel:2155550147" className="bg-white text-orange-600 hover:bg-orange-50 font-bold px-8 py-4 rounded-xl text-lg shadow-sm transition-colors flex items-center gap-2">
            <Phone className="w-5 h-5" /> (215) 555-0147
          </a>
          <a href="#ai-demo" className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-8 py-4 rounded-xl text-lg transition-colors flex items-center gap-2">
            <Calendar className="w-5 h-5" /> Book Online
          </a>
        </div>
      </div>
    </section>
  );
}

// ── Footer ─────────────────────────────────────────────────────────────────────
function Footer() {
  return (
    <footer className="bg-navy-950 text-navy-400 py-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between gap-8 mb-8">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <Wrench className="w-4 h-4 text-white" />
              </div>
              <span className="text-white font-bold">Keystone Plumbing &amp; Drain</span>
            </div>
            <p className="text-sm max-w-xs">Philadelphia&apos;s trusted plumber since 2014. Licensed, insured, and always available.</p>
          </div>
          <div className="text-sm">
            <div className="text-white font-semibold mb-2">Service Area</div>
            <p>Wayne, Ardmore, Glenside, Norristown,<br />Bala Cynwyd, King of Prussia, Haverford,<br />Drexel Hill, Chester, Bryn Mawr + more</p>
          </div>
          <div className="text-sm">
            <div className="text-white font-semibold mb-2">Contact</div>
            <p>(215) 555-0147<br />mike@keystoneplumbingphilly.com<br />24/7 Emergency Line</p>
          </div>
        </div>
        <div className="border-t border-navy-800 pt-6 flex flex-col md:flex-row justify-between items-center gap-4 text-xs">
          <p>© 2026 Keystone Plumbing &amp; Drain LLC. PA License #PA-047821.</p>
          <p>
            AI-powered by{" "}
            <a href="https://forrestintelligence.com" className="text-orange-400 hover:underline font-medium" target="_blank" rel="noopener">
              Forrest Intelligence — AI for service businesses
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}

// ── Root Page ──────────────────────────────────────────────────────────────────
export default function KeystonePage() {
  const [modal, setModal] = useState<string | null>(null);
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <TrustBar />
        <Services />
        <AiDemoStrip onOpen={setModal} />
        <Testimonials />
        <CtaBand />
      </main>
      <Footer />
      {modal === "briefing"     && <BriefingModal     onClose={() => setModal(null)} />}
      {modal === "reviews"      && <ReviewModal       onClose={() => setModal(null)} />}
      {modal === "reengagement" && <ReengagementModal onClose={() => setModal(null)} />}
      {modal === "receptionist" && <ReceptionistModal onClose={() => setModal(null)} />}
    </>
  );
}
