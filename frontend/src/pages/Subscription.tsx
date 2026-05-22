import { useQuery } from "@tanstack/react-query";
import { tenantApi } from "@/api/endpoints";
import PageHeader from "@/components/PageHeader";
import { Badge, Card, CardBody, CardHeader, Loading } from "@/components/ui";

function UsageBar({ label, used, limit }: { label: string; used: number; limit: number }) {
  const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
  return (
    <div>
      <div className="flex justify-between text-sm">
        <span className="text-slate-600">{label}</span>
        <span className="text-slate-500">
          {used} / {limit}
        </span>
      </div>
      <div className="mt-1 h-2 rounded-full bg-slate-100">
        <div className="h-2 rounded-full bg-brand" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function Subscription() {
  const { data: subscription, isLoading } = useQuery({
    queryKey: ["subscription"],
    queryFn: tenantApi.subscription,
  });
  const { data: plans } = useQuery({ queryKey: ["plans"], queryFn: tenantApi.plans });

  if (isLoading || !subscription) return <Loading />;

  return (
    <div>
      <PageHeader
        title="Subscription"
        subtitle="Your current plan and usage (billing not enabled)"
      />

      <Card className="mb-6 max-w-xl">
        <CardHeader
          title="Current plan"
          action={<Badge tone="green">{subscription.plan.toUpperCase()}</Badge>}
        />
        <CardBody className="space-y-4">
          <UsageBar
            label="WhatsApp numbers"
            used={subscription.numbers_used}
            limit={subscription.limits.numbers}
          />
          <UsageBar
            label="Templates"
            used={subscription.templates_used}
            limit={subscription.limits.templates}
          />
          <p className="text-xs text-slate-400">Limits are illustrative and not enforced.</p>
        </CardBody>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {plans?.map((p) => (
          <Card key={p.plan}>
            <CardBody>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold capitalize text-slate-900">{p.plan}</h3>
                {p.plan === subscription.plan && <Badge tone="green">Active</Badge>}
              </div>
              <ul className="mt-3 space-y-1 text-sm text-slate-600">
                <li>{p.limits.numbers} numbers</li>
                <li>{p.limits.templates} templates</li>
              </ul>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}
