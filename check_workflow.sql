-- Check most recent rewards_history entries
SELECT 
    timestamp,
    rewards,
    cumulative_rewards,
    is_online,
    participation_active
FROM rewards_history
ORDER BY timestamp DESC
LIMIT 5;

-- Check most recent node_status entries
SELECT 
    timestamp,
    current_balance,
    is_online,
    current_round,
    time_remaining
FROM node_status
ORDER BY timestamp DESC
LIMIT 5;

-- Check most recent rewards entries
SELECT 
    timestamp,
    round,
    amount,
    tx_id
FROM rewards
ORDER BY timestamp DESC
LIMIT 5; 