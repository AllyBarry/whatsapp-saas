import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { numberApi } from "@/api/endpoints";
import PageHeader from "@/components/PageHeader";
import { Badge, Button, Card, EmptyState, Loading, Table, statusTone } from "@/components/ui";

export default function Numbers() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["numbers"], queryFn: numberApi.list });

  const sync = useMutation({
    mutationFn: numberApi.sync,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["numbers"] }),
  });

  return (
    <div>
      <PageHeader
        title="WhatsApp Numbers"
        subtitle="Phone numbers registered under your WABA"
        action={
          <Button onClick={() => sync.mutate()} loading={sync.isPending}>
            Sync numbers
          </Button>
        }
      />
      {sync.isError && (
        <p className="mb-4 text-sm text-red-600">{(sync.error as Error).message}</p>
      )}

      <Card>
        {isLoading ? (
          <Loading />
        ) : !data || data.length === 0 ? (
          <EmptyState
            title="No numbers synced"
            hint="Configure credentials in Settings, then sync."
          />
        ) : (
          <Table
            headers={["Phone number", "Display name", "Quality", "Status", "Messaging limit"]}
          >
            {data.map((n) => (
              <tr key={n.id}>
                <td className="px-5 py-3 font-medium text-slate-800">
                  {n.display_phone_number || n.phone_number_id}
                </td>
                <td className="px-5 py-3 text-slate-600">{n.verified_name || "—"}</td>
                <td className="px-5 py-3">
                  <Badge tone={statusTone(n.quality_rating)}>{n.quality_rating || "—"}</Badge>
                </td>
                <td className="px-5 py-3">
                  <Badge tone={statusTone(n.status)}>{n.status || "—"}</Badge>
                </td>
                <td className="px-5 py-3 text-slate-600">{n.messaging_limit || "—"}</td>
              </tr>
            ))}
          </Table>
        )}
      </Card>
    </div>
  );
}
