-- Create rewards history table
create table if not exists rewards_history (
    id bigint primary key generated always as identity,
    timestamp timestamptz not null,
    address text not null,
    rewards numeric not null,
    rewards_base bigint not null,
    amount numeric not null,
    cumulative_rewards numeric not null,
    is_online boolean not null,
    current_round bigint not null,
    pending_rewards numeric not null,
    participation_active boolean not null,
    created_at timestamptz default now()
);

-- Create index for faster queries
create index if not exists rewards_history_address_timestamp_idx 
on rewards_history(address, timestamp);

-- Enable Row Level Security
alter table rewards_history enable row level security;

-- Drop existing policies
drop policy if exists "Enable insert for authenticated users only" on rewards_history;
drop policy if exists "Enable insert for service role" on rewards_history;
drop policy if exists "Enable select for all users" on rewards_history;

-- Create a single policy to allow all operations (for testing)
create policy "Allow all operations"
on rewards_history
for all
using (true)
with check (true); 