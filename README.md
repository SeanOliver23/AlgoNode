# Algorand Rewards Tracker

Automated tracking of Algorand node participation rewards with data storage in Supabase.

## Features

- Hourly tracking of rewards and participation status
- Persistent storage in Supabase database
- Automated execution using GitHub Actions
- Detailed status reporting and verification

## Setup Instructions

1. Fork this repository to your GitHub account

2. Set up GitHub Secrets:
   - Go to your repository's Settings > Secrets and variables > Actions
   - Add the following secrets:
     - `SUPABASE_URL`: Your Supabase project URL
     - `SUPABASE_KEY`: Your Supabase anon key
     - `ALGO_ADDRESS`: Your Algorand node address

3. Enable GitHub Actions:
   - Go to the Actions tab in your repository
   - Enable workflows if they're disabled
   - The tracker will now run automatically every hour

## Local Development

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd algorand-rewards-tracker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials:
   ```
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
   ALGO_ADDRESS=your_algorand_address
   ```

5. Run the tracker:
   ```bash
   python rewards_tracker_service.py
   ```

## Data Structure

The rewards data is stored in a `rewards_history` table with the following columns:
- `timestamp`: When the data was collected
- `address`: Algorand node address
- `rewards`: Current rewards amount
- `rewards_base`: Rewards base value
- `amount`: Current account balance
- `cumulative_rewards`: Total rewards earned
- `is_online`: Node online status
- `current_round`: Current blockchain round
- `pending_rewards`: Pending rewards amount
- `participation_active`: Active participation status

## Monitoring

You can monitor your rewards data through:
1. Supabase Dashboard: View raw data and create visualizations
2. GitHub Actions: Check the workflow runs and logs
3. Local development: Run the script manually for testing

## Troubleshooting

If you encounter issues:
1. Check GitHub Actions logs for any errors
2. Verify your Supabase credentials are correct
3. Ensure your Algorand node address is valid
4. Check the Supabase database connectivity 