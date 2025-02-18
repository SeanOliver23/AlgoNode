from setuptools import setup, find_packages

setup(
    name="algorand-rewards-tracker",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=[
        'requests==2.31.0',
        'python-dotenv==1.0.0',
        'httpx>=0.23.0,<0.24.0',
        'supabase==1.0.3',
        'pandas==2.1.4',
        'plotly==5.18.0',
        'streamlit==1.29.0',
        'schedule==1.2.1',
        'python-dateutil>=2.8.2',
        'postgrest==0.10.6',
        'gotrue>=1.1.0,<2.0.0'
    ],
) 