-- Check the last hour of data
select 
    timestamp,
    rewards / 1e6 as rewards_algo,
    amount / 1e6 as balance_algo,
    current_round,
    is_online,
    participation_active,
    pending_rewards / 1e6 as pending_rewards_algo
from rewards_history
where timestamp > now() - interval '1 hour'
order by timestamp desc; 