/**
 * Persistent banner shown only in demo builds. Makes the mocked nature of the
 * data obvious and lets visitors reset to the seeded state.
 */
import { isDemoMode, resetDemoState } from "@/api/endpoints";
import { useAuthStore } from "@/stores/auth";

export default function DemoBanner() {
  if (!isDemoMode) return null;

  const logout = useAuthStore((s) => s.logout);

  const handleReset = () => {
    resetDemoState();
    logout();
    window.location.href = "/";
  };

  return (
    <div className="flex items-center justify-center gap-3 bg-amber-100 px-4 py-2 text-center text-sm text-amber-900">
      <span>
        <span className="font-semibold">Demo mode.</span> No backend — all data
        is mocked and stored locally in your browser.
      </span>
      <button
        onClick={handleReset}
        className="rounded-md border border-amber-700/30 bg-white/60 px-2 py-0.5 text-xs font-medium text-amber-900 hover:bg-white"
      >
        Reset demo data
      </button>
    </div>
  );
}
