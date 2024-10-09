import random
from latency import cost_time, prob_latency

class TendermintParams:
    def __init__(self, proposal_size, vote_size, proposal_generation_rate, bandwidth, 
                 proposal_verification_rate, std_dev_generation, std_dev_verification, 
                 std_dev_broadcast, latency):
        self.proposal_size = proposal_size
        self.vote_size = vote_size
        self.proposal_generation_rate = proposal_generation_rate
        self.bandwidth = bandwidth
        self.proposal_verification_rate = proposal_verification_rate
        self.std_dev_generation = std_dev_generation
        self.std_dev_verification = std_dev_verification
        self.std_dev_broadcast = std_dev_broadcast
        self.latency = latency

def update_clock(clock, time_increments):
    return clock + max(time_increments)

def has_two_thirds_majority(votes, num_validators):
    return sum(votes) > (2/3) * num_validators

# Function for the proposal phase
def proposal_phase(proposer, proposed_values, params, clock):
    # Generate a proposal
    proposal = proposer.generate_proposal(proposed_values)
    
    # Calculate time for proposal generation
    proposal_generation_time = cost_time(params.proposal_size, params.proposal_generation_rate, params.std_dev_generation)

    # Calculate time for proposal broadcast
    proposal_broadcast_time = cost_time(params.proposal_size, params.bandwidth, params.std_dev_broadcast)

    # Update the clock with proposal generation, broadcast time, and latency
    total_latency = prob_latency(params.latency, params.std_dev_broadcast)
    clock += proposal_generation_time + proposal_broadcast_time + total_latency

    return clock, proposal

# Function for the prevote phase
def prevote_phase(validators, proposer, proposal, params, clock):
    prevotes = []
    prevotes_time = []

    for v in validators:
        if v.id == proposer.id:
            prevotes.append(True)
            prevotes_time.append(0)
        else:
            is_valid = v.verify_proposal(proposal)
            prevotes.append(is_valid)
            if is_valid:
                v.valid_value = proposal

            # Calculate time for proposal verification
            proposal_verification_time = cost_time(params.proposal_size, params.proposal_verification_rate, params.std_dev_verification)

            # Calculate time for prevote vote broadcast
            single_vote_time = cost_time(params.vote_size, params.bandwidth, params.std_dev_broadcast)
            network_latency = prob_latency(params.latency, params.std_dev_broadcast)
            vote_broadcast_time = (single_vote_time + network_latency) * len(validators) 

            time = proposal_verification_time + vote_broadcast_time

            v.local_clock = clock + time
            prevotes_time.append(time)

    # Update global clock after prevote phase
    clock = update_clock(clock, prevotes_time)

    return clock, prevotes

# Function for the precommit phase
def precommit_phase(validators, prevotes, proposal, params, clock):
    precommits = []
    precommit_times = []

    for v in validators:
        if prevotes[validators.index(v)]:
            v.locked_value = proposal
            precommits.append(True)

            # Calculate time for precommit vote broadcast
            single_vote_time = cost_time(params.vote_size, params.bandwidth, params.std_dev_broadcast)
            network_latency = prob_latency(params.latency, params.std_dev_broadcast)
            vote_broadcast_time = (single_vote_time + network_latency) * len(validators)  # Simplify with Gossip logic if needed

            time = vote_broadcast_time

            v.local_clock = clock + time
            precommit_times.append(time)
        else:
            precommits.append(False)
            precommit_times.append(0)

    # Update global clock after precommit phase
    clock = update_clock(clock, precommit_times)

    return clock, precommits

# Main tendermint simulation function
def tendermint_simulation(validators, rounds, proposed_values, params):
    num_validators = len(validators)
    clock = 0
    consensus_times = []  # List to store the consensus times for each round

    for round in range(1, rounds + 1):
        previous_clock = clock  # Store the clock time at the start of the round
        proposer_id = (round - 1) % num_validators
        proposer = validators[proposer_id]

        # Proposal Phase
        clock, proposal = proposal_phase(proposer, proposed_values, params, clock)

        # Prevote Phase
        clock, prevotes = prevote_phase(validators, proposer, proposal, params, clock)

        # Check for 2/3 majority in prevotes
        if has_two_thirds_majority(prevotes, num_validators):
            # Precommit Phase
            clock, precommits = precommit_phase(validators, prevotes, proposal, params, clock)

            # Check if consensus is reached in precommit phase
            if has_two_thirds_majority(precommits, num_validators):
                consensus_times.append(clock - previous_clock)  # Store the time consensus is achieved
        else:
            # No consensus, continue to the next round without storing time
            continue

    # Return only the times when consensus is achieved
    return consensus_times