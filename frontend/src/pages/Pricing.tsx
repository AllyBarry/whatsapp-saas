import { Link } from "react-router-dom";
import PublicNav from "@/components/PublicNav";

// Mock pricing — billing is not implemented.
const PLANS = [
  { name: "Free", price: "$0", numbers: 1, templates: 5, highlight: false },
  { name: "Starter", price: "$29", numbers: 3, templates: 25, highlight: false },
  { name: "Business", price: "$99", numbers: 10, templates: 100, highlight: true },
  { name: "Enterprise", price: "Custom", numbers: 100, templates: 1000, highlight: false },
];

export default function Pricing() {
  return (
    <div className="min-h-full">
      <PublicNav />
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-900">Simple, transparent pricing</h1>
          <p className="mt-2 text-sm text-slate-500">
            Plans are illustrative — billing integration is not enabled in this MVP.
          </p>
        </div>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {PLANS.map((p) => (
            <div
              key={p.name}
              className={`rounded-xl border bg-white p-6 shadow-sm ${
                p.highlight ? "border-brand ring-1 ring-brand" : "border-slate-200"
              }`}
            >
              <h3 className="font-semibold text-slate-900">{p.name}</h3>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {p.price}
                {p.price !== "Custom" && (
                  <span className="text-sm font-normal text-slate-500">/mo</span>
                )}
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                <li>{p.numbers} WhatsApp number{p.numbers > 1 ? "s" : ""}</li>
                <li>{p.templates} templates</li>
                <li>Conversation logging</li>
              </ul>
              <Link
                to="/register"
                className="mt-6 block rounded-md bg-brand px-4 py-2 text-center text-sm font-semibold text-white hover:bg-brand-dark"
              >
                Get started
              </Link>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
