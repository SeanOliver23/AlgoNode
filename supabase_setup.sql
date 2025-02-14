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

-- Create policy to allow inserts from authenticated users
create policy "Enable insert for authenticated users only"
on rewards_history for insert
to authenticated
with check (true);

-- Create policy to allow select for all users
create policy "Enable select for all users"
on rewards_history for select
to anon
using (true); 