-- Drop existing tables if they exist
DROP TABLE IF EXISTS rewards_history CASCADE;
DROP TABLE IF EXISTS rewards CASCADE;
DROP TABLE IF EXISTS node_status CASCADE;
DROP VIEW IF EXISTS daily_rewards;

-- Create rewards history table
CREATE TABLE rewards_history (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    timestamp timestamptz NOT NULL,
    address text NOT NULL,
    rewards numeric NOT NULL,
    rewards_base bigint NOT NULL,
    amount numeric NOT NULL,
    cumulative_rewards numeric NOT NULL,
    is_online boolean NOT NULL,
    current_round bigint NOT NULL,
    pending_rewards numeric NOT NULL,
    participation_active boolean NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- Create rewards table
CREATE TABLE rewards (
    id BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    round BIGINT NOT NULL,
    amount DECIMAL(20, 6) NOT NULL,
    tx_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create node_status table
CREATE TABLE node_status (
    id BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    current_balance DECIMAL(20, 6) NOT NULL,
    is_online BOOLEAN NOT NULL,
    current_round BIGINT NOT NULL,
    participation_key_present BOOLEAN NOT NULL,
    time_remaining TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_rewards_history_address_timestamp ON rewards_history(address, timestamp);
CREATE INDEX idx_rewards_address ON rewards(address);
CREATE INDEX idx_rewards_timestamp ON rewards(timestamp);
CREATE INDEX idx_rewards_tx_id ON rewards(tx_id);
CREATE INDEX idx_node_status_address ON node_status(address);
CREATE INDEX idx_node_status_timestamp ON node_status(timestamp);

-- Create view for daily rewards
CREATE VIEW daily_rewards AS
SELECT 
    address,
    DATE_TRUNC('day', timestamp) as date,
    COUNT(*) as num_rewards,
    SUM(amount) as total_rewards,
    AVG(amount) as avg_reward
FROM rewards
GROUP BY address, DATE_TRUNC('day', timestamp)
ORDER BY date DESC;

-- Enable Row Level Security
ALTER TABLE rewards_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE rewards ENABLE ROW LEVEL SECURITY;
ALTER TABLE node_status ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DO $$ 
BEGIN
    -- Drop policies for rewards_history
    DROP POLICY IF EXISTS "Allow all operations" ON rewards_history;
    DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON rewards_history;
    DROP POLICY IF EXISTS "Enable select for all users" ON rewards_history;
    
    -- Drop policies for rewards
    DROP POLICY IF EXISTS "Allow all operations" ON rewards;
    DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON rewards;
    DROP POLICY IF EXISTS "Enable select for all users" ON rewards;
    
    -- Drop policies for node_status
    DROP POLICY IF EXISTS "Allow all operations" ON node_status;
    DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON node_status;
    DROP POLICY IF EXISTS "Enable select for all users" ON node_status;
EXCEPTION
    WHEN undefined_object THEN
        NULL;
END $$;

-- Create new policies
CREATE POLICY "Allow all operations on rewards_history"
ON rewards_history FOR ALL
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow all operations on rewards"
ON rewards FOR ALL
USING (true)
WITH CHECK (true);

CREATE POLICY "Allow all operations on node_status"
ON node_status FOR ALL
USING (true)
WITH CHECK (true); 