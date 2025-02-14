import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List
import os
import json

class AlgoRewardTracker:
    def __init__(self, address: str):
        self.address = address
        self.indexer_url = "https://mainnet-idx.algonode.cloud/v2"
        self.algod_url = "https://mainnet-api.algonode.cloud"
        self.rewards_data: List[Dict] = []
        self.history_file = 'rewards_history.json'
        print(f"Initialized tracker for address: {address}")
        
    def load_history(self):
        """Load historical rewards data from file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                # Convert string dates back to datetime
                for entry in history:
                    entry['datetime'] = datetime.fromisoformat(entry['datetime'])
                return history
        return []

    def save_history(self, data):
        """Save rewards data to history file."""
        # Convert datetime to string for JSON serialization
        serializable_data = []
        for entry in data:
            entry_copy = entry.copy()
            entry_copy['datetime'] = entry_copy['datetime'].isoformat()
            serializable_data.append(entry_copy)
            
        with open(self.history_file, 'w') as f:
            json.dump(serializable_data, f)
        
    def fetch_account_info(self) -> Dict:
        """Fetch current account information."""
        print("Fetching account information...")
        url = f"{self.algod_url}/v2/accounts/{self.address}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            raise Exception(f"Error fetching data: {response.text}")
        
        data = response.json()
        print(f"Account data retrieved successfully")
        print(f"Raw account data: {data}")  # Debug print
        return data
    
    def process_rewards(self):
        """Process and organize rewards data."""
        print("Processing rewards data...")
        account_data = self.fetch_account_info()
        
        # Get rewards information
        rewards = account_data.get('rewards', 0)
        rewards_base = account_data.get('rewards-base', 0)
        amount = account_data.get('amount', 0)
        
        # Create new data point
        current_data = {
            'datetime': datetime.now(),
            'rewards': rewards,
            'rewards_base': rewards_base,
            'amount': amount / 1e6,  # Convert microAlgos to Algos
            'cumulative_rewards': rewards / 1e6  # Convert microAlgos to Algos
        }
        
        # Load historical data
        history = self.load_history()
        
        # Add new data point if it's been at least 1 hour since last update
        if not history or (current_data['datetime'] - history[-1]['datetime']) > timedelta(hours=1):
            history.append(current_data)
            self.save_history(history)
        
        # Convert to DataFrame
        self.rewards_data = pd.DataFrame(history)
        print(f"Processed rewards data: {self.rewards_data.to_dict('records')}")
        return self.rewards_data
    
    def display_rewards(self, save_path='algo_rewards_report.png'):
        """Display rewards information interactively and save to file."""
        if self.rewards_data.empty:
            print("No rewards data to display")
            return
            
        # Create a figure with three subplots, taller for better visibility
        plt.style.use('default')
        fig = plt.figure(figsize=(15, 16), facecolor='white')
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 2, 1], hspace=0.4)
        
        # Plot 1: Account Balance and Rewards (Bar Chart)
        ax1 = fig.add_subplot(gs[0])
        data = [
            self.rewards_data['amount'].iloc[-1],
            self.rewards_data['cumulative_rewards'].iloc[-1]
        ]
        labels = ['Account Balance', 'Total Rewards']
        colors = ['#2ecc71', '#3498db']
        
        bars = ax1.bar(labels, data, color=colors)
        ax1.set_title('Current Account Balance and Rewards (ALGO)', pad=20)
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on the bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.6f}',
                    ha='center', va='bottom')
        
        # Plot 2: Rewards Over Time (Line Chart)
        ax2 = fig.add_subplot(gs[1])
        ax2.plot(self.rewards_data['datetime'], 
                self.rewards_data['cumulative_rewards'],
                color='#3498db',
                marker='o',
                linewidth=2,
                markersize=8)
        ax2.set_title('Rewards Over Time', pad=20)
        ax2.set_xlabel('Date', labelpad=10)
        ax2.set_ylabel('Cumulative Rewards (ALGO)', labelpad=10)
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Plot 3: Rewards Information (Text)
        ax3 = fig.add_subplot(gs[2])
        rewards_info = f"""
        Rewards Information:
        -------------------
        Total Rewards: {self.rewards_data['cumulative_rewards'].iloc[-1]:,.6f} ALGO
        Rewards Base: {self.rewards_data['rewards_base'].iloc[-1]:,}
        Last Updated: {self.rewards_data['datetime'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')}
        First Tracked: {self.rewards_data['datetime'].iloc[0].strftime('%Y-%m-%d %H:%M:%S')}
        Tracking Period: {(self.rewards_data['datetime'].iloc[-1] - self.rewards_data['datetime'].iloc[0]).days} days
        
        Account Information:
        ------------------
        Current Balance: {self.rewards_data['amount'].iloc[-1]:,.6f} ALGO
        """
        
        ax3.text(0.05, 0.95, rewards_info,
                transform=ax3.transAxes,
                fontsize=12,
                verticalalignment='top',
                family='monospace')
        ax3.axis('off')
        
        plt.suptitle(f'Algorand Account Overview\n{self.address}', fontsize=14, y=0.98)
        plt.tight_layout()
        
        # Save the figure
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nReport saved to: {save_path}")
        
        # Display the figure
        plt.show()

    def check_participation_status(self) -> Dict:
        """Check detailed participation status of the account."""
        account_data = self.fetch_account_info()
        
        # Get current round from algod
        status_url = f"{self.algod_url}/v2/status"
        status_response = requests.get(status_url)
        current_round = status_response.json().get('last-round', 0)
        
        participation = account_data.get('participation', {})
        status = {
            'is_online': account_data.get('status') == 'Online',
            'current_round': current_round,
            'vote_first_valid': participation.get('vote-first-valid'),
            'vote_last_valid': participation.get('vote-last-valid'),
            'vote_key_dilution': participation.get('vote-key-dilution'),
            'has_participation_keys': bool(participation),
            'pending_rewards': account_data.get('pending-rewards', 0) / 1e6,
            'reward_base': account_data.get('reward-base', 0),
            'total_rewards': account_data.get('rewards', 0) / 1e6,
            'amount': account_data.get('amount', 0) / 1e6,
            'min_balance': account_data.get('min-balance', 0) / 1e6
        }
        
        # Calculate additional status information
        if status['vote_first_valid'] and status['vote_last_valid']:
            status['participation_active'] = (
                status['vote_first_valid'] <= current_round <= status['vote_last_valid']
            )
            status['blocks_remaining'] = max(0, status['vote_last_valid'] - current_round)
            status['participation_time_remaining'] = timedelta(seconds=status['blocks_remaining'] * 4.5)  # ~4.5 seconds per block
        else:
            status['participation_active'] = False
            status['blocks_remaining'] = 0
            status['participation_time_remaining'] = timedelta(0)
            
        return status

    def display_participation_status(self):
        """Display detailed participation status."""
        status = self.check_participation_status()
        
        status_text = f"""
Algorand Node Participation Status
================================
Address: {self.address}

Node Status:
-----------
Online: {'✅' if status['is_online'] else '❌'}
Current Round: {status['current_round']:,}

Participation Keys:
-----------------
Has Keys: {'✅' if status['has_participation_keys'] else '❌'}
Active: {'✅' if status.get('participation_active') else '❌'}
First Valid Round: {status['vote_first_valid']:,}
Last Valid Round: {status['vote_last_valid']:,}
Blocks Remaining: {status['blocks_remaining']:,}
Time Remaining: {status['participation_time_remaining']}

Rewards Information:
------------------
Total Rewards: {status['total_rewards']:,.6f} ALGO
Pending Rewards: {status['pending_rewards']:,.6f} ALGO
Reward Base: {status['reward_base']:,}

Account Information:
------------------
Current Balance: {status['amount']:,.6f} ALGO
Minimum Balance: {status['min_balance']:,.6f} ALGO
"""
        print(status_text)
        return status

def main():
    # Your Algorand address
    address = "KK4KTUPTKX3YNA5G2HMYO4CD63F6MTKXDJLIOJ5RRT7TRQK6HC25NUGZTY"
    
    print("\nStarting Algorand Rewards Tracker...")
    tracker = AlgoRewardTracker(address)
    
    print("\nChecking participation status...")
    tracker.display_participation_status()
    
    print("\nFetching rewards data...")
    tracker.process_rewards()
    
    print("\nDisplaying rewards information...")
    tracker.display_rewards()

if __name__ == "__main__":
    main() 