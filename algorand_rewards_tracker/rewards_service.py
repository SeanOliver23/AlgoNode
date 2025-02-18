import os
from datetime import datetime, timedelta
import time
import schedule
from supabase import create_client, Client
from dotenv import load_dotenv
from algo_rewards import AlgorandRewardsTracker
import requests

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase credentials")

try:
    supabase: Client = create_client(
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    print("Supabase client initialized successfully")
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    raise

class RewardsService:
    def __init__(self):
        self.address = "KK4KTUPTKX3YNA5G2HMYO4CD63F6MTKXDJLIOJ5RRT7TRQK6HC25NUGZTY"
        self.start_date = datetime(2025, 2, 15)
        self.original_balance = 145726.37  # Set the original balance
        self.tracker = AlgorandRewardsTracker(self.address, self.start_date)

    def update_rewards_data(self):
        """Collect rewards data and update Supabase."""
        try:
            print(f"Starting rewards update at {datetime.now()}")
            print(f"Using address: {self.address}")
            print(f"Supabase connection: {'OK' if supabase else 'Failed'}")
            
            # Get current data
            url = f"{self.tracker.indexer_url}/v2/accounts/{self.address}/transactions"
            params = {
                'after-time': self.start_date.strftime("%Y-%m-%d"),
                'limit': 1000,
                'note-prefix': 'UHJvcG9zZXJQYXlvdXQ='
            }
            
            # Get account info
            print("Fetching account info...")
            account_info = self.tracker.get_account_info()
            rewards = account_info.get('rewards', 0)
            rewards_base = account_info.get('rewards-base', 0)
            pending_rewards = account_info.get('pending-rewards', 0)
            
            # Get participation status
            print("Checking participation status...")
            participation_status = self.tracker.get_participation_status()
            
            # Get rewards transactions
            print("Fetching rewards transactions...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Calculate cumulative rewards
            total_rewards = sum(
                tx['payment-transaction'].get('amount', 0) / 1e6
                for tx in data.get('transactions', [])
                if tx.get('payment-transaction')
            )
            print(f"Found total rewards: {total_rewards:.6f} ALGO")
            
            # Calculate current balance as original balance plus total rewards
            current_balance = self.original_balance + total_rewards
            print(f"Current balance: {current_balance:.6f} ALGO")
            
            # Store rewards history
            print("Updating rewards history...")
            history_data = {
                'timestamp': datetime.now().isoformat(),
                'address': self.address,
                'rewards': rewards / 1e6,  # Convert to ALGO
                'rewards_base': rewards_base,
                'amount': current_balance,  # Updated current balance
                'cumulative_rewards': total_rewards,
                'is_online': participation_status['online'],
                'current_round': participation_status['current_round'],
                'pending_rewards': pending_rewards / 1e6,  # Convert to ALGO
                'participation_active': participation_status.get('participation_active', False)
            }
            
            # Update rewards_history table
            result = supabase.table('rewards_history').insert(history_data).execute()
            print(f"Rewards history updated: {len(result.data) if result.data else 0} rows affected")
            
            # Store node status with correct current balance
            print("Updating node status...")
            node_status = {
                'timestamp': datetime.now().isoformat(),
                'address': self.address,
                'current_balance': current_balance,  # Updated current balance
                'is_online': participation_status['online'],
                'current_round': participation_status['current_round'],
                'participation_key_present': participation_status['participation_key_present'],
                'time_remaining': participation_status['time_remaining']
            }
            
            # Update node_status table
            result = supabase.table('node_status').upsert(node_status).execute()
            print(f"Node status updated: {len(result.data) if result.data else 0} rows affected")
            
            # Get and store rewards transactions
            print("Processing individual rewards transactions...")
            transactions = data.get('transactions', [])
            tx_count = 0
            
            for tx in transactions:
                if tx.get('payment-transaction'):
                    reward_data = {
                        'address': self.address,
                        'timestamp': datetime.fromtimestamp(tx.get('round-time', 0)).isoformat(),
                        'round': tx.get('confirmed-round', 0),
                        'amount': tx['payment-transaction'].get('amount', 0) / 1e6,
                        'tx_id': tx.get('id')
                    }
                    
                    # Update rewards table
                    result = supabase.table('rewards').upsert(reward_data, on_conflict='tx_id').execute()
                    if result.data:
                        tx_count += 1
            
            print(f"Processed {tx_count} reward transactions")
            print(f"Data updated successfully at {datetime.now()}")
            
        except Exception as e:
            print(f"Error updating data: {e}")
            raise  # Re-raise the exception to ensure GitHub Actions marks the run as failed

    def run_scheduler(self):
        """Run the scheduler to update data periodically."""
        # Update immediately on start
        self.update_rewards_data()
        
        # Schedule updates every hour
        schedule.every(1).hours.do(self.update_rewards_data)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    service = RewardsService()
    service.run_scheduler()

if __name__ == "__main__":
    main() 