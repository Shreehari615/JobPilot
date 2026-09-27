import os

# Set testing database URL before app imports
os.environ["DATABASE_URL"] = "sqlite:///./test_jobpilot.db"
os.environ["SEED_DEMO_DATA"] = "false"
