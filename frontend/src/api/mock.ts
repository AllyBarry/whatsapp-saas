/**
 * Mock API layer used in demo builds (VITE_DEMO_MODE=true).
 *
 * Mirrors the public surface of `./real.ts` exactly so the page components
 * don't need to know which mode they're running in. State persists in
 * localStorage so the demo feels real across reloads; use `resetDemoState()`
 * to wipe it back to the seed.
 */
import type {
  AuthResult,
  Conversation,
  ConversationEvent,
  Credential,
  DashboardStats,
  PlanInfo,
  Plan,
  Subscription,
  Template,
  Tenant,
  User,
  WhatsAppNumber,
} from "@/types";

const STORAGE_KEY = "whatsapp-saas-demo-state";
const DEMO_TENANT_ID = "demo-tenant-000";
const DEMO_USER_ID = "demo-user-000";

interface DemoState {
  numbers: WhatsAppNumber[];
  templates: Template[];
  conversations: Conversation[];
  credential: Credential | null;
  plan: Plan;
}

// --- Seed data ---------------------------------------------------------------

function seed(): DemoState {
  const now = new Date().toISOString();
  return {
    plan: "business",
    credential: null,
    numbers: [
      {
        id: "n-1",
        phone_number_id: "55667788",
        display_phone_number: "+27 82 123 4567",
        verified_name: "Acme Demo",
        quality_rating: "GREEN",
        status: "CONNECTED",
        messaging_limit: "TIER_1K",
        created_at: "2026-04-15T10:00:00Z",
      },
      {
        id: "n-2",
        phone_number_id: "55667789",
        display_phone_number: "+27 82 765 4321",
        verified_name: "Acme Support",
        quality_rating: "GREEN",
        status: "CONNECTED",
        messaging_limit: "TIER_10K",
        created_at: "2026-04-20T14:30:00Z",
      },
      {
        id: "n-3",
        phone_number_id: "55667790",
        display_phone_number: "+27 11 987 6543",
        verified_name: "Acme Sales",
        quality_rating: "YELLOW",
        status: "PENDING",
        messaging_limit: "TIER_250",
        created_at: "2026-05-10T09:15:00Z",
      },
    ],
    templates: [
      mkTemplate("t-1", "welcome_message", "APPROVED", "MARKETING",
        "Hi {{1}}, welcome to {{2}}! We're glad to have you on board."),
      mkTemplate("t-2", "order_confirmation", "APPROVED", "UTILITY",
        "Order {{1}} confirmed for R{{2}}. We'll notify you when it ships."),
      mkTemplate("t-3", "appointment_reminder", "APPROVED", "UTILITY",
        "Reminder: your appointment is on {{1}} at {{2}}."),
      mkTemplate("t-4", "delivery_update", "PENDING", "UTILITY",
        "Your order {{1}} is out for delivery and will arrive today."),
      mkTemplate("t-5", "promo_summer", "APPROVED", "MARKETING",
        "Hi {{1}}, our summer promo gives you 20% off. Use code SUMMER20."),
      mkTemplate("t-6", "support_followup", "REJECTED", "UTILITY",
        "Hi {{1}}, please rate your recent support experience: {{2}}"),
    ],
    conversations: [
      mkConversation("c-1", "+27821112222", "open", now, [
        mkEvent("template_sent", "outbound", { template: "welcome_message" }),
        mkEvent("inbound_message", "inbound", { text: "Thanks! Looking forward to it." }),
      ]),
      mkConversation("c-2", "+27823334444", "open", now, [
        mkEvent("template_sent", "outbound", { template: "order_confirmation" }),
        mkEvent("status_delivered", "system", { status: "delivered" }),
      ]),
      mkConversation("c-3", "+27825556666", "closed", now, [
        mkEvent("template_sent", "outbound", { template: "appointment_reminder" }),
        mkEvent("inbound_message", "inbound", { text: "Got it, see you then." }),
      ]),
      mkConversation("c-4", "+27827778888", "open", now, [
        mkEvent("template_sent", "outbound", { template: "promo_summer" }),
      ]),
    ],
  };
}

