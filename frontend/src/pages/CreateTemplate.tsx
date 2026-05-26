import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { templateApi } from "@/api/endpoints";
import type { TemplateCategory, TemplateComponent } from "@/types";
import PageHeader from "@/components/PageHeader";
import WhatsAppPreview, { extractVariables } from "@/components/WhatsAppPreview";
import { Button, Card, CardBody, CardHeader, Field } from "@/components/ui";

type HeaderType = "NONE" | "TEXT";

const NAME_PATTERN = /^[a-z0-9_]+$/;

const CATEGORIES: { value: TemplateCategory; label: string; hint: string }[] = [
  { value: "MARKETING", label: "Marketing", hint: "Promotions, offers, announcements" },
  { value: "UTILITY", label: "Utility", hint: "Order updates, confirmations, alerts" },
  { value: "AUTHENTICATION", label: "Authentication", hint: "One-time codes, login" },
];

const LANGUAGES = ["en", "en_US", "en_GB", "af", "zu", "xh", "pt_BR", "es"];

export default function CreateTemplate() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // --- Form state ---------------------------------------------------------
  const [name, setName] = useState("");
  const [category, setCategory] = useState<TemplateCategory>("MARKETING");
  const [language, setLanguage] = useState("en");
  const [headerType, setHeaderType] = useState<HeaderType>("NONE");
  const [headerText, setHeaderText] = useState("");
  const [body, setBody] = useState("Hi {{1}}, your order {{2}} is on its way!");
  const [footer, setFooter] = useState("");
  const [submitToMeta, setSubmitToMeta] = useState(false);
  const [sampleValues, setSampleValues] = useState<Record<number, string>>({
    1: "Alice",
    2: "AC-1042",
  });

  // Variables present in header + body — dictates which sample inputs we show.
  const variables = useMemo(() => {
    const fromBody = extractVariables(body);
    const fromHeader = headerType === "TEXT" ? extractVariables(headerText) : [];
    return [...new Set([...fromHeader, ...fromBody])].sort((a, b) => a - b);
  }, [body, headerText, headerType]);

  // --- Validation ---------------------------------------------------------
  const nameError =
    name && !NAME_PATTERN.test(name)
      ? "Lowercase letters, digits and underscores only"
      : null;
  const bodyError = !body.trim() ? "Body is required" : null;
  const canSubmit = !!name && !nameError && !bodyError;

  // --- Submit -------------------------------------------------------------
  const create = useMutation({
    mutationFn: templateApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      navigate("/app/templates");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    const components: TemplateComponent[] = [];

    if (headerType === "TEXT" && headerText.trim()) {
      const headerVars = extractVariables(headerText);
      const component: TemplateComponent = {
        type: "HEADER",
        format: "TEXT",
        text: headerText.trim(),
      };
      if (headerVars.length > 0) {
        component.example = {
          header_text: headerVars.map((n) => sampleValues[n] || `var${n}`),
        };
      }
      components.push(component);
    }

    const bodyVars = extractVariables(body);
    const bodyComponent: TemplateComponent = { type: "BODY", text: body.trim() };
    if (bodyVars.length > 0) {
      bodyComponent.example = {
        body_text: [bodyVars.map((n) => sampleValues[n] || `var${n}`)],
      };
    }
    components.push(bodyComponent);

    if (footer.trim()) {
      components.push({ type: "FOOTER", text: footer.trim() });
    }

    create.mutate({ name, language, category, components, submit_to_meta: submitToMeta });
  };

  // --- Render -------------------------------------------------------------
  return (
    <div>
      <PageHeader
        title="Create template"
        subtitle="Design a template — the preview on the right updates as you type."
        action={
          <Button variant="secondary" onClick={() => navigate("/app/templates")}>
            Cancel
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-2">
        {/* --- LEFT: form --- */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Card>
            <CardHeader title="Basics" />
            <CardBody className="space-y-4">
              <div>
                <Field
                  label="Name"
                  placeholder="order_confirmation"
                  value={name}
                  onChange={(e) => setName(e.target.value.toLowerCase())}
                  required
                />
                {nameError && (
                  <p className="mt-1 text-xs text-red-600">{nameError}</p>
                )}
                <p className="mt-1 text-xs text-slate-400">
                  Identifier used when sending. Lowercase, digits and underscores only.
                </p>
              </div>

              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">
                  Category
                </span>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value as TemplateCategory)}
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                >
                  {CATEGORIES.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label} — {c.hint}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">
                  Language
                </span>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l} value={l}>
                      {l}
                    </option>
                  ))}
                </select>
              </label>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Message" />
            <CardBody className="space-y-4">
              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">
                  Header
                </span>
                <select
                  value={headerType}
                  onChange={(e) => setHeaderType(e.target.value as HeaderType)}
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="NONE">None</option>
                  <option value="TEXT">Text</option>
                </select>
              </label>

              {headerType === "TEXT" && (
                <Field
                  label="Header text"
                  placeholder="Order update"
                  value={headerText}
                  onChange={(e) => setHeaderText(e.target.value)}
                  maxLength={60}
                />
              )}

              <label className="block">
                <span className="mb-1 block text-sm font-medium text-slate-700">
                  Body <span className="text-red-500">*</span>
                </span>
                <textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  rows={5}
                  maxLength={1024}
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                />
                {bodyError && (
                  <p className="mt-1 text-xs text-red-600">{bodyError}</p>
                )}
                <p className="mt-1 text-xs text-slate-400">
                  Use {"{{"}1{"}}"}, {"{{"}2{"}}"}, … for placeholders that you'll fill
                  in when sending.
                </p>
              </label>

              <Field
                label="Footer (optional)"
                placeholder="Reply STOP to unsubscribe"
                value={footer}
                onChange={(e) => setFooter(e.target.value)}
                maxLength={60}
              />
            </CardBody>
          </Card>

          {variables.length > 0 && (
            <Card>
              <CardHeader title="Sample values for preview" />
              <CardBody className="space-y-3">
                <p className="text-xs text-slate-500">
                  These don't get saved — they're just used to render the preview
                  and as Meta-required examples for review.
                </p>
                {variables.map((n) => (
                  <Field
                    key={n}
                    label={`{{${n}}}`}
                    value={sampleValues[n] ?? ""}
                    onChange={(e) =>
                      setSampleValues({ ...sampleValues, [n]: e.target.value })
                    }
                  />
                ))}
              </CardBody>
            </Card>
          )}

          <Card>
            <CardBody className="space-y-4">
              <label className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={submitToMeta}
                  onChange={(e) => setSubmitToMeta(e.target.checked)}
                  className="mt-1"
                />
                <span className="text-sm">
                  <span className="font-medium text-slate-800">
                    Submit to Meta for review
                  </span>
                  <span className="block text-xs text-slate-500">
                    Requires WhatsApp credentials. If off, the template is saved as
                    a local draft you can preview and iterate on.
                  </span>
                </span>
              </label>

              {create.isError && (
                <p className="text-sm text-red-600">
                  {(create.error as Error).message}
                </p>
              )}

              <div className="flex justify-end gap-3">
                <Button
                  variant="secondary"
                  type="button"
                  onClick={() => navigate("/app/templates")}
                >
                  Cancel
                </Button>
                <Button type="submit" loading={create.isPending} disabled={!canSubmit}>
                  {submitToMeta ? "Submit to Meta" : "Save draft"}
                </Button>
              </div>
            </CardBody>
          </Card>
        </form>

        {/* --- RIGHT: live preview --- */}
        <div className="lg:sticky lg:top-6 lg:self-start">
          <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-500">
            Live preview
          </p>
          <WhatsAppPreview
            headerText={headerType === "TEXT" ? headerText : undefined}
            body={body}
            footer={footer}
            sampleValues={sampleValues}
          />
        </div>
      </div>
    </div>
  );
}
