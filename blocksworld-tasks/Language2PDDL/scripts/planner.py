import os
import json
import yaml
from tqdm import tqdm
import argparse
from pathlib import Path
from tarski.io import PDDLReader

from Language2PDDL.domains.blocksworld.simulator import BlocksWorldManager, parse_problem_file
from Language2PDDL.scripts.utils import *

def validate_plan(domain, instance, plan):    
    cmd = f"validate {domain} {instance} {plan}"
    response = os.popen(cmd).read()
    print(response)
    if 'Problem in domain' in response:
        raise Exception('Problem in domain: Check PDDL Writer')
    return True if "Plan valid" in response else False

def compute_naive_plan(domain, instance):
    result = parse_problem_file(domain, instance)
    plan = BlocksWorldManager.generate_naive_plan(*result)    
    plan = [ "(" + " ".join(x) + ")" for x in plan ]
    plan.append("; end")
    return '\n'.join(plan)

def compute_plan(domain, instance, plan_file="sas_plan", timeout=150):
    '''
    domain - Path to the domain file
    instance - Path to the problem file
    plan_file - the temporary filename for generated plan
    '''
    fast_downward_path = os.getenv("DOWNWARD_DIR")
    # Remove > /dev/null to see the output of fast-downward
    assert(os.path.exists(f"{fast_downward_path}/fast-downward.py"))
    cmd = f"timeout {timeout}s {fast_downward_path}/fast-downward.py --plan-file {plan_file} {domain} {instance} --search \"astar(lmcut())\" > /dev/null 2>&1"
    os.system(cmd)

    if not os.path.exists(plan_file):
        return ""
    return Path(plan_file).read_text()

def construct_example(domain, problem, plan, init_lang, goal_lang):
    ctx_l, goal, ctx_r = extract_context_goal_tuple(problem)
    prompt = f";The PDDL domain definition is as follows: \n{domain}"
    # prompt += f"\n; As initial conditions I have that, {init_lang}."
    context = ctx_l + "\n...\n" + ctx_r
    prompt += f"\n; Part of the PDDL problem definition is as follows: \n{context}"
    prompt += f"\n; The goal is as follows. {goal_lang}\n"
    prompt += "Write a plan that satisfies the description above."
    return {
        "prompt": prompt,
        "problem": problem,
        "completion": " " + plan
    }

def generate_plan_dataset(domain_path, dataset_dir, save_dir, heuristics=False):
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(dataset_dir, "data.txt"), 'r') as f:
        data = f.readlines()
        for entry_raw in data:
            entry = json.loads(entry_raw.strip())
            problem_file = entry["path"]
            filename = os.path.basename(problem_file).split('.')[0] + '.plan'
            if heuristics:
                plan = compute_naive_plan(domain_path, problem_file)
            else:
                plan = compute_plan(domain_path, problem_file)
            plan_path = os.path.join(save_dir, filename)
            with open(plan_path, 'w') as fout:
                fout.write(plan)
            valid = validate_plan(domain_path, problem_file, plan_path)
            if not valid:
                print(f"invalid plan: {plan_path} for {domain_path} {problem_file}")
                break

def gen_plan_finetuning_data(domain_path, dataset_path, save_path, heuristics=False):
    domain = Path(domain_path).read_text()
    test = dataset_path.endswith("test/data.txt")
    print(dataset_path, test)
    with open(dataset_path) as f, open(save_path, 'w') as fout:
        data = f.readlines()
        for line in tqdm(data):
            entry = json.loads(line.strip())
            problem_file = entry["path"]
            init = entry["init"]
            goal = entry["goal"]
            problem = Path(problem_file).read_text()
            if not test:
                if not "plan" in entry:     
                    if heuristics:
                        plan = compute_naive_plan(domain_path, problem_file)
                    else:
                        plan = compute_plan(domain_path, problem_file)
                else:
                    plan_path = entry["plan"]
                    plan = Path(plan_path).read_text()
            else:
                plan = ""
            example_entry = construct_example(domain, problem, plan, init, goal)
            entry.update(example_entry)
            fout.write(json.dumps(entry)+"\n")
            
            
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain_path", type=str, required=True)
    parser.add_argument("--dataset_path", type=str, required=True)
    parser.add_argument("--save_path", type=str, required=True)
    args = parser.parse_args()
    return args
    
            
if __name__ == "__main__":
    args = parse_args()
    gen_plan_finetuning_data(
        domain_path=args.domain_path, 
        dataset_path=args.dataset_path, 
        save_path=args.save_path)
