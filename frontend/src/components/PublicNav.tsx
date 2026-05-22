import { Link } from "react-router-dom";

export default function PublicNav() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="text-lg font-bold text-brand">
          WhatsApp SaaS
        </Link>
        <nav className="flex items-center gap-6 text-sm font-medium text-slate-600">
          <Link to="/pricing" className="hover:text-slate-900">
            Pricing
          </Link>
          <Link to="/login" className="hover:text-slate-900">
            Log in
          </Link>
          <Link
            to="/register"
            className="rounded-md bg-brand px-4 py-2 text-white hover:bg-brand-dark"
          >
            Get started
          </Link>
        </nav>
      </div>
    </header>
  );
}
