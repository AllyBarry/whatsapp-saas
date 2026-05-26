export type Role = "owner" | "admin" | "viewer";
export type Plan = "free" | "starter" | "business" | "enterprise";

export interface User {
  id: string;
  tenant_id: string;
  email: string;
  role: Role;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResult {
  token: TokenResponse;
  user: User;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  status: string;
  subscription_plan: Plan;
  created_at: string;
}

export interface PlanLimits {
  numbers: number;
  templates: number;
}

export interface Subscription {
  plan: Plan;
  limits: PlanLimits;
  numbers_used: number;
  templates_used: number;
}

export interface PlanInfo {
  plan: Plan;
  limits: PlanLimits;
}

export interface Credential {
  id: string;
  tenant_id: string;
  waba_id: string;
  phone_number_id: string;
  verify_token: string;
  has_access_token: boolean;
  has_app_secret: boolean;
  created_at: string;
}

export interface WhatsAppNumber {
  id: string;
  phone_number_id: string;
  display_phone_number: string | null;
  verified_name: string | null;
  quality_rating: string | null;
  status: string | null;
  messaging_limit: string | null;
  created_at: string;
}

export interface Template {
  id: string;
  meta_template_id: string | null;
  name: string;
  language: string;
  category: string | null;
  status: string | null;
  template_json: Record<string, unknown>;
  created_at: string;
}

export type TemplateCategory = "MARKETING" | "UTILITY" | "AUTHENTICATION";

export interface TemplateComponent {
  type: "HEADER" | "BODY" | "FOOTER" | "BUTTONS";
  format?: string;
  text?: string;
  example?: { body_text?: string[][]; header_text?: string[] };
  buttons?: Array<Record<string, unknown>>;
}

export interface TemplateCreateBody {
  name: string;
  language: string;
  category: TemplateCategory;
  components: TemplateComponent[];
  submit_to_meta: boolean;
}

export interface ConversationEvent {
  id: string;
  event_type: string;
  direction: "inbound" | "outbound" | "system";
  payload: Record<string, unknown>;
  created_at: string;
}

export interface Conversation {
  id: string;
  customer_number: string;
  started_at: string;
  last_message_at: string;
  status: string;
  events?: ConversationEvent[];
}

export interface DashboardStats {
  numbers_count: number;
  templates_count: number;
  conversations_count: number;
  recent_sends: ConversationEvent[];
  recent_webhooks: Array<Record<string, unknown>>;
}
