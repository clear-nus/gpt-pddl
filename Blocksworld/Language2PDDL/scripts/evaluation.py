import os
import json
import yaml
import argparse
from pathlib import Path
from Language2PDDL.scripts.planner import validate_plan
from Language2PDDL.scripts.utils import *
from Language2PDDL.scripts.inference import *
# import Language2PDDL.domains.blocksworld.gen_lang as gen_lang

'''
def text_acc(domain_path, label_dir, target_dir):
    target_files = os.listdir(target_dir)
    domain = Path(domain_path).read_text()
    total_score = 0
    for target_file in target_files:
        label_path = os.path.join(label_dir, target_file)
        target_path = os.path.join(target_dir, target_file)
        label_prob = Path(label_path).read_text()
        target_prob = Path(target_path).read_text()
        target_prob = extract_legal_pddl(target_prob)
        score = blocksworld_problem_similarity(domain, label_prob, target_prob)
        if score < 0.5:
            print(label_prob, target_prob)
        total_score += score
    return total_score / len(target_files)
'''
    

def naive_plan_grounding(plan):
    new_plan = []
    flag = False
    for i in range(len(plan)):
        if plan[i+1:i+6] == "block" and plan[i] == ' ':
            flag = True
            new_plan.append('_')
        else:
            new_plan.append(plan[i])
    new_plan = ''.join(new_plan)
    if flag:
        print(new_plan)
    return new_plan

