import json
import yaml
import argparse
from tarski.io import PDDLReader
# from utils import naive_variable_replacement            
from pathlib import Path   
import os
from Language2PDDL.scripts.utils import *
from Language2PDDL.domains.blocksworld.simulator import BlocksWorldManager, parse_problem_string
import Language2PDDL.domains.blocksworld.gen_lang as gen_lang

def construct_example(domain, problem, init_lang, goal_lang, entry):
    ctx_l, goal, ctx_r = extract_context_goal_tuple(problem)
    prompt = f";The PDDL domain definition is as follows: \n{domain}"
    # prompt += f"\n; As initial conditions I have that, {init_lang}."
    context = ctx_l + "\n...\n" + ctx_r
    prompt += f"\n; Part of the PDDL problem definition is as follows: \n{context}"
    # prompt += f"\n; The goal is to have that {goal_lang}."
    prompt += f"\n; The goal is as follows. {goal_lang}\n"
    prompt += "Write a PDDL goal definition that satisfies the description above."
    return {
        "prompt": prompt,
        "problem": problem,
        "completion": " " + goal  
    }

def construct_list_example(domain, problem, init_lang, goal_lang, entry):
    ctx_l, goal, ctx_r = extract_context_goal_tuple(problem)
    prompt = f";The PDDL domain definition is as follows: \n{domain}"
    # prompt += f"\n; As initial conditions I have that, {init_lang}."
    context = ctx_l + "\n...\n" + ctx_r
    prompt += f"\n; Part of the PDDL problem definition is as follows: \n{context}"
    # prompt += f"\n; The goal is to have that {goal_lang}."
    prompt += f"\n; The goal is as follows. {goal_lang}\n"
    prompt += "Generate Python lists representing the stacks stated above. " \
        "The list should contain objects specified in the domain description."
    
    if "constr" in entry and "goal_stacks" in entry["constr"]:
        goal_stacks = entry["constr"]["goal_stacks"]
    else:
        objects, facts, goals = parse_problem_string(domain, problem)
        res = BlocksWorldManager.facts_to_stack_state(objects, goals, strict=False)
        assert(res != False)
        goal_stacks = res[0]
    goal = str(goal_stacks)
    return {
        "prompt": prompt,
        "problem": problem,
        "completion": " " + goal
    }

def construct_lang_goal_example(domain, problem, init_lang, goal_lang, entry):
    ctx_l, goal, ctx_r = extract_context_goal_tuple(problem)
    prompt = f";The PDDL domain definition is as follows: \n{domain}"
    # prompt += f"\n; As initial conditions I have that, {init_lang}."
    context = ctx_l + "\n...\n" + ctx_r
    prompt += f"\n; Part of the PDDL problem definition is as follows: \n{context}"
    # prompt += f"\n; The goal is to have that {goal_lang}."
    prompt += f"\n; The goal is as follows. {goal_lang}\n"
    prompt += "Using objects specified in the domain description, " \
        "rewrite the goal in a way that satisfies the description above, " \
        "and then represent it with PDDL goal definition."
    
    objects, facts, goals = parse_problem_string(domain, problem)
    
    predicate_dict = {
        "ontable": "The {} is on the table.",
        "clear": "There is nothing on the {}.",
        "handempty": "The hand is empty.",
        "on": "The {} is on top of the {}."
    }
    
    precise_goal_lang = []
    for pred in goals:
        template = predicate_dict[pred[0]]
        pred_lang = template.format(*pred[1:]) if len(pred) > 1 else template
        precise_goal_lang.append(pred_lang)
        
    precise_goal_lang = " ".join(precise_goal_lang)
    goal = precise_goal_lang + "\n" + goal
    
    return {
        "prompt": prompt,
        "problem": problem,
        "completion": " " + goal
    }

def construct_checker_example(domain, problem, init_lang, goal_lang, entry):
    ctx_l, goal, ctx_r = extract_context_goal_tuple(problem)
    prompt = f";The PDDL domain definition is as follows: \n{domain}"
    # prompt += f"\n; As initial conditions I have that, {init_lang}."
    context = ctx_l + "\n...\n" + ctx_r
    prompt += f"\n; Part of the PDDL problem definition is as follows: \n{context}"
    # prompt += f"\n; The goal is to have that {goal_lang}."
    prompt += f"{goal_lang}\n"
    return {
        "prompt": prompt,
        "problem": problem,
        "completion": entry["answer"]  
    }


def construct_checker_example_with_checker(domain, entry, checker):
    prob_path = entry["path"]
    goal_lang, answer = checker.instance_to_text(prob_path)
    entry["completion"] = answer
    
    problem = Path(prob_path).read_text()
    ctx_l, goal, ctx_r = extract_context_goal_tuple(problem)
    prompt = f";The PDDL domain definition is as follows: \n{domain}"
    # prompt += f"\n; As initial conditions I have that, {init_lang}."
    context = ctx_l + "\n...\n" + ctx_r
    prompt += f"\n; Part of the PDDL problem definition is as follows: \n{context}"
    
    prompt += f"{goal_lang}\n"
    return {
        "prompt": prompt,
        "problem": problem,
        "completion": answer,
        "answer": answer
    }
    

def gen_goal_finetuning_data(domain_path, dataset_path, save_path, example_constructor=construct_example):
    domain = Path(domain_path).read_text()
    # domain_lang = config["domain_intro"]
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(dataset_path, "r") as fd, open(save_path, "w") as fout:
        data = fd.readlines()
        for dumped_entry in data:
            entry = json.loads(dumped_entry.strip())
            prob_path = entry["path"]
            init_lang = entry["init"]
            goal_lang = entry["goal"]
            prob_raw = Path(prob_path).read_text()
            example_entry = example_constructor(
                domain, prob_raw, init_lang, goal_lang, entry)
            entry.update(example_entry)
            fout.write(json.dumps(entry) + "\n")

def gen_domain_checker_data(domain_path, dataset_path, save_path, checker, size_cap=100):
    domain = Path(domain_path).read_text()
    # domain_lang = config["domain_intro"]
    # for checker_fn, name in domain_checker_dict.items():
        # save_path = save_path_template.format(checker=name)
    # checker = checker_fn(domain)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(dataset_path, "r") as fd, open(save_path, "w") as fout:
        data = fd.readlines()
        for dumped_entry in data[:size_cap]:
            entry = json.loads(dumped_entry.strip())
            example_entry = construct_checker_example_with_checker(domain, entry, checker)
            entry.update(example_entry)
            fout.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--config", type=str, required=True)
    # TODO change this to domain dir + domain name?
    parser.add_argument("--domain_path", type=str, required=True)
    parser.add_argument("--save_path", type=str, required=True)
    parser.add_argument("--dataset_path", type=str, required=True)
    # add arguments
    args = parser.parse_args()
    gen_goal_finetuning_data(args.domain_path, args.dataset_path, args.save_path)