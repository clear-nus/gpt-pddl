from planner import compute_naive_plan, compute_plan
import os
import argparse
from tqdm import tqdm
def generate_unencoded_plan(domain_path, dataset_dir, save_dir, heuristics=False):
    os.makedirs(save_dir, exist_ok=True)
    for prob_basename in tqdm(os.listdir(dataset_dir)):
        prob_path = os.path.join(dataset_dir, prob_basename)
        if heuristics:
            plan = compute_naive_plan(domain_path, prob_path)
        else:
            plan = compute_plan(domain_path, prob_path)
        plan_basename = prob_basename.split(".")[0] + ".plan"
        with open(os.path.join(save_dir, plan_basename), "w") as f:
            f.write(plan)
            
            
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain_path", type=str, required=True)
    parser.add_argument("--dataset_dir", type=str, required=True)
    parser.add_argument("--save_dir", type=str, required=True)
    parser.add_argument("--strategy", type=str, default="fd", choices=["naive", "fd", "optimal"])
    # TODO: use this strategy flag
    args = parser.parse_args()
    return args
    
            
if __name__ == "__main__":
    args = parse_args()
    generate_unencoded_plan(
        domain_path=args.domain_path, 
        dataset_dir=args.dataset_dir, 
        save_dir=args.save_dir)
    
           
           

        