def ground_plan_files(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    plan_files = os.listdir(src_dir)
    for plan_file in plan_files:
        plan = Path(os.path.join(src_dir, plan_file)).read_text()
        plan = naive_plan_grounding(plan)
        with open(os.path.join(dst_dir, plan_file), "w") as fout:
            fout.write(plan)

def succ_rate(domain_path, prob_dir, plan_dir):
    plan_files = os.listdir(plan_dir)
    total_score = 0
    for plan_file in plan_files:
        prob_file = os.path.basename(plan_file).split('.')[0] + '.pddl'
        prob_path = os.path.join(prob_dir, prob_file)
        plan_path = os.path.join(plan_dir, plan_file)
        total_score += validate_plan(domain_path, prob_path, plan_path)
    return total_score / len(plan_files)
    

def goal_evaluation(label_path, target_path, metric=text_acc_goal_metric):
    with open(label_path) as f_label, open(target_path) as f_target:
        score = 0
        labels = f_label.readlines()
        targets = f_target.readlines()
        for label, target in zip(labels, targets): 
            label = json.loads(label)
            target = json.loads(target)
            tgt_goal = target["completion"]
            if metric(tgt_goal, label):
                score += 1
        return score, score / len(labels)

def get_detailed_eval_result(label_path, target_path, metric=text_acc_goal_metric):
    results = []
    with open(label_path) as f_label, open(target_path) as f_target:
        score = 0
        labels = f_label.readlines()
        targets = f_target.readlines()
        for label, target in zip(labels, targets): 
            label = json.loads(label)
            target = json.loads(target)
            tgt_goal = target["completion"]
            results.append(metric(tgt_goal, label))
        return results    

def plan_evaluation(label_path, target_path, metric=naive_validate_plan_metric):
    with open(label_path) as f_label, open(target_path) as f_target:
        score = 0
        labels = f_label.readlines()
        targets = f_target.readlines()
        assert(len(labels) >= len(targets))
        for label, target in zip(labels, targets):
            label = json.loads(label)
            target = json.loads(target)
            plan = target["completion"]
            if metric(plan, label):
                score += 1
        print(score / len(labels))

readability_dict = {
    'standard': "ExplicitStacks",
    'stack_seq': "ExplicitStacks-II",
    'c1': "BlockAmbiguity",
    'h1': "NBlocks",
    'heq': "KStacks",
    'hprime': "PrimeStack",
    'ceq': "KStacksColor"
}

def evaluate_all_list(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    RESULT_DIR = os.path.dirname(config["list_result_template"])
    RESULT_DIR = os.path.join(os.environ["ROOT_DIR"], RESULT_DIR)
    results = os.listdir(RESULT_DIR)
    results.sort()
    for target_path in results:
        if not target_path.endswith("txt"):
            continue
        target_base = target_path.split(".")[0].split("-")
        print(target_base)
        if target_base[-1].endswith("test"):
            dataset = target_base[-1]
        elif len(target_base) >=2 and target_base[-2].endswith("test"):
            dataset = target_base[-2]
        else:
            continue
        
        label_path = config["goal_finetuning_template"].format(dataset)
        label_path = os.path.join(os.environ["ROOT_DIR"], label_path)
        # label_path = "data/prob_finetuning_dataset/goal_pred_{}.txt".format(dataset)
        if not os.path.exists(label_path):
            continue
        print(target_path, os.path.basename(label_path))
        target_path = os.path.join(RESULT_DIR, target_path)
        # plan_evaluation(label_path, target_path)
        try:
            _, s1 = goal_evaluation(label_path, target_path, metric=constr_eval_list_goal_metric)
        except KeyError:
            continue
        
        print(s1)

def evaluate_all(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    RESULT_DIR = os.path.dirname(config["goal_result_template"])
    RESULT_DIR = os.path.join(os.environ["ROOT_DIR"], RESULT_DIR)
    results = os.listdir(RESULT_DIR)
    results.sort()
    template = "obj_(.*?)_(.*?)_mode"
    pattern = re.compile(template)
    res_dict = {}
    for target_path in results:
        if not target_path.endswith("txt"):
            continue
        target_base = target_path.split(".")[0].split("-")
        
        if target_base[-1].endswith("test"):
            dataset = target_base[-1]
            variant = "STANDARD"
        elif len(target_base) >=2 and target_base[-2].endswith("test"):
            dataset = target_base[-2]
            variant = target_base[-1]
        else:
            continue
        
        label_path = config["goal_finetuning_template"].format(dataset)
        label_path = os.path.join(os.environ["ROOT_DIR"], label_path)
        # label_path = "data/prob_finetuning_dataset/goal_pred_{}.txt".format(dataset)
        if not os.path.exists(label_path):
            continue
        # print(target_path, os.path.basename(label_path))
        target_path = os.path.join(RESULT_DIR, target_path)
        # plan_evaluation(label_path, target_path)
        try:
            _, s1 = goal_evaluation(label_path, target_path, metric=pddl_validity_eval_goal_metric)
        except KeyError:
            continue
        _, s2 = goal_evaluation(label_path, target_path, metric=goal_validity_eval_goal_metric)
        _, s3 = goal_evaluation(label_path, target_path, metric=constr_strict_eval_goal_metric)
        _, s3_l = goal_evaluation(label_path, target_path, metric=constr_eval_goal_metric)
        e1 = 1-s1
        e2 = 1-s2
        e3 = 1-s3
        de2 = e2-e1
        de3 = e3-e2
        result = [s3_l, s3, e1, de2, de3]
        print(dataset, variant)
        for data in result:
            print("{:.2f}".format(data * 100), end=" ")
        print("")
        res = re.search(pattern, target_path)
        obj_num, task = res.group(1), res.group(2)
        if not task in res_dict:
            res_dict[task] = {}
        
def find_failing_index(config_path, num=2):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    RESULT_DIR = os.path.dirname(config["goal_result_template"])
    RESULT_DIR = os.path.join(os.environ["ROOT_DIR"], RESULT_DIR)
    results = os.listdir(RESULT_DIR)
    results.sort()
    for target_path in results:
        if not target_path.endswith("txt"):
            continue
        if "weak" in target_path:
            continue
        if not "standard" in target_path or not "12" in target_path:
            continue
        target_base = target_path.split(".")[0].split("-")
        print(target_base)
        if target_base[-1].endswith("test"):
            dataset = target_base[-1]
        elif len(target_base) >=2 and target_base[-2].endswith("test"):
            dataset = target_base[-2]
        else:
            continue
        
        label_path = config["goal_finetuning_template"].format(dataset)
        label_path = os.path.join(os.environ["ROOT_DIR"], label_path)
        # label_path = "data/prob_finetuning_dataset/goal_pred_{}.txt".format(dataset)
        list_res_path = target_path.replace("pddl_files", "list_files")
        if not os.path.exists(label_path):
            continue
        print(target_path, os.path.basename(label_path))
        target_path = os.path.join(RESULT_DIR, target_path)
        # plan_evaluation(label_path, target_path)
        failing_cases = []
        res_index = []
        with open(label_path) as f_label, open(target_path) as f_target:
            labels = f_label.readlines()
            targets = f_target.readlines()
            for idx, (label, target) in enumerate(zip(labels, targets)): 
                label = json.loads(label)
                target = json.loads(target)
                
                # lbl_goal = label["completion"]
                tgt_goal = target["completion"]
                try:
                    result = constr_strict_eval_goal_metric(tgt_goal, label)
                except KeyError:
                    continue

                if not result:
                    res_index.append(idx)
                    failing_cases.append(500 + eval(re.findall(r'\d+', label['path'])[-1]))
                    if len(failing_cases) == num:
                        break
            print(failing_cases, res_index)


def calculate_goal_inference_failure(config_path, succ_case=True):
    if succ_case == "succ":
        print("Evaluating on SUCCESS cases")
    else:
        print("Evaluating on FAILURE cases")
    # RESULT_DIR = "results/completion/pddl_files/blocksworld"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    RESULT_DIR = os.path.dirname(config["goal_result_template"])
    RESULT_DIR = os.path.join(os.environ["ROOT_DIR"], RESULT_DIR)
    results = os.listdir(RESULT_DIR)
    results.sort()

    template = "obj_(.*?)_(.*?)_mode"
    pattern = re.compile(template)
    REF_RESULT = 1 if succ_case else 0
    res_dict = {}
    for target_path in results:
        if not target_path.endswith("test.txt"):
            continue
        target_base = target_path.split(".")[0].split("-")
        
        if target_base[-1].endswith("test"):
            dataset = target_base[-1]
        # elif len(target_base) >=2 and target_base[-2].endswith("test"):
        #     dataset = target_base[-2]
        else:
            continue
        
        label_path = config["goal_finetuning_template"].format(dataset)
        label_path = os.path.join(os.environ["ROOT_DIR"], label_path)
        # label_path = "data/prob_finetuning_dataset/goal_pred_{}.txt".format(dataset)
        
        if not os.path.exists(label_path):
            continue
        
        target_path = os.path.join(RESULT_DIR, target_path)
        list_tgt_path = config["list_result_template"].format(config["model"], dataset)
        list_lbl_path = config["list_finetuning_template"].format(dataset)
        if not os.path.exists(list_tgt_path) or not os.path.exists(list_lbl_path):
            continue
        try:
            goal_res = get_detailed_eval_result(label_path, target_path, metric=constr_strict_eval_goal_metric)
        except KeyError:
            continue
        list_res = get_detailed_eval_result(list_lbl_path, list_tgt_path, metric=constr_eval_list_goal_metric)

        res = re.search(pattern, target_path)
        obj_num, task = res.group(1), res.group(2)
        if task == 'seq_t2b' or task == 'seq_b2t':
            task = 'stack_seq'
        if not task in res_dict:
            res_dict[task] = {"case_total":0, "goal_total":0}
        case_total = 0
        goal_total = 0
        for x, y in zip(goal_res, list_res):
            if x == REF_RESULT:
                case_total += 1
                if y == 0:
                    goal_total += 1
       
        res_dict[task]["case_total"] += case_total
        res_dict[task]["goal_total"] += goal_total
       # print(target_base)
        
    order = [
        'standard',
        'stack_seq',
        'c1',
        'h1',
        'heq',
        'hprime',
        'ceq'
    ]  
        
    for key in order:
        if not key in res_dict:
            continue
        val = res_dict[key]
        print(readability_dict[key], end=" ")
        case_total = val["case_total"]
        goal_total = val["goal_total"]
        print("{:.2f}".format(100 * goal_total / case_total) if case_total != 0 else "-")
        # print(val["goal_total"], val["case_total"], val["goal_total"] / val["case_total"] if val["case_total"] != 0 else "-")


def calculate_domain_understanding_failure(config_path, succ_case=True):
    if succ_case == "succ":
        print("Evaluating on SUCCESS cases")
    else:
        print("Evaluating on FAILURE cases")
    # RESULT_DIR = "results/completion/pddl_files/blocksworld"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    RESULT_DIR = os.path.dirname(config["goal_result_template"])
    RESULT_DIR = os.path.join(os.environ["ROOT_DIR"], RESULT_DIR)
    results = os.listdir(RESULT_DIR)
    results.sort()

    template = "obj_(.*?)_(.*?)_mode"
    pattern = re.compile(template)

    res_dict = {}
    REF_RESULT = 1 if succ_case else 0
    domain_checker_list =  [
      "obj_list",
      "color_list",
      "on_pred",
      "table_pred",
      "clear_pred"
    ]
    
    for target_path in results:
        if not target_path.endswith("test.txt"):
            continue
        target_base = target_path.split(".")[0].split("-")
        # print(target_base)
        if target_base[-1].endswith("test"):
            dataset = target_base[-1]
        # elif len(target_base) >=2 and target_base[-2].endswith("test"): # this is a variation
        #     dataset = target_base[-2]
        else:
            continue
        
        label_path = config["goal_finetuning_template"].format(dataset)
        label_path = os.path.join(os.environ["ROOT_DIR"], label_path)
        # label_path = "data/prob_finetuning_dataset/goal_pred_{}.txt".format(dataset)
        
        if not os.path.exists(label_path):
            # print("Not found:", label_path)
            continue
        
        target_path = os.path.join(RESULT_DIR, target_path)
        try:
            goal_res = get_detailed_eval_result(label_path, target_path, metric=constr_strict_eval_goal_metric)
        except KeyError:
            # print("key error", target_path)
            continue
        
        checked = True
        checker_res_dict = {}
        # for checker, cname in domain_checker_dict.items():
        for cname in domain_checker_list:
            checker_dataset_name = config["checker_name_template"].format(dataset=dataset.replace("mode_test", "mode_check"), checker=cname)
            checker_tgt_path = config["check_result_template"].format(config["model"], checker_dataset_name)
            checker_lbl_path = config["check_finetuning_template"].format(checker_dataset_name)
            if not os.path.exists(checker_tgt_path) or not os.path.exists(checker_lbl_path):
                print(checker_tgt_path)
                checked = False
                break
            checker_res_dict[cname] = get_detailed_eval_result(checker_lbl_path, checker_tgt_path, metric=constr_eval_check_metric)
        if not checked:
            continue
        
        res = re.search(pattern, target_path)
        obj_num, task = res.group(1), res.group(2)
        if task == 'seq_t2b' or task == 'seq_b2t':
            task = 'stack_seq'
        if not task in res_dict:
            res_dict[task] = { cname: {"case_total":0, "goal_total":0} for cname in domain_checker_list }
        
        for cname in domain_checker_list:
            case_total = 0
            goal_total = 0
            for x, y in zip(goal_res, checker_res_dict[cname]):
                if x == REF_RESULT:
                    case_total += 1
                    if y == 0:
                        goal_total += 1
            res_dict[task][cname]["case_total"] += case_total
            res_dict[task][cname]["goal_total"] += goal_total
       
       
    order = [
        'standard',
        'stack_seq',
        'c1',
        'h1',
        'heq',
        'hprime',
        'ceq'
    ]
    
    c_order = [
        "obj_list",
        "color_list",
        "on_pred",
        "table_pred",
        "clear_pred"
    ]
    
    for key in order:
        if not key in res_dict:
            continue
        val = res_dict[key]
        print(readability_dict[key], end=" ")
        rate_sum = 0
        for cname in c_order:
            case_total = val[cname]["case_total"]
            goal_total = val[cname]["goal_total"]
            if case_total == 0:
                rate_sum = -1
                break
            print("{:.2f}".format(100 * goal_total / case_total) if case_total != 0 else "-", end=" ")
            rate_sum += goal_total / case_total
        if rate_sum < 0:
            print("-")
        else:
            print("{:.2f}".format(rate_sum / len(c_order) * 100))
        print("")

mode_dict = {
    "all": lambda args: evaluate_all(config_path=args.config),
    "goal_inf": lambda args: calculate_goal_inference_failure(config_path=args.config, succ_case=(args.case=="succ")),
    "dom_und": lambda args: calculate_domain_understanding_failure(config_path=args.config, succ_case=(args.case=="succ"))
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="domains/blocksworld/gen_data_config.yaml")
    parser.add_argument("--mode", type=str, default="all", choices=mode_dict.keys())
    parser.add_argument("--case", type=str, default="succ", choices=["succ", "fail"])
    args = parser.parse_args()
    args.config = os.path.join(os.environ["ROOT_DIR"], args.config)
    return args

if __name__ == "__main__":
    args = parse_args()
    
    mode_dict[args.mode](args)
    