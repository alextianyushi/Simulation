# main.py

# Import functions and classes from latency.py
from latency import cost_time, prob_latency

# Import classes and functions from tendermint.py
from tendermint import TendermintParams, tendermint_simulation

# Import Validator class from validator.py
from validator import Validator

import random

def main():
    # Initialize validators
    num_validators = 100
    validators = [Validator(i) for i in range(num_validators)]

    # Define Tendermint parameters
    params = TendermintParams(
        proposal_size=10,  # MB
        vote_size=1,  # MB
        proposal_generation_rate=10,  # MB/s
        bandwidth=100,  # MB/s
        proposal_verification_rate=5,  # MB/s
        std_dev_generation=1.0,  # Standard deviation for proposal generation
        std_dev_verification=0.5,  # Standard deviation for proposal verification
        std_dev_broadcast=0.2,  # Standard deviation for broadcasting
        latency=50  # ms
    )

    # Run Tendermint simulation
    rounds = 10
    proposed_values = ['A', 'B', 'C', 'D']
    consensus_times = tendermint_simulation(validators, rounds, proposed_values, params)

    # Output results
    for i, consensus_time in enumerate(consensus_times):
        print(f"Round {i + 1}: Consensus reached in {consensus_time:.2f} seconds")

if __name__ == "__main__":
    main()
