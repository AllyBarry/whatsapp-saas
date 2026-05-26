/**
 * WhatsApp-style live preview of a template message. The component is pure —
 * it renders whatever it is given, so the parent owns editing state and this
 * reflects the latest draft on every keystroke.
 *
 * Variables `{{1}}, {{2}}, ...` in the body and header are substituted with
 * the provided `sampleValues` (1-indexed). Empty/missing samples render as
 * placeholder pill text so the variable position stays visible.
 */
import type { ReactNode } from "react";

export interface PreviewProps {
  headerText?: string;
  body: string;
  footer?: string;
  /** 1-indexed sample values for {{1}}, {{2}}, ... */
  sampleValues?: Record<number, string>;
}

export function extractVariables(text: string): number[] {
  const matches = text.matchAll(/\{\{(\d+)\}\}/g);
  const numbers = new Set<number>();
  for (const m of matches) numbers.add(Number(m[1]));
  return [...numbers].sort((a, b) => a - b);
}

function substituteVariables(
  text: string,
  sampleValues: Record<number, string> | undefined,
): ReactNode[] {
  if (!text) return [];
  const parts: ReactNode[] = [];
  const regex = /\{\{(\d+)\}\}/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) parts.push(text.slice(last, match.index));
    const num = Number(match[1]);
    const value = sampleValues?.[num]?.trim();
    if (value) {
      parts.push(value);
    } else {
      parts.push(
        <span
          key={`var-${key++}`}
          className="rounded bg-emerald-100 px-1 text-emerald-700"
        >
          {`{{${num}}}`}
        </span>,
      );
    }
    last = match.index + match[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

const TIME_LABEL = "12:34";

export default function WhatsAppPreview({
  headerText,
  body,
  footer,
  sampleValues,
}: PreviewProps) {
  const hasHeader = Boolean(headerText?.trim());
  const hasFooter = Boolean(footer?.trim());

  return (
    // WhatsApp-paper background. Subtle dot pattern via radial gradient.
    <div
      className="rounded-2xl border border-slate-200 p-4 sm:p-6"
      style={{
        background:
          "radial-gradient(rgba(0,0,0,0.04) 1px, transparent 1px) 0 0 / 16px 16px, #e7e3d8",
        minHeight: 520,
      }}
    >
      <div className="mx-auto max-w-sm">
        <p className="mb-3 text-center text-[11px] text-slate-500">Today</p>

        {/* Received bubble (template sent FROM the business TO the customer
            renders as an incoming bubble in the customer's view). */}
        <div className="relative">
          <div className="relative ml-2 rounded-lg rounded-tl-none bg-white px-3 py-2 shadow-sm">
            {/* Tail */}
            <span
              aria-hidden
              className="absolute left-0 top-0 -translate-x-2 border-y-[8px] border-r-[10px] border-y-transparent border-r-white"
            />

            {hasHeader && (
              <p className="mb-1 break-words text-[15px] font-semibold leading-snug text-slate-900">
                {substituteVariables(headerText!, sampleValues)}
              </p>
            )}

            {body.trim() ? (
              <p className="whitespace-pre-wrap break-words text-[14.5px] leading-snug text-slate-800">
                {substituteVariables(body, sampleValues)}
              </p>
            ) : (
              <p className="text-[13px] italic text-slate-400">
                Your message body will appear here.
              </p>
            )}

            {hasFooter && (
              <p className="mt-1 break-words text-[12px] text-slate-400">
                {footer}
              </p>
            )}

            <p className="mt-1 text-right text-[10px] text-slate-400">
              {TIME_LABEL}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
