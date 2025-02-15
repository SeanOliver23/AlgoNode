-- Check raw data in rewards_history
select 
    timestamp,
    address,
    rewards / 1e6 as rewards_algo,
    amount / 1e6 as balance_algo,
    is_online,
    participation_active,
    current_round
from rewards_history
order by timestamp desc
limit 10; 