import { api, unwrap } from "./client";
import type {
  AuthResult,
  Conversation,
  Credential,
  DashboardStats,
  PlanInfo,
  Subscription,
  Template,
  Tenant,
  User,
  WhatsAppNumber,
} from "@/types";

// --- Auth ---
export const authApi = {
  register: (body: { company_name: string; email: string; password: string }) =>
    api.post("/api/v1/auth/register", body).then((r) => unwrap<AuthResult>(r.data)),
  login: (body: { email: string; password: string }) =>
    api.post("/api/v1/auth/login", body).then((r) => unwrap<AuthResult>(r.data)),
  me: () => api.get("/api/v1/auth/me").then((r) => unwrap<User>(r.data)),
};

// --- Tenant / subscription ---
export const tenantApi = {
  get: () => api.get("/api/v1/tenant").then((r) => unwrap<Tenant>(r.data)),
  subscription: () =>
    api.get("/api/v1/subscription").then((r) => unwrap<Subscription>(r.data)),
  plans: () => api.get("/api/v1/plans").then((r) => unwrap<PlanInfo[]>(r.data)),
};

// --- Credentials ---
export const credentialApi = {
  get: () =>
    api.get("/api/v1/credentials").then((r) => unwrap<Credential | null>(r.data)),
  save: (body: {
    access_token: string;
    app_secret: string;
    verify_token: string;
    waba_id: string;
    phone_number_id: string;
  }) => api.put("/api/v1/credentials", body).then((r) => unwrap<Credential>(r.data)),
};

// --- Numbers ---
export const numberApi = {
  list: () => api.get("/api/v1/numbers").then((r) => unwrap<WhatsAppNumber[]>(r.data)),
  sync: () =>
    api.post("/api/v1/numbers/sync").then((r) => unwrap<WhatsAppNumber[]>(r.data)),
};

// --- Templates ---
export const templateApi = {
  list: (status?: string) =>
    api
      .get("/api/v1/templates", { params: status ? { status } : {} })
      .then((r) => unwrap<Template[]>(r.data)),
  sync: () =>
    api
      .post("/api/v1/templates/sync")
      .then((r) => unwrap<{ synced: number; created: number; updated: number }>(r.data)),
};

// --- Messages ---
export const messageApi = {
  sendTemplate: (body: {
    template_name: string;
    language: string;
    recipient: string;
    variables: Record<string, string>;
  }) =>
    api.post("/api/v1/messages/send-template", body).then((r) => unwrap(r.data)),
};

// --- Conversations / dashboard ---
export const conversationApi = {
  list: () =>
    api.get("/api/v1/conversations").then((r) => unwrap<Conversation[]>(r.data)),
  get: (id: string) =>
    api.get(`/api/v1/conversations/${id}`).then((r) => unwrap<Conversation>(r.data)),
  dashboard: () =>
    api.get("/api/v1/dashboard").then((r) => unwrap<DashboardStats>(r.data)),
};
