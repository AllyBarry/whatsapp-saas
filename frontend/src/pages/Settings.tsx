import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { credentialApi } from "@/api/endpoints";
import PageHeader from "@/components/PageHeader";
import { Badge, Button, Card, CardBody, CardHeader, Field, Loading } from "@/components/ui";

const EMPTY = {
  access_token: "",
  app_secret: "",
  verify_token: "",
  waba_id: "",
  phone_number_id: "",
};

export default function Settings() {
  const queryClient = useQueryClient();
  const { data: credential, isLoading } = useQuery({
    queryKey: ["credentials"],
    queryFn: credentialApi.get,
  });

  const [form, setForm] = useState(EMPTY);

  // Pre-fill non-secret fields from the stored credential.
  useEffect(() => {
    if (credential) {
      setForm((f) => ({
        ...f,
        verify_token: credential.verify_token,
        waba_id: credential.waba_id,
        phone_number_id: credential.phone_number_id,
      }));
    }
  }, [credential]);

  const save = useMutation({
    mutationFn: credentialApi.save,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["credentials"] }),
  });

  const update = (key: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [key]: e.target.value });

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    save.mutate(form);
  };

  if (isLoading) return <Loading />;

  return (
    <div>
      <PageHeader title="Settings" subtitle="WhatsApp Cloud API credentials" />
      <Card className="max-w-xl">
        <CardHeader
          title="Meta credentials"
          action={
            credential ? (
              <Badge tone="green">Configured</Badge>
            ) : (
              <Badge tone="yellow">Not set</Badge>
            )
          }
        />
        <CardBody>
          <form onSubmit={submit} className="space-y-4">
            <Field
              label="Access token"
              type="password"
              placeholder={credential?.has_access_token ? "•••••••• (stored)" : ""}
              value={form.access_token}
              onChange={update("access_token")}
              required={!credential}
            />
            <Field
              label="App secret"
              type="password"
              placeholder={credential?.has_app_secret ? "•••••••• (stored)" : ""}
              value={form.app_secret}
              onChange={update("app_secret")}
              required={!credential}
            />
            <Field
              label="Verify token"
              value={form.verify_token}
              onChange={update("verify_token")}
              required
            />
            <Field
              label="WABA ID"
              value={form.waba_id}
              onChange={update("waba_id")}
              required
            />
            <Field
              label="Phone number ID"
              value={form.phone_number_id}
              onChange={update("phone_number_id")}
              required
            />
            <p className="text-xs text-slate-400">
              Secrets are encrypted at rest and never returned by the API.
            </p>
            <Button type="submit" loading={save.isPending}>
              Save credentials
            </Button>
            {save.isSuccess && (
              <p className="text-sm text-green-600">Credentials saved.</p>
            )}
            {save.isError && (
              <p className="text-sm text-red-600">{(save.error as Error).message}</p>
            )}
          </form>
        </CardBody>
      </Card>
    </div>
  );
}