function mkTemplate(
  id: string,
  name: string,
  status: string,
  category: string,
  body: string,
): Template {
  return {
    id,
    meta_template_id: id.replace("t-", "100"),
    name,
    language: "en",
    category,
    status,
    template_json: { components: [{ type: "BODY", text: body }] },
    created_at: "2026-04-01T08:00:00Z",
  };
}

function mkConversation(
  id: string,
  customer: string,
  status: "open" | "closed",
  ts: string,
  events: ConversationEvent[],
): Conversation {
  return {
    id,
    customer_number: customer,
    started_at: ts,
    last_message_at: ts,
    status,
    events,
  };
}

function mkEvent(
  event_type: string,
  direction: "inbound" | "outbound" | "system",
  payload: Record<string, unknown>,
): ConversationEvent {
  return {
    id: `e-${Math.random().toString(36).slice(2, 10)}`,
    event_type,
    direction,
    payload,
    created_at: new Date().toISOString(),
  };
}

// --- State + helpers --------------------------------------------------------

function load(): DemoState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as DemoState;
  } catch {
    /* fall through to seed */
  }
  const fresh = seed();
  save(fresh);
  return fresh;
}

function save(state: DemoState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    /* localStorage full / unavailable — drop silently */
  }
}

function update<T>(mutator: (state: DemoState) => T): T {
  const state = load();
  const result = mutator(state);
  save(state);
  return result;
}

