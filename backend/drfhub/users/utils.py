import random 
from django.db import IntegrityError
from django.apps import apps

def generate_random_bigint():
    """
    Generate a random BigInt in the range 10,000 to 999,999,999,999,999,999
    
    The database's PRIMARY KEY constraint will handle uniqueness.
    
    Returns:
        int: A random big integer
    """
    return random.randint(10_000, 999_999_999_999_999_999)