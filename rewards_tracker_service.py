import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any
import requests
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RewardsTracker:
    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Get Algorand address
        self.address = os.getenv('ALGO_ADDRESS')
        if not self.address:
            raise ValueError("Algorand address not found in environment variables")
        
        # Use public Algorand nodes
        self.algod_url = "https://mainnet-api.algonode.cloud"
        self.indexer_url = "https://mainnet-idx.algonode.cloud"
        
    def fetch_account_info(self) -> Dict[str, Any]:
        """Fetch account information from local node"""
        try:
            response = requests.get(
                f"{self.algod_url}/v2/accounts/{self.address}",
                headers={"X-Algo-API-Token": ""}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching account info: {str(e)}")
            return {}

    def check_participation_status(self) -> Dict[str, Any]:
        """Check participation status of the node"""
        try:
            # Get node status
            status_response = requests.get(
                f"{self.algod_url}/v2/status",
                headers={"X-Algo-API-Token": ""}
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            
            # Get account participation info
            account_info = self.fetch_account_info()
            
            return {
                "is_online": "participation" in account_info,
                "current_round": status_data.get("last-round", 0),
                "participation_active": bool(account_info.get("participation", {}).get("selection-participation-key")),
                "pending_rewards": account_info.get("pending-rewards", 0)
            }
        except Exception as e:
            logger.error(f"Error checking participation status: {str(e)}")
            return {
                "is_online": False,
                "current_round": 0,
                "participation_active": False,
                "pending_rewards": 0
            }

    def process_rewards(self) -> Dict[str, Any]:
        """Process and store rewards data"""
        try:
            account_info = self.fetch_account_info()
            participation_status = self.check_participation_status()
            
            if not account_info:
                raise ValueError("Failed to fetch account information")
            
            # Prepare data for storage
            timestamp = datetime.now(timezone.utc)
            data = {
                "timestamp": timestamp.isoformat(),
                "address": self.address,
                "rewards": account_info.get("rewards", 0),
                "rewards_base": account_info.get("rewards-base", 0),
                "amount": account_info.get("amount", 0),
                "cumulative_rewards": account_info.get("rewards-total", 0),
                **participation_status
            }
            
            # Store in Supabase
            self.supabase.table("rewards_history").insert(data).execute()
            logger.info("Successfully stored rewards data")
            
            return data
            
        except Exception as e:
            logger.error(f"Error processing rewards: {str(e)}")
            return {}

def main():
    try:
        tracker = RewardsTracker()
        data = tracker.process_rewards()
        
        if data:
            logger.info(f"Successfully tracked rewards: {json.dumps(data, indent=2)}")
        else:
            logger.error("Failed to track rewards")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main() 