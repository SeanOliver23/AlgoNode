-- Simple rewards tracking visualization
select 
    timestamp,
    rewards / 1e6 as rewards_algo,
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