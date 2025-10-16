import os
import json
import uuid
from tqdm import tqdm
from pathlib import Path

from Language2PDDL.domains.blocksworld.simulator import BlocksWorldManager, \
    parse_problem_file, parse_plan_file, parse_problem_string
import Language2PDDL.domains.blocksworld.gen_lang as bw_gen_lang
from Language2PDDL.scripts.planner import validate_plan
from Language2PDDL.scripts.utils import completion_with_backoff, \
    goal_logic_acc, extract_context_goal_tuple

BW_DOMAIN_PATH = os.path.join(os.environ["ROOT_DIR"], "domains/blocksworld/generated_domain.pddl")

def select_example_by_shortest(source_path, min_k=1):
    with open(source_path, "r") as f:
        examples = f.readlines()
        loaded_examples = [ json.loads(x.strip()) for x in examples ]
        loaded_examples.sort(key=lambda x: len(x["completion"]))
        example = loaded_examples[:min_k]
        return example

def select_example_by_order(source_path, num=1):
    examples = Path(source_path).read_text().split('\n')
    example = [ json.loads(examples[idx]) for idx in range(num) ]
    return example

def select_example_by_indices(source_path, indices=[0,]):
    examples = Path(source_path).read_text().split('\n')
    example = [ json.loads(examples[idx]) for idx in indices if idx < len(examples) ]
    return example

###########
# metrics #
###########

def text_acc_goal_metric(answer, entry):
    return goal_logic_acc(answer, entry["completion"])

def pddl_validity_eval_goal_metric(answer, entry):
    domain_path = BW_DOMAIN_PATH
    problem = entry["problem"]
    ctx_l, _, ctx_r = extract_context_goal_tuple(problem)
    new_prob = ctx_l + " " + answer + " " + ctx_r
    instance_path = "./tmp-problem-{}.pddl".format(str(uuid.uuid4()))
    with open(instance_path, "w") as f_prob:
        f_prob.write(new_prob)
    try:
        parse_problem_file(domain_path, instance_path)
    except Exception as e:
        os.remove(instance_path)
        return False
    os.remove(instance_path)
    return True

def goal_validity_eval_goal_metric(answer, entry):
    domain_path = BW_DOMAIN_PATH
    problem = entry["problem"]
    ctx_l, _, ctx_r = extract_context_goal_tuple(problem)
    new_prob = ctx_l + " " + answer + " " + ctx_r
    instance_path = "./tmp-problem-{}.pddl".format(str(uuid.uuid4()))
    with open(instance_path, "w") as f_prob:
        f_prob.write(new_prob)
    try:
        objects, facts, goals = parse_problem_file(domain_path, instance_path)
    except Exception as e:
        print("parsing error", e)
        os.remove(instance_path)
        return False
    res = BlocksWorldManager.facts_to_stack_state(objects, goals)
    os.remove(instance_path)
    if res == False:
        return False
    return True


def constr_loose_eval_goal_metric(answer, entry):
    '''
    This is an ambiguous metric, kept just for compatibility.
    "constr_eval_goal_metric" defines the LOOSE metric used in the paper.
    '''
    return constr_eval_goal_metric(answer, entry, extend=True, strict=False)

def constr_strict_eval_goal_metric(answer, entry):
    '''
    The STRICT metric used in the paper.
    '''
    return constr_eval_goal_metric(answer, entry, extend=False, strict=True)

def constr_eval_goal_metric(answer, entry, extend=False, strict=False):
    '''
    The LOOSE metric used in the paper.
    '''
    domain_path = BW_DOMAIN_PATH
    constr = bw_gen_lang.ConstrSpecBase.load(entry["constr"])
    problem = entry["problem"]
    ctx_l, _, ctx_r = extract_context_goal_tuple(problem)
    new_prob = ctx_l + " " + answer + " " + ctx_r
    instance_path = "./tmp-problem-{}.pddl".format(str(uuid.uuid4()))
    with open(instance_path, "w") as f_prob:
        f_prob.write(new_prob)
    try:
        objects, facts, goals = parse_problem_file(domain_path, instance_path)
    except Exception as e:
        # print("parsing error", e)
        os.remove(instance_path)
        return False
    res = BlocksWorldManager.facts_to_stack_state(objects, goals, extend=extend, strict=strict)
    os.remove(instance_path)
    if res == False:
        return False
    goal_stacks = res[0]

    return constr.evaluate(goal_stacks, objects)