/** Wipe demo state — used by the "Reset demo data" button. */
export function resetDemoState(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

const delay = (ms = 250) =>
  new Promise<void>((r) => setTimeout(r, ms + Math.random() * 150));

const PLAN_LIMITS: Record<Plan, { numbers: number; templates: number }> = {
  free: { numbers: 1, templates: 5 },
  starter: { numbers: 3, templates: 25 },
  business: { numbers: 10, templates: 100 },
  enterprise: { numbers: 100, templates: 1000 },
};

function makeAuthResult(email: string): AuthResult {
  const user: User = {
    id: DEMO_USER_ID,
    tenant_id: DEMO_TENANT_ID,
    email,
    role: "owner",
  };
  return {
    token: {
      access_token: `demo-${Math.random().toString(36).slice(2, 10)}`,
      token_type: "bearer",
      expires_in: 60 * 60 * 24,
    },
    user,
  };
}

// --- Mocked APIs (shape mirrors real.ts) ------------------------------------

export const authApi = {
  async register(body: { company_name: string; email: string; password: string }) {
    await delay();
    // Reset to seed when a new account is "created" — keeps demos predictable.
    resetDemoState();
    return makeAuthResult(body.email);
  },
  async login(body: { email: string; password: string }) {
    await delay();
    return makeAuthResult(body.email);
  },
  async me(): Promise<User> {
    await delay(100);
    return {
      id: DEMO_USER_ID,
      tenant_id: DEMO_TENANT_ID,
      email: "demo@acmeco.com",
      role: "owner",
    };
  },
};

export const tenantApi = {
  async get(): Promise<Tenant> {
    await delay(100);
    const state = load();
    return {
      id: DEMO_TENANT_ID,
      name: "Acme Demo Co",
      slug: "acme-demo",
      status: "active",
      subscription_plan: state.plan,
      created_at: "2026-03-01T10:00:00Z",
    };
  },
  async subscription(): Promise<Subscription> {
    await delay(100);
    const state = load();
    return {
      plan: state.plan,
      limits: PLAN_LIMITS[state.plan],
      numbers_used: state.numbers.length,
      templates_used: state.templates.length,
    };
  },
  async plans(): Promise<PlanInfo[]> {
    await delay(80);
    return (Object.keys(PLAN_LIMITS) as Plan[]).map((plan) => ({
      plan,
      limits: PLAN_LIMITS[plan],
    }));
  },
};

export const credentialApi = {
  async get(): Promise<Credential | null> {
    await delay(100);
    return load().credential;
  },
  async save(body: {
    access_token: string;
    app_secret: string;
    verify_token: string;
    waba_id: string;
    phone_number_id: string;
  }): Promise<Credential> {
    await delay();
    return update((state) => {
      const cred: Credential = {
        id: "cred-1",
        tenant_id: DEMO_TENANT_ID,
        waba_id: body.waba_id,
        phone_number_id: body.phone_number_id,
        verify_token: body.verify_token,
        has_access_token: Boolean(body.access_token),
        has_app_secret: Boolean(body.app_secret),
        created_at: new Date().toISOString(),
      };
      state.credential = cred;
      return cred;
    });
  },
};

export const numberApi = {
  async list(): Promise<WhatsAppNumber[]> {
    await delay(100);
    return load().numbers;
  },
  async sync(): Promise<WhatsAppNumber[]> {
    await delay(600);
    return update((state) => {
      // Touch each number's status string to simulate a refresh.
      for (const n of state.numbers) {
        if (n.status === "PENDING" && Math.random() > 0.5) n.status = "CONNECTED";
      }
      return state.numbers;
    });
  },
};

export const templateApi = {
  async list(status?: string): Promise<Template[]> {
    await delay(100);
    const all = load().templates;
    if (!status) return all;
    return all.filter((t) => (t.status || "").toUpperCase() === status.toUpperCase());
  },
  async sync(): Promise<{ synced: number; created: number; updated: number }> {
    await delay(700);
    const state = load();
    return { synced: state.templates.length, created: 0, updated: state.templates.length };
  },
};

export const messageApi = {
  async sendTemplate(body: {
    template_name: string;
    language: string;
    recipient: string;
    variables: Record<string, string>;
  }) {
    await delay(500);
    return update((state) => {
      // Append to an existing conversation or open a new one.
      let conv = state.conversations.find((c) => c.customer_number === body.recipient);
      if (!conv) {
        conv = mkConversation(
          `c-${Math.random().toString(36).slice(2, 8)}`,
          body.recipient,
          "open",
          new Date().toISOString(),
          [],
        );
        state.conversations.unshift(conv);
      }
      const event = mkEvent("template_sent", "outbound", {
        template: body.template_name,
        language: body.language,
        variables: body.variables,
        message_id: `msg-${Math.random().toString(36).slice(2, 12)}`,
      });
      conv.events = [...(conv.events ?? []), event];
      conv.last_message_at = event.created_at;
      return {
        message_id: event.payload.message_id,
        recipient: body.recipient,
        conversation_id: conv.id,
        status: "sent",
      };
    });
  },
};

export const conversationApi = {
  async list(): Promise<Conversation[]> {
    await delay(100);
    // Hide the events on the list endpoint to match the real API shape.
    return load().conversations.map(({ events: _events, ...c }) => c);
  },
  async get(id: string): Promise<Conversation> {
    await delay(100);
    const conv = load().conversations.find((c) => c.id === id);
    if (!conv) throw new Error("Conversation not found");
    return conv;
  },
  async dashboard(): Promise<DashboardStats> {
    await delay(100);
    const state = load();
    const recentSends = state.conversations
      .flatMap((c) => c.events ?? [])
      .filter((e) => e.direction === "outbound")
      .sort((a, b) => b.created_at.localeCompare(a.created_at))
      .slice(0, 5);
    return {
      numbers_count: state.numbers.length,
      templates_count: state.templates.length,
      conversations_count: state.conversations.length,
      recent_sends: recentSends,
      recent_webhooks: state.conversations.slice(0, 3).map((c) => ({
        id: `wh-${c.id}`,
        object_type: "whatsapp_business_account",
        signature_valid: true,
        created_at: c.last_message_at,
      })),
    };
  },
};
