import os
import argparse
import yaml
import random
import hashlib
from tarski.io import PDDLReader
from tarski.syntax.formulas import *

class PDDLGenerator():
    def __init__(self, data, domain_path, save_dir, version):
        self.data = data
        self.domain = domain_path
        self.instances_dir = os.path.join(save_dir, "instances", version)
        self.instances_template = os.path.join(self.instances_dir, data['instances_template'])
        os.makedirs(self.instances_dir, exist_ok=True)
    
        self.hashset = set()

    def instance_ok(self, domain, instance):
        reader = PDDLReader(raise_on_error=True)
        reader.parse_domain(domain)
        reader.parse_instance(instance)
        if isinstance(reader.problem.goal, Tautology):
            return False
        elif isinstance(reader.problem.goal, Atom):
            if reader.problem.goal in reader.problem.init.as_atoms():
                return False
        else:
            if (all([i in reader.problem.init.as_atoms() for i in reader.problem.goal.subformulas])):
                return False
        return True

    def add_existing_files_to_hash_set(self):
        for i in os.listdir(self.instances_dir):
            f = open(os.path.join(self.instances_dir, i), "r")
            pddl = f.read()
            self.hashset.add(hashlib.md5(pddl.encode('utf-8')).hexdigest())
        return len(self.hashset)

    def gen_goal_directed_instances(self, n_obj=0):
        trial = self.data['max_trial']
        n = self.data['n_instances']
        if n_obj < 4:
            return
        else:
            n_objs = [ n_obj, ]
        CMD = "${{ROOT_DIR}}/domains/blocksworld/blocksworld/blocksworld 4 {}"
        c = self.add_existing_files_to_hash_set()
        for obj in n_objs:
            if c >= n:
                break
            cmd_exec = CMD.format(obj)
            for _ in range(trial):
                if c >= n:
                    break
                with open(self.instances_template.format(c), "w+") as fd:
                    pddl = os.popen(cmd_exec).read()
                    hash_of_instance = hashlib.md5(pddl.encode('utf-8')).hexdigest()
                    if hash_of_instance in self.hashset:
                        print("[+]: Same instance, skipping...")
                        continue
                    self.hashset.add(hash_of_instance)
                    fd.write(pddl)

                inst_to_parse = self.instances_template.format(c)
                if self.instance_ok(self.domain, inst_to_parse):
                    c += 1
                else:
                    print("[-]: Instance not valid")
                    self.hashset.remove(hash_of_instance)
                    os.remove(inst_to_parse)
                    continue
        
        print(f"[+]: A total of {c} instances have been generated")

    def gen_generalization_instances(self):
        def gen_instance(objs):
            text = "(define (problem BW-generalization-4)\n(:domain blocksworld-4ops)"
            text += "(:objects " + " ".join(objs) + ")\n"
            text += "(:init \n(handempty)\n"

            for obj in objs:
                text += f"(ontable {obj})\n"

            for obj in objs:
                text += f"(clear {obj})\n"

            text += ")\n(:goal\n(and\n"

            obj_tuples = list(zip(objs, objs[1:]))
            # obj_tuples.reverse() # TODO: this improves considerably Davinci t4

            for i in obj_tuples:
                text += f"(on {i[0]} {i[1]})\n"

            text += ")))"
            return text

        n = self.data['n_instances'] + 2
        objs = self.data['encoded_objects']
        encoded_objs = list(objs.keys())
        start = self.add_existing_files_to_hash_set()

        print("[+]: Making generalization instances for blocksworld")
        for c in range(start, n):
            n_objs = random.randint(3, len(objs))
            random.shuffle(encoded_objs)
            objs_instance = encoded_objs[:n_objs]
            instance = gen_instance(objs_instance)

            if hashlib.md5(instance.encode('utf-8')).hexdigest() in self.hashset:
                print("INSTANCE ALREADY IN SET, SKIPPING")
                continue

            with open(self.instances_template.format(c), "w+") as fd:
                fd.write(instance)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    # TODO change this to domain dir + domain name?
    parser.add_argument("--domain_path", type=str, required=True)
    parser.add_argument("--save_dir", type=str, required=True, 
                        help="instances are saved in $(save_dir)/instances/$(version).\n"
                        "dataset is saved in $(save_dir)/dataset/$(split)")
    parser.add_argument("--version", type=str, required=True,
                        help="instances are saved in $(save_dir)/instances/$(version).")
    parser.add_argument("--object", type=int, default=0, help="Number of objects appearing in problem")
    
    
    # add arguments
    args = parser.parse_args()
    return args

def main(args):
    with open(args.config) as f:
        data = yaml.safe_load(f)
    generator = PDDLGenerator(
        data=data, 
        domain_path=args.domain_path, 
        save_dir=args.save_dir, 
        version=args.version)
    generator.gen_goal_directed_instances(args.object)

if __name__ == "__main__":
    random.seed(10)
    args = parse_args()
    main(args)
    

