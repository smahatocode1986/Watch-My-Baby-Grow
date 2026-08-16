-- Run this once in Supabase Dashboard > SQL Editor.
create table if not exists public.app_state (
    id text primary key,
    payload jsonb not null default '{}'::jsonb,
    updated_at timestamptz not null default now()
);

-- No public policies are created. The Streamlit server connects with a secret
-- key, which must remain only in .env or Streamlit Community Cloud secrets.
alter table public.app_state enable row level security;

revoke all on table public.app_state from anon, authenticated;
grant all on table public.app_state to service_role;
