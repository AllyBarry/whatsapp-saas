import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { conversationApi } from "@/api/endpoints";
import PageHeader from "@/components/PageHeader";
import { Badge, Card, EmptyState, Loading, SlideOver, Table } from "@/components/ui";

export default function Conversations() {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["conversations"],
    queryFn: conversationApi.list,
  });

  const { data: detail } = useQuery({
    queryKey: ["conversation", selectedId],
    queryFn: () => conversationApi.get(selectedId!),
    enabled: selectedId !== null,
  });

  return (
    <div>
      <PageHeader title="Conversations" subtitle="Logged customer conversations" />

      <Card>
        {isLoading ? (
          <Loading />
        ) : !data || data.length === 0 ? (
          <EmptyState title="No conversations" hint="Conversations appear after you send or receive messages." />
        ) : (
          <Table headers={["Customer", "Status", "Started", "Last message"]}>
            {data.map((c) => (
              <tr
                key={c.id}
                className="cursor-pointer hover:bg-slate-50"
                onClick={() => setSelectedId(c.id)}
              >
                <td className="px-5 py-3 font-medium text-slate-800">{c.customer_number}</td>
                <td className="px-5 py-3">
                  <Badge tone={c.status === "open" ? "green" : "gray"}>{c.status}</Badge>
                </td>
                <td className="px-5 py-3 text-slate-600">
                  {new Date(c.started_at).toLocaleString()}
                </td>
                <td className="px-5 py-3 text-slate-600">
                  {new Date(c.last_message_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </Table>
        )}
      </Card>

      <SlideOver
        open={selectedId !== null}
        title={detail?.customer_number || "Conversation"}
        onClose={() => setSelectedId(null)}
      >
        {!detail ? (
          <Loading />
        ) : (
          <div className="space-y-3">
            {(detail.events || []).length === 0 && (
              <EmptyState title="No events" />
            )}
            {(detail.events || []).map((e) => (
              <div key={e.id} className="rounded-lg border border-slate-100 p-3 text-sm">
                <div className="flex justify-between">
                  <Badge tone={e.direction === "outbound" ? "blue" : e.direction === "inbound" ? "green" : "gray"}>
                    {e.event_type}
                  </Badge>
                  <span className="text-xs text-slate-400">
                    {new Date(e.created_at).toLocaleString()}
                  </span>
                </div>
                <pre className="mt-2 overflow-x-auto text-xs text-slate-600">
                  {JSON.stringify(e.payload, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        )}
      </SlideOver>
    </div>
  );
}
