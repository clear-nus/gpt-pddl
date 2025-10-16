import json
import yaml
import argparse
from tarski.io import PDDLReader
import time
import datetime
import re
import random
import openai


# define a retry decorator
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (openai.error.RateLimitError, openai.error.ServiceUnavailableError),
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specified errors
            except errors as e:
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper


@retry_with_exponential_backoff
def completion_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)
'''
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)
'''

def get_timestamp():
    current_time = datetime.datetime.now()
    time_stamp = current_time.timestamp()
    date_time = datetime.fromtimestamp(time_stamp)
    str_date_time = date_time.strftime("%d-%m-%Y-%H-%M-%S")
    return str_date_time

def extract_context_goal_tuple(problem):
    start_ptr = 0
    while start_ptr < len(problem):
        if problem[start_ptr:start_ptr+6] == "(:goal":
            break
        start_ptr += 1
    stack_ptr = 1
    ptr = start_ptr + 1
    while ptr < len(problem) and stack_ptr > 0:
        if problem[ptr] == '(':
            stack_ptr += 1
        elif problem[ptr] == ')':
            stack_ptr -= 1
        ptr += 1
        
    return problem[:start_ptr], problem[start_ptr:ptr], problem[ptr:]     

def naive_variable_replacement(problem, object_dict):
    vars = problem.split(' ')
    output = []
    for var in vars:
        if var in object_dict:
            output.append(object_dict[var])
            continue
        if var[1] == ')' and var[0] in object_dict:
            output.append(object_dict[var[0]] + var[1:])
            continue
        output.append(var)
        continue
    return " ".join(output)


def extract_legal_pddl(text):
    ptr = 0
    while ptr < len(text) and text[ptr:ptr+7] != '(define':
        ptr += 1
    lo = ptr
    stack = 0
    while ptr < len(text):
        if text[ptr] == '(':
            stack += 1
        elif text[ptr] == ')':
            stack -= 1
        ptr += 1
        if stack == 0:
            break
    hi = ptr
    return text[lo:hi]

def naive_text_acc(label, target):
    return " ".join(label.split()) == " ".join(target.split())

def goal_logic_acc(label, target, exact=True):
    template = "\(on\s+([_a-z]*)\s+([_a-z]*)\s*\)"
    pattern = re.compile(template)
    def naive_parse_goal(goal_str):
        result = re.findall(pattern, goal_str)
        return result
    target_parsed = set(naive_parse_goal(target))
    label_parsed = set(naive_parse_goal(label))
    for atom in label_parsed:
        if not atom in target_parsed:
             return 0
    if exact:
        for atom in target_parsed:
            if not atom in label_parsed:
                return 0
    return 1
        
def reversed_goal_logic_acc(label, target, exact=True):
    template = "\(on\s+([_a-z]*)\s+([_a-z]*)\s*\)"
    pattern = re.compile(template)
    def naive_parse_goal(goal_str):
        result = re.findall(pattern, goal_str)
        return result
    target_parsed = set(naive_parse_goal(target))
    target_parsed = set([(x[1], x[0]) for x in target_parsed])
    label_parsed = set(naive_parse_goal(label))
    print(target_parsed, label_parsed)
    for atom in label_parsed:
        if not atom in target_parsed:
             return 0
    if exact:
        for atom in target_parsed:
            if not atom in label_parsed:
                return 0
    return 1       
    

def blocksworld_problem_similarity(domain, label, target):
    # TODO: more accurate comparison
    label_reader = PDDLReader(raise_on_error=True)
    label_reader.parse_domain_string(domain)
    try:
        label_prob = label_reader.parse_instance_string(label)
    except:
        return 0
    
    assert(label_prob != None)
    target_reader = PDDLReader(raise_on_error=True)
    target_reader.parse_domain_string(domain)
    try:
        target_prob = target_reader.parse_instance_string(target)
    except:
        return 0
    
    if label_prob.domain_name != target_prob.domain_name:
        return 0
    
    '''
    if label_prob.init != target_prob.init:
        return 0
    '''
    
    if label_prob.goal != target_prob.goal:
        return 0
    
    return 1