import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { messageApi, templateApi } from "@/api/endpoints";
import PageHeader from "@/components/PageHeader";
import { Button, Card, CardBody, Field } from "@/components/ui";

export default function SendMessage() {
  const { data: templates } = useQuery({
    queryKey: ["templates", ""],
    queryFn: () => templateApi.list(),
  });

  const [templateName, setTemplateName] = useState("");
  const [language, setLanguage] = useState("en");
  const [recipient, setRecipient] = useState("");
  const [variablesText, setVariablesText] = useState("{}");
  const [jsonError, setJsonError] = useState<string | null>(null);

  const send = useMutation({
    mutationFn: messageApi.sendTemplate,
  });

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setJsonError(null);
    let variables: Record<string, string>;
    try {
      variables = JSON.parse(variablesText || "{}");
    } catch {
      setJsonError("Variables must be valid JSON");
      return;
    }
    send.mutate({ template_name: templateName, language, recipient, variables });
  };

  return (
    <div>
      <PageHeader title="Send Message" subtitle="Send a WhatsApp template to a recipient" />
      <Card className="max-w-xl">
        <CardBody>
          <form onSubmit={submit} className="space-y-4">
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">Template</span>
              <select
                value={templateName}
                onChange={(e) => {
                  const t = templates?.find((x) => x.name === e.target.value);
                  setTemplateName(e.target.value);
                  if (t) setLanguage(t.language);
                }}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
                required
              >
                <option value="">Select a template…</option>
                {templates?.map((t) => (
                  <option key={t.id} value={t.name}>
                    {t.name} ({t.language})
                  </option>
                ))}
              </select>
            </label>

            <Field
              label="Language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              required
            />
            <Field
              label="Recipient (E.164)"
              placeholder="+27821234567"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              required
            />

            <label className="block">
              <span className="mb-1 block text-sm font-medium text-slate-700">
                Variables (JSON)
              </span>
              <textarea
                value={variablesText}
                onChange={(e) => setVariablesText(e.target.value)}
                rows={4}
                className="w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-sm"
              />
            </label>
            {jsonError && <p className="text-sm text-red-600">{jsonError}</p>}

            <Button type="submit" loading={send.isPending}>
              Send template
            </Button>

            {send.isSuccess && (
              <p className="text-sm text-green-600">Message sent successfully.</p>
            )}
            {send.isError && (
              <p className="text-sm text-red-600">{(send.error as Error).message}</p>
            )}
          </form>
        </CardBody>
      </Card>
    </div>
  );
}
