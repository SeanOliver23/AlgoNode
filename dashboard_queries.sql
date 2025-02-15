-- 1. Node Status Timeline
select 
    timestamp,
    amount / 1e6 as balance_algo,
    current_round,
    case 
        when is_online and participation_active then 'Participating'
        when is_online then 'Online Only'
        else 'Offline'
    end as node_status
from rewards_history
where address = 'KK4KTUPTKX3YNA5G2HMYO4CD63F6MTKXDJLIOJ5RRT7TRQK6HC25NUGZTY'
order by timestamp asc;

-- 2. Round Progress
select 
    timestamp,
    current_round,
    current_round - lag(current_round) over (order by timestamp) as blocks_produced
from rewards_history
where address = 'KK4KTUPTKX3YNA5G2HMYO4CD63F6MTKXDJLIOJ5RRT7TRQK6HC25NUGZTY'
order by timestamp asc;

-- 3. Participation Stats
select 
    count(*) as total_checks,
    sum(case when is_online then 1 else 0 end)::float / count(*) * 100 as online_percentage,
    sum(case when participation_active then 1 else 0 end)::float / count(*) * 100 as participation_percentage,
    min(current_round) as start_round,
    max(current_round) as latest_round,
    max(current_round) - min(current_round) as rounds_elapsed
from rewards_history
where address = 'KK4KTUPTKX3YNA5G2HMYO4CD63F6MTKXDJLIOJ5RRT7TRQK6HC25NUGZTY'; 