import { useQuery } from "@tanstack/react-query";
import { conversationApi } from "@/api/endpoints";
import PageHeader from "@/components/PageHeader";
import { Card, CardBody, CardHeader, EmptyState, Loading } from "@/components/ui";

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <Card>
      <CardBody>
        <p className="text-sm text-slate-500">{label}</p>
        <p className="mt-1 text-3xl font-bold text-slate-900">{value}</p>
      </CardBody>
    </Card>
  );
}

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: conversationApi.dashboard,
  });

  if (isLoading) return <Loading />;
  if (!data) return <EmptyState title="No dashboard data" />;

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Overview of your WhatsApp workspace" />

      <div className="grid gap-4 sm:grid-cols-3">
        <Stat label="WhatsApp Numbers" value={data.numbers_count} />
        <Stat label="Templates" value={data.templates_count} />
        <Stat label="Conversations" value={data.conversations_count} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Recent template sends" />
          <CardBody className="space-y-3">
            {data.recent_sends.length === 0 && (
              <EmptyState title="No sends yet" hint="Send a template to see activity here." />
            )}
            {data.recent_sends.map((e) => (
              <div key={e.id} className="flex justify-between text-sm">
                <span className="text-slate-700">
                  {String((e.payload as Record<string, unknown>).template ?? e.event_type)}
                </span>
                <span className="text-slate-400">
                  {new Date(e.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Recent webhook activity" />
          <CardBody className="space-y-3">
            {data.recent_webhooks.length === 0 && (
              <EmptyState title="No webhook events" hint="Events from Meta will appear here." />
            )}
            {data.recent_webhooks.map((w, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-slate-700">{String(w.object_type ?? "event")}</span>
                <span className="text-slate-400">
                  {w.created_at ? new Date(String(w.created_at)).toLocaleString() : ""}
                </span>
              </div>
            ))}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
