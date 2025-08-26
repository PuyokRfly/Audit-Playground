-- Supabase SQL Schema for Audit Submissions and Results

-- Enable pgcrypto extension for gen_random_uuid()
create extension if not exists pgcrypto;

-- 1. audit_submissions table
-- Create an ENUM type for the status column for better data integrity
create type submission_status as enum ('pending', 'running', 'done', 'failed');

create table if not exists audit_submissions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id),
  contract_code text,
  status submission_status default 'pending',
  created_at timestamptz default now()
);

comment on table audit_submissions is 'Stores contract audit submissions from users.';
comment on column audit_submissions.user_id is 'Foreign key to the user who submitted the audit.';
comment on column audit_submissions.status is 'The current status of the audit submission.';

-- 2. audit_results table
create table if not exists audit_results (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid not null references audit_submissions(id) on delete cascade,
  raw_slither_json jsonb,
  risk_score numeric(5,2),
  summary_report text,
  created_at timestamptz default now()
);

comment on table audit_results is 'Stores the results of contract audits.';
comment on column audit_results.submission_id is 'Links to the corresponding submission.';
comment on column audit_results.raw_slither_json is 'Raw JSON output from the Slither analysis tool.';
comment on column audit_results.risk_score is 'A calculated risk score from 0.00 to 100.00.';

-- 3. Indexes
-- Create an index on submission_id for faster lookups of results for a given submission.
create index if not exists idx_audit_results_submission_id on audit_results(submission_id);

-- 4. Granting permissions
-- Grant usage on the schema to the authenticated role
grant usage on schema public to authenticated;
-- Grant all privileges on the new tables to the authenticated role
alter table audit_submissions owner to postgres;
alter table audit_results owner to postgres;
grant select, insert, update, delete on table audit_submissions to authenticated;
grant select, insert, update, delete on table audit_results to authenticated;
grant all on table audit_submissions to service_role;
grant all on table audit_results to service_role;


-- 5. Example INSERT statements for testing
-- Note: To run these inserts, you must have a user in the `auth.users` table.
-- Supabase automatically creates a user entry upon sign-up.
-- The following is a placeholder for a real user UUID.
-- Replace '00000000-0000-0000-0000-000000000001' with a valid user_id from your auth.users table.

-- To make this script runnable for testing, we can insert a dummy user.
-- In a real scenario, the user would exist from Supabase Auth.
insert into auth.users (id, aud, role, email, encrypted_password, email_confirmed_at, recovery_sent_at, last_sign_in_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at, confirmation_token, email_change, email_change_sent_at, confirmed_at)
values
  ('00000000-0000-0000-0000-000000000001', 'authenticated', 'authenticated', 'test@example.com', 'dummy_password', now(), null, null, '{"provider":"email","providers":["email"]}', '{}', now(), now(), '', '', null, now())
on conflict (id) do nothing;


-- Insert a sample submission
insert into audit_submissions (user_id, contract_code, status)
values ('00000000-0000-0000-0000-000000000001', 'contract HelloWorld {}', 'done');

-- Get the ID of the last submission to use in the results table
-- (This is a bit tricky in a static script, so we'll just assume we know the submission_id
-- or use a hardcoded one for the example. In an application, you'd get this programmatically.)

-- Insert a sample result for the submission
-- Note: You would need to retrieve the actual submission_id created above.
-- For this example, we will assume the application logic would handle this.
-- For a self-contained script, we can't easily get the UUID from the previous insert.
-- A more advanced script could use plpgsql for this.
insert into audit_results (submission_id, raw_slither_json, risk_score, summary_report)
select id, '{"results": "none"}', 5.50, 'This is a summary report.'
from audit_submissions where contract_code = 'contract HelloWorld {}';
