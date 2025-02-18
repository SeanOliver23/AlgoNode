import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import os
from pathlib import Path

class AlgorandRewardsTracker:
    def __init__(self, address: str, start_date: datetime = datetime(2025, 2, 15)):
        """Initialize the rewards tracker with an Algorand address."""
        self.address = address
        self.start_date = start_date
        self.algod_url = "https://mainnet-api.algonode.cloud"
        self.indexer_url = "https://mainnet-idx.algonode.cloud"
        self.data_file = Path('rewards_data.json')
        
    def get_account_info(self) -> Dict:
        """Fetch current account information from Algonode."""
        try:
            response = requests.get(f"{self.algod_url}/v2/accounts/{self.address}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching account info: {e}")
            return {}

    def get_node_status(self) -> Dict:
        """Get current node status from network."""
        try:
            response = requests.get(f"{self.algod_url}/v2/status")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching node status: {e}")
            return {}

    def load_historical_data(self) -> list:
        """Load historical rewards data from file."""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Convert timestamp strings back to datetime objects
                for entry in data:
                    entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
                return data
        return []

    def save_historical_data(self, data: list):
        """Save rewards data to file."""
        # Convert datetime objects to strings for JSON serialization
        serializable_data = []
        for entry in data:
            entry_copy = entry.copy()
            if isinstance(entry['timestamp'], datetime):
                entry_copy['timestamp'] = entry['timestamp'].isoformat()
            serializable_data.append(entry_copy)
            
        with open(self.data_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)

    def track_rewards(self) -> Dict:
        """Track and record current rewards state."""
        account_info = self.get_account_info()
        if not account_info:
            return {}

        # Extract relevant data
        current_data = {
            'timestamp': datetime.now(),
            'rewards': account_info.get('rewards', 0),  # Keep in microAlgos for precision
            'pending_rewards': account_info.get('pending-rewards', 0),
            'total_balance': account_info.get('amount', 0) / 1e6,  # Convert to Algo
            'status': account_info.get('status', 'Offline'),
            'rewards_base': account_info.get('rewards-base', 0),
        }

        # Load and update historical data
        historical_data = self.load_historical_data()
        
        # Only add new data point if it's been at least 1 hour since last update
        if not historical_data or (
            current_data['timestamp'] - historical_data[-1]['timestamp']
            > timedelta(hours=1)
        ):
            historical_data.append(current_data)
            self.save_historical_data(historical_data)

        return current_data

    def get_rewards_from_indexer(self) -> float:
        """Get rewards information from indexer API by looking for ProposerPayout transactions."""
        try:
            # Query transactions since start date
            start_time = self.start_date.strftime("%Y-%m-%d")
            url = f"{self.indexer_url}/v2/accounts/{self.address}/transactions"
            params = {
                'after-time': start_time,
                'limit': 1000,  # Get maximum transactions
                'note-prefix': 'UHJvcG9zZXJQYXlvdXQ='  # Base64 encoded "ProposerPayout"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            total_rewards = 0
            transactions = data.get('transactions', [])
            
            # Sum up all ProposerPayout transactions
            for tx in transactions:
                if tx.get('payment-transaction'):
                    amount = tx['payment-transaction'].get('amount', 0)
                    total_rewards += amount
            
            return total_rewards / 1e6  # Convert to Algo
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching indexer data: {e}")
            return 0

    def calculate_rewards_metrics(self) -> Dict:
        """Calculate rewards metrics since start date."""
        # Get rewards from indexer
        total_rewards = self.get_rewards_from_indexer()
        
        # Calculate days running
        days_running = (datetime.now() - self.start_date).days
        
        # Calculate daily average
        rewards_per_day = total_rewards / max(days_running, 1)  # Avoid division by zero
        
        return {
            'total_rewards': total_rewards,
            'rewards_per_day': rewards_per_day,
            'days_running': days_running
        }

    def get_participation_status(self) -> Dict:
        """Get current participation status."""
        account_info = self.get_account_info()
        node_status = self.get_node_status()
        
        participation = account_info.get('participation', {})
        current_round = node_status.get('last-round', 0)
        
        vote_first_valid = participation.get('vote-first-valid')
        vote_last_valid = participation.get('vote-last-valid')
        
        status = {
            'online': account_info.get('status') == 'Online',
            'current_round': current_round,
            'participation_key_present': bool(participation),
            'vote_first_valid': vote_first_valid,
            'vote_last_valid': vote_last_valid,
            'vote_key_dilution': participation.get('vote-key-dilution'),
            'participation_active': False  # Default value
        }
        
        # Calculate participation active status
        if vote_first_valid and vote_last_valid:
            status['participation_active'] = (
                vote_first_valid <= current_round <= vote_last_valid and
                status['online'] and
                status['participation_key_present']
            )
            status['blocks_remaining'] = max(0, vote_last_valid - current_round)
            status['time_remaining'] = str(timedelta(seconds=status['blocks_remaining'] * 4.5))
        else:
            status['blocks_remaining'] = 0
            status['time_remaining'] = "No participation keys found"
            
        return status

    def print_report(self):
        """Print a simple report of current rewards and participation status."""
        current_data = self.track_rewards()
        participation_status = self.get_participation_status()
        rewards_metrics = self.calculate_rewards_metrics()
        
        print("\nAlgorand Rewards Report")
        print("=" * 50)
        print(f"Address: {self.address}")
        print(f"Node Start Date: {self.start_date.strftime('%Y-%m-%d')}")
        print(f"Days Running: {rewards_metrics['days_running']}")
        
        print(f"\nRewards Status:")
        print(f"Total Rewards Since Start: {rewards_metrics['total_rewards']:.6f} ALGO")
        print(f"Average Daily Rewards: {rewards_metrics['rewards_per_day']:.6f} ALGO")
        if rewards_metrics['days_running'] > 0:
            print(f"Projected Monthly Rewards: {rewards_metrics['rewards_per_day'] * 30:.6f} ALGO")
        
        print(f"\nParticipation Status:")
        print(f"Online: {'Yes' if participation_status['online'] else 'No'}")
        print(f"Current Round: {participation_status['current_round']:,}")
        print(f"Participation Keys: {'Present' if participation_status['participation_key_present'] else 'Not Found'}")
        print(f"Time Remaining: {participation_status['time_remaining']}")

        # Debug information
        print("\nDebug Information:")
        try:
            # Get ProposerPayout transactions for debugging
            url = f"{self.indexer_url}/v2/accounts/{self.address}/transactions"
            params = {
                'after-time': self.start_date.strftime("%Y-%m-%d"),
                'limit': 1000,
                'note-prefix': 'UHJvcG9zZXJQYXlvdXQ='
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            transactions = data.get('transactions', [])
            print(f"\nFound {len(transactions)} ProposerPayout transactions:")
            
            for tx in transactions:
                if tx.get('payment-transaction'):
                    amount = tx['payment-transaction'].get('amount', 0) / 1e6
                    round_num = tx.get('confirmed-round', 0)
                    timestamp = tx.get('round-time', 0)
                    date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Round {round_num}: {amount:.6f} ALGO ({date})")
                    
        except Exception as e:
            print(f"Error fetching debug data: {e}")

def main():
    # Algorand address to track
    address = "KK4KTUPTKX3YNA5G2HMYO4CD63F6MTKXDJLIOJ5RRT7TRQK6HC25NUGZTY"
    start_date = datetime(2025, 2, 15)  # Set specific start date
    
    tracker = AlgorandRewardsTracker(address, start_date)
    tracker.print_report()

if __name__ == "__main__":
    main() 