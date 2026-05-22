import { Link } from "react-router-dom";
import PublicNav from "@/components/PublicNav";

const FEATURES = [
  { title: "WhatsApp Numbers", body: "Sync and monitor every number under your WABA in one place." },
  { title: "Template Management", body: "Pull approved templates from Meta and send them in seconds." },
  { title: "Conversation Logging", body: "Every outbound send and webhook event captured automatically." },
  { title: "Multi-Tenant", body: "Strict tenant isolation — built for agencies and resellers." },
];

export default function Landing() {
  return (
    <div className="min-h-full">
      <PublicNav />
      <section className="mx-auto max-w-6xl px-6 py-24 text-center">
        <h1 className="mx-auto max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Manage WhatsApp at scale, for every client
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-lg text-slate-600">
          A multi-tenant control plane for the WhatsApp Cloud API — numbers,
          templates, sending and conversations in one dashboard.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link
            to="/register"
            className="rounded-md bg-brand px-6 py-3 text-sm font-semibold text-white hover:bg-brand-dark"
          >
            Start free
          </Link>
          <Link
            to="/pricing"
            className="rounded-md border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            View pricing
          </Link>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 pb-24 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((f) => (
          <div key={f.title} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="font-semibold text-slate-900">{f.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{f.body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
