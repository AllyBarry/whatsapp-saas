import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { templateApi } from "@/api/endpoints";
import type { Template } from "@/types";
import PageHeader from "@/components/PageHeader";
import {
  Badge,
  Button,
  Card,
  EmptyState,
  Loading,
  SlideOver,
  Table,
  statusTone,
} from "@/components/ui";

const STATUS_FILTERS = ["", "APPROVED", "PENDING", "REJECTED"];

/** Extract the BODY component text from a Meta template payload. */
function templateBody(t: Template): string {
  const components = (t.template_json?.components as Array<Record<string, unknown>>) || [];
  const body = components.find((c) => c.type === "BODY");
  return (body?.text as string) || "No body preview available.";
}

export default function Templates() {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState("");
  const [preview, setPreview] = useState<Template | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["templates", status],
    queryFn: () => templateApi.list(status || undefined),
  });

  const sync = useMutation({
    mutationFn: templateApi.sync,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["templates"] }),
  });

  return (
    <div>
      <PageHeader
        title="Templates"
        subtitle="Message templates synced from Meta"
        action={
          <Button onClick={() => sync.mutate()} loading={sync.isPending}>
            Sync templates
          </Button>
        }
      />

      <div className="mb-4 flex gap-2">
        {STATUS_FILTERS.map((s) => (
          <button
            key={s || "all"}
            onClick={() => setStatus(s)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              status === s ? "bg-brand text-white" : "bg-white text-slate-600 border border-slate-300"
            }`}
          >
            {s || "All"}
          </button>
        ))}
      </div>
      {sync.isError && (
        <p className="mb-4 text-sm text-red-600">{(sync.error as Error).message}</p>
      )}

      <Card>
        {isLoading ? (
          <Loading />
        ) : !data || data.length === 0 ? (
          <EmptyState title="No templates" hint="Sync templates from Meta to get started." />
        ) : (
          <Table headers={["Name", "Language", "Category", "Status", ""]}>
            {data.map((t) => (
              <tr key={t.id}>
                <td className="px-5 py-3 font-medium text-slate-800">{t.name}</td>
                <td className="px-5 py-3 text-slate-600">{t.language}</td>
                <td className="px-5 py-3 text-slate-600">{t.category || "—"}</td>
                <td className="px-5 py-3">
                  <Badge tone={statusTone(t.status)}>{t.status || "—"}</Badge>
                </td>
                <td className="px-5 py-3 text-right">
                  <Button variant="ghost" onClick={() => setPreview(t)}>
                    Preview
                  </Button>
                </td>
              </tr>
            ))}
          </Table>
        )}
      </Card>

      <SlideOver
        open={preview !== null}
        title={preview?.name || "Template"}
        onClose={() => setPreview(null)}
      >
        {preview && (
          <div className="space-y-4 text-sm">
            <div className="flex gap-2">
              <Badge tone="blue">{preview.language}</Badge>
              <Badge tone={statusTone(preview.status)}>{preview.status}</Badge>
            </div>
            <div className="rounded-lg bg-slate-50 p-4 text-slate-700 whitespace-pre-wrap">
              {templateBody(preview)}
            </div>
            <p className="text-xs text-slate-400">
              Test sends are available on the Send Message page.
            </p>
          </div>
        )}
      </SlideOver>
    </div>
  );
}
