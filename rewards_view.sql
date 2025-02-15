-- Create a view for rewards over time
create or replace view rewards_over_time as
select 
    date_trunc('hour', timestamp) as time_period,
    address,
    rewards / 1e6 as rewards_algo,
    cumulative_rewards / 1e6 as cumulative_rewards_algo,
    amount / 1e6 as balance_algo,
    is_online,
    participation_active,
    current_round
from rewards_history
order by timestamp desc;

-- Create a view for daily rewards summary
create or replace view daily_rewards_summary as
select 
    date_trunc('day', timestamp) as day,
    address,
    max(rewards / 1e6) - min(rewards / 1e6) as rewards_earned_today,
    max(cumulative_rewards / 1e6) as total_rewards,
    avg(amount / 1e6) as average_balance,
    bool_and(is_online) as consistently_online,
    bool_and(participation_active) as consistently_participating,
    count(*) as num_checks
from rewards_history
group by date_trunc('day', timestamp), address
order by day desc; 