def constr_eval_list_goal_metric(answer, entry):
    domain_path = BW_DOMAIN_PATH
    constr = bw_gen_lang.ConstrSpecBase.load(entry["constr"])
    domain = Path(domain_path).read_text()
    problem = entry["problem"]
    objects, _, _  = parse_problem_string(domain, problem)
    try:
        goal_stacks = eval(answer.strip())
    except Exception:
        print("parsing error")
        return False
    if not isinstance(goal_stacks, list):
        print("type error")
        return False
    for stack in goal_stacks:
        if not isinstance(stack, list):
            print("type error")
            return False
        for obj in stack:
            if not obj in objects:
                print("unseen object", obj)
                return False
    
    return constr.evaluate(goal_stacks, objects)

def constr_eval_check_metric(answer, entry):
    label = entry["answer"]
    def process(raw):
        l = raw.strip().split(" ")
        l = [ e.lower() for e in l ]
        l.sort()
        return l
    tgt_list = process(answer)
    lbl_list = process(label)
    for x, y in zip(lbl_list, tgt_list):
        if not x == y:
            # print(lbl_list, tgt_list)
            return False
    return True
def constr_eval_lang_goal_metric(answer, entry):
    _, answer, _ = extract_context_goal_tuple(answer)
    return constr_eval_goal_metric(answer, entry)

def naive_validate_plan_metric(answer, entry):
    domain_path = BW_DOMAIN_PATH
    plan_file = "./tmp-plan-{}.txt".format(str(uuid.uuid4()))
    problem_file = "./tmp-problem-{}.pddl".format(str(uuid.uuid4()))
    with open(plan_file, "w") as fplan, open(problem_file, "w") as fprob:
        fprob.write(entry["problem"])
        fplan.write(answer)
    ret = validate_plan(domain_path, problem_file, plan_file)
    # TODO: this remove is not working
    os.remove(plan_file)
    os.remove(problem_file)
    return ret

def constr_validate_plan_metric(answer, entry):
    domain_path = BW_DOMAIN_PATH
    constr = bw_gen_lang.ConstrSpecBase.load(entry["constr"])
    plan_file = "./tmp-plan-{}.txt".format(str(uuid.uuid4()))
    problem_file = "./tmp-problem-{}.pddl".format(str(uuid.uuid4()))
    with open(plan_file, "w") as fplan, open(problem_file, "w") as fprob:
        fprob.write(entry["problem"])
        fplan.write(answer)
        
    objects, facts, _ = parse_problem_file(domain_path, problem_file)
    manager = BlocksWorldManager()
    manager.initialize(objects, facts)
    action_seq = parse_plan_file(plan_file)
    os.remove(plan_file)
    os.remove(problem_file)
    for action in action_seq:
        succ = manager.step(action)
        if not succ:
            return False
    goal_stacks = manager.stacks
    ret = constr.evaluate(goal_stacks)
    
    return ret

def fewshot_evaluation(model, 
                       example_path, 
                       dataset_path, 
                       save_path, 
                       test_size=100,
                       metric=constr_strict_eval_goal_metric,
                       example_select=select_example_by_order):
    examples = example_select(example_path)
    prompt_prefix = ""
    for example in examples:
        prompt_prefix += "Q: "+ example["prompt"] \
            + "\nA: " + example["completion"] + "\n"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(dataset_path, "r") as fd, open(save_path, "w") as fout:
        data = fd.readlines()[:test_size]
        score = 0
        for dumped_entry in tqdm(data):
            question = json.loads(dumped_entry.strip())

            fs_prompt = prompt_prefix \
                + "Q:" + question["prompt"] \
                    + "\nA:"
            
            response = completion_with_backoff(
                model=model,
                prompt=fs_prompt,
                temperature=0.0,
                max_tokens=1000,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop="Q:"
            )
            answer = response['choices'][0]['text']
            if metric(answer, question):
                score += 1
            dumped_ans = json.dumps({"prompt": fs_prompt,"completion": answer})
            fout.write(dumped_ans + "\n")
        print("accuracy:", score / len(data))