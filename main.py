from strategies.example_strategy import run_strategy
from execution.example_executor import execute_trade
from dashboard.example_dashboard import show_dashboard
from utils.helpers import log_message

def main():
    log_message('MMM System Starting...')
    run_strategy()
    execute_trade()
    show_dashboard()
    log_message('MMM System Finished.')

if __name__ == '__main__':
    main()
