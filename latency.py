import numpy as np
from scipy.stats import truncnorm

"""
mean_rate: Select between 10 - 500 MB/s depending on the network environment. Generally, 100 MB/s is a common and moderate value.
mean_latency: Select between 1 - 150 ms depending on node geographic distribution. 50 ms is suitable for cross-country node communication.
std_dev: Choose an appropriate standard deviation to simulate network fluctuation, typically between 10 - 20.
"""

def truncated_normal(mean, std_dev, lower, upper):
    """
    Generate a value from a truncated normal distribution within the given bounds.

    Parameters:
    - mean: Mean of the distribution
    - std_dev: Standard deviation of the distribution
    - lower: Lower bound of the value
    - upper: Upper bound of the value

    Returns:
    - A value from the truncated normal distribution
    """
    return truncnorm((lower - mean) / std_dev, (upper - mean) / std_dev, loc=mean, scale=std_dev).rvs()

def cost_time(message_size, mean_rate, std_dev):
    """
    Calculate the time required to generate/verify/propagate a message based on message size,
    mean rate, and standard deviation.

    Parameters:
    - message_size: Size of the message in MB
    - mean_rate: Mean operation rate in MB/s
    - std_dev: Standard deviation of the operation rate in MB/s

    Returns:
    - operation_time: The time required to operate the message in seconds
    """
    # Generate the rate using a truncated normal distribution to ensure it's within a reasonable range
    generation_rate = truncated_normal(mean_rate, std_dev, 0.1, mean_rate * 2)  # Lower bound of 0.1 MB/s, upper bound is twice the mean rate
    
    # Calculate the time required to operate the message (seconds) using the generated rate
    time = message_size / generation_rate
    return time

def prob_latency(mean_latency, std_dev):
    """
    Calculate the network latency with a given mean and standard deviation.

    Parameters:
    - mean_latency: Mean latency in milliseconds
    - std_dev: Standard deviation of the latency in milliseconds

    Returns:
    - current_latency: The latency in seconds (always positive)
    """
    # Generate latency using a log-normal distribution because network latency typically has a skewed distribution with most values being small and occasional larger values, 
    # while also ensuring it is always positive. This makes it suitable for modeling real-world network conditions where delays are generally low but can occasionally spike.
    current_latency = np.random.lognormal(mean=np.log(mean_latency), sigma=std_dev / 100.0)  # Convert std_dev to a scale factor for lognormal
    
    return current_latency / 1000  # Convert milliseconds to seconds