import os
import argparse
import yaml
import json
import random
from collections import defaultdict
from tarski.io import PDDLReader
from pathlib import Path
from copy import deepcopy


import Language2PDDL.domains.blocksworld.gen_lang as gen_lang
from Language2PDDL.domains.blocksworld.gen_lang import naive_variable_replacement

from Language2PDDL.scripts.utils import extract_context_goal_tuple
from Language2PDDL.scripts.planner import gen_plan_finetuning_data
from Language2PDDL.scripts.prepare_finetuning import gen_goal_finetuning_data, \
    construct_list_example, construct_lang_goal_example, construct_checker_example, \
        gen_domain_checker_data

def load_pddl_paths_by_range(dataset, pddl_dir, plan_dir, filename_template, i_start, i_end):
    path_template = os.path.join(pddl_dir, filename_template)
    planname_template = filename_template.split(".")[0] + ".plan"
    planpath_template = os.path.join(plan_dir, planname_template)
    for i in range(i_start, i_end):
        dataset.append((path_template.format(i), planpath_template.format(i)))
    return dataset 

def load_pddl_paths_by_idx(dataset, pddl_dir, plan_dir, filename_template, indices):
    path_template = os.path.join(pddl_dir, filename_template)
    planname_template = filename_template.split(".")[0] + ".plan"
    planpath_template = os.path.join(plan_dir, planname_template)
    for i in indices:
        dataset.append((path_template.format(i), planpath_template.format(i)))
    return dataset 


def separate_pddl_paths_by_plan_length(dataset):
    plan_prop_dict = {}
    len_cnt = defaultdict(int)
    for prob_path, plan_path in dataset:
        with open(plan_path) as f:
            plan_len = len(f.readlines())
            plan_prop_dict[prob_path] = plan_len
            len_cnt[plan_len] += 1
    len_cnt_list = [ (key, len_cnt[key]) for key in len_cnt ]
    len_cnt_list.sort(key=lambda x: x[0])
    sum = 0
    medium = 0
    for key, value in len_cnt_list:
        sum += value
        if sum > len(dataset) / 2:
            medium = key
            break
    prob_lo = []
    prob_hi = []
    for prob_path, plan_path in dataset:
        plan_len = plan_prop_dict[prob_path]
        if plan_len > medium:
            prob_hi.append((prob_path, plan_path))
        else:
            prob_lo.append((prob_path, plan_path))
    return prob_lo, prob_hi, medium
        
    
class DataGenerator():
    def __init__(self, config, save_dir, shuffle, domain_path, 
                 rewrite=False,
                 translator=None):
        self.read_config(config)
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        # self.dataset_dir = os.path.join(self.save_dir, "dataset", args.split)
        # os.makedirs(self.dataset_dir, exist_ok=True)
        self.shuffle = shuffle
        self.domain_path = domain_path
        if translator != None:
            self.translator = translator
        else:         
            # These are deprecated trasnlators
            if rewrite:
                self.translator = gen_lang.StackTranslator(self.domain_path)
            else:
                self.translator = gen_lang.BinaryTranslator(self.domain_path, False)
        # self.pddl_gen = PDDLGenerator(self.data, args.domain_path, args.save_dir, args.version)

    def read_config(self, config_file):
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)
    
    def get_problem(self, instance_path: str, domain_path: str):
        reader = PDDLReader(raise_on_error=True)
        reader.parse_domain(domain_path)
        return reader.parse_instance(instance_path)

    def decouple_encoding(self, encoding):
        # encoding = config_data["encoded_objects"]
        enc_list = [ (key, encoding[key]) for key in encoding ]
        enc_list.sort(key=lambda x:x[0])
        keys, items = zip(*enc_list)
        return keys, items

    def get_shuffled_encoding(self, sorted_keys, sorted_items):
        keys = sorted_keys
        items = list(sorted_items)
        random.shuffle(items)
        enc_dict = {}
        for i in range(len(keys)):
            enc_dict[keys[i]] = items[i]
        return enc_dict

    def get_encoding_for_pddl(self, encoding):
        pddl_enc = {}
        for key in encoding:
            pddl_enc[key] = '_'.join(encoding[key].strip('"').replace("\'", " ").split())
        return pddl_enc    
    
    def instance_to_text(self, instance_path):
        return self.translator(instance_path)
        
 
    def generate_dataset(self, pddl_path_list, split_name, gen_plan=True, checker_dump=False):
        dataset_dir = os.path.join(self.save_dir, split_name)
        os.makedirs(dataset_dir, exist_ok=True)

        object_dict = self.config['encoded_objects']
        keys, items = self.decouple_encoding(object_dict)
        # for key in object_dict:
        #     object_dict[key] = '_'.join(object_dict[key].split())
        encoded_pddl_dir = os.path.join(dataset_dir, "instances")
        os.makedirs(encoded_pddl_dir, exist_ok=True)
        encoded_plan_dir = os.path.join(dataset_dir, "plans")
        os.makedirs(encoded_plan_dir, exist_ok=True)
        dataset = []
        filename_template = "instance-{}.pddl"
        planname_template = "instance-{}.plan"
        for i, cur_entry in enumerate(pddl_path_list):
            cur_instance, cur_plan = cur_entry
            data = self.config
            if self.shuffle:
                object_dict = self.get_shuffled_encoding(keys, items)
                data = deepcopy(self.config)
                data["encoded_objects"] = object_dict
            
            pddl_encoding = self.get_encoding_for_pddl(object_dict)
            
            pddl_content = Path(cur_instance).read_text()
            encoded_pddl = naive_variable_replacement(pddl_content, pddl_encoding)
            pddl_path = os.path.join(encoded_pddl_dir, filename_template.format(i))
            
            with open(pddl_path, "w") as fout:
                fout.write(encoded_pddl)

            res = self.instance_to_text(pddl_path)
            
            if checker_dump:
                INIT = ""
                GOAL = res[0]
                ANSWER = res[1]
                entry = {
                    "path": pddl_path,
                    "init": INIT,
                    "goal": GOAL,
                    "answer": ANSWER
                }

            else: # normal routine
                GOAL = res[0] 
                GOAL_PDDL = res[1]
                
                constrained = False
                if len(res) > 2:
                    constrained = True
                    dumped_constr = res[2]
                
                ctx_prev, _, ctx_succ = extract_context_goal_tuple(encoded_pddl)
                encoded_pddl = ctx_prev + GOAL_PDDL + ctx_succ
                
                with open(pddl_path, "w") as fout:
                    fout.write(encoded_pddl)
            
                # TODO This is using an existing plan rather than gen plan. CHange the symbol
                if gen_plan:
                    plan_content = Path(cur_plan).read_text()
                    encoded_plan = naive_variable_replacement(plan_content, pddl_encoding)
                    plan_path = os.path.join(encoded_plan_dir, planname_template.format(i))
                    with open(plan_path, "w") as fout:
                        fout.write(encoded_plan)
                
                # for compatibility
                INIT = ""
                entry = {
                    "path": pddl_path,
                    "init": INIT,
                    "goal": GOAL,
                    "goal_pddl": GOAL_PDDL
                }
                if gen_plan:
                    entry["plan"] = plan_path
                if constrained:
                    entry["constr"] = dumped_constr
                
            dataset.append(entry)
        print(f"{split_name} {len(dataset)} entries generated.")
        
        # shuffle
        random.shuffle(dataset)
        dataset_path = os.path.join(dataset_dir, "data.txt")
        with open(dataset_path, "w") as f:
            for entry in dataset:
                dumped_entry = json.dumps(entry)
                f.write(dumped_entry + "\n")
        return dataset_path

constr_translator_dict = {
    "standard_stack": gen_lang.StandardTranslator,
    "stack_seq_b2t": lambda domain_path: gen_lang.StackSeqTranslator(domain_path, reversed=False),
    "stack_seq_t2b": lambda domain_path: gen_lang.StackSeqTranslator(domain_path, reversed=True),
    "stack_seq_t2b_rev": lambda domain_path:  gen_lang.StackSeqTranslator(domain_path, reversed=True, rev_pddl_order=True),
    "constr_h1": gen_lang.HeightConstrSampler,
    "constr_heq": gen_lang.HeightEqualConstrSampler,
    "constr_hprime": gen_lang.HeightPrimeConstrSampler,
    "constr_c1": gen_lang.ColorBinaryTranslator,
    "constr_ceq": gen_lang.ColorEqualConstrSampler
}

def gen_constr_data_routine(args, loader, config):
    dataset_template = config["dataset_template"]
    n_obj_list = config["n_obj_list"]
    pddl_range_dict = config["range_dict"]
    shuffling = config["shuffled"]
    uniform_dataset_configs = [ (n, s, m) for n in n_obj_list 
                               for s in shuffling for m in pddl_range_dict ]
    
    for n, s, m in uniform_dataset_configs:
        dataset = []
        i_start, i_end = pddl_range_dict[m]
        loader(dataset, n, i_start, i_end)
        gen_config = os.path.join(args.root_dir, config["encoding"])
        generator = DataGenerator(
            config=gen_config, 
            save_dir=args.save_dir, 
            shuffle=s, 
            domain_path=args.domain_path,
            translator=constr_translator_dict[args.task_type](args.domain_path))
        generator.generate_dataset(dataset, 
                        split_name=dataset_template.format(obj=n, mode=m), 
                        gen_plan=False)

def dump_check_ft_data(args, config):
    dataset_template = config["dataset_template"]
    checker_name_template = args.checker_name_template
    n_obj_list = config["n_obj_list"]

    shuffling = config["shuffled"]
    uniform_dataset_configs = [ (n, s) for n in n_obj_list 
                               for s in shuffling ]
    domain_checker_dict = {
        gen_lang.ObjectListSampler: "obj_list",
        gen_lang.ColorListSampler: "color_list",
        gen_lang.OnPredicateSampler: "on_pred",
        gen_lang.TablePredicateSampler: "table_pred",
        gen_lang.ClearPredicateSampler: "clear_pred"
    }
    for n, s in uniform_dataset_configs:
        for translator, t_name in domain_checker_dict.items():
            source_split_name = dataset_template.format(obj=n, shuffled=s, mode="test")
            split_name = checker_name_template.format(dataset=dataset_template.format(obj=n, shuffled=s, mode="check"), checker=t_name)
            dataset_path = os.path.join(args.save_dir, source_split_name, "data.txt")
            gen_domain_checker_data(args.domain_path, dataset_path, args.check_ft_template.format(split_name),
                                    translator(args.domain_path))

def dump_constr_ft_data(args, config, mode):
    dataset_template = config["dataset_template"]
    n_obj_list = config["n_obj_list"]
    pddl_range_dict = config["range_dict"]
    shuffling = config["shuffled"]
    uniform_dataset_configs = [ (n, s, m) for n in n_obj_list 
                               for s in shuffling for m in pddl_range_dict ]
    
    for n, s, m in uniform_dataset_configs:
        split_name = dataset_template.format(obj=n, mode=m)
        dataset_path = os.path.join(args.save_dir, split_name, "data.txt")
        if mode == "goal":
            gen_goal_finetuning_data(args.domain_path, dataset_path, args.goal_ft_template.format(split_name))
        elif mode == "plan":
            gen_plan_finetuning_data(args.domain_path, dataset_path, args.plan_ft_template.format(split_name))
        elif mode == "list":
            gen_goal_finetuning_data(args.domain_path, 
                                     dataset_path, 
                                     args.list_ft_template.format(split_name),
                                     example_constructor=construct_list_example)
        elif mode == "lang":
            gen_goal_finetuning_data(args.domain_path, 
                                     dataset_path, 
                                     args.lang_ft_template.format(split_name),
                                     example_constructor=construct_lang_goal_example)
        
gen_dict = {
    "standard_stack": gen_constr_data_routine,
    "stack_seq_b2t": gen_constr_data_routine,
    "stack_seq_t2b": gen_constr_data_routine,
    "stack_seq_t2b_rev": gen_constr_data_routine,
    "constr_h1": gen_constr_data_routine,
    "constr_heq": gen_constr_data_routine,
    "constr_hprime": gen_constr_data_routine,
    "constr_c1": gen_constr_data_routine,
    "constr_ceq": gen_constr_data_routine
} 

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    # TODO change this to domain dir + domain name?
    parser.add_argument("--domain_path", type=str, required=True)
    parser.add_argument("--save_dir", type=str, default="./dataset/blocksworld", required=True, 
                        help="directory where dataset and encoded instances are saved")
    # parser.add_argument("--shuffle", action="store_true", help="shuffle object encodings")
    parser.add_argument("--task_type", type=str, required=True, choices=list(gen_dict.keys()))
    parser.add_argument("--dump_ft", type=str, help="dump finetuning datasets", choices=["plan", "goal", "list", "lang", "check"])
    # parser.add_argument("--check", action="store_true")
    # add arguments
    args = parser.parse_args()
    return args

def main(args, config):
    def loader(dataset, n_obj, i_start, i_end):
        filename_template = args.filename
        pddl_dir_template = args.pddl_dir
        plan_dir_template = args.plan_dir
        pddl_dir = pddl_dir_template.format(n_obj)
        plan_dir = plan_dir_template.format(n_obj)
        load_pddl_paths_by_range(dataset, pddl_dir, plan_dir, filename_template, i_start, i_end)
    
    # def idx_loader(dataset, n_obj, idx):
    #     filename_template = args.filename
    #     pddl_dir_template = args.pddl_dir
    #     plan_dir_template = args.plan_dir
    #     pddl_dir = pddl_dir_template.format(n_obj)
    #     plan_dir = plan_dir_template.format(n_obj)
    #     load_pddl_paths_by_idx(dataset, pddl_dir, plan_dir, filename_template, idx) 
    
    if args.dump_ft != None:
        if args.dump_ft == "check":
            dump_check_ft_data(args, config[args.task_type])
        else:
            dump_constr_ft_data(args, config[args.task_type], args.dump_ft)
    else:
        gen_dict[args.task_type](args, loader, config[args.task_type])
    

if __name__ == "__main__":
    random.seed(10)
    args = parse_args()
    assert("ROOT_DIR" in os.environ)
    root_dir = os.environ["ROOT_DIR"]
    with open(args.config) as f_conf:
        config = yaml.safe_load(f_conf)
        args.checker_name_template = config["checker_name_template"]
        pddl_dir = os.path.join(root_dir, config["pddl_dir_template"])
        plan_dir = os.path.join(root_dir, config["plan_dir_template"])
        
        args.goal_ft_template = os.path.join(root_dir, config["goal_finetuning_template"])
        args.plan_ft_template = os.path.join(root_dir, config["plan_finetuning_template"])
        args.list_ft_template = os.path.join(root_dir, config["list_finetuning_template"])
        args.lang_ft_template = os.path.join(root_dir, config["lang_finetuning_template"])
        args.check_ft_template = os.path.join(root_dir, config["check_finetuning_template"])
        args.filename = config["instances_template"]
        args.pddl_dir = pddl_dir
        args.plan_dir = plan_dir
        args.root_dir = root_dir
        main(args, config)
    

