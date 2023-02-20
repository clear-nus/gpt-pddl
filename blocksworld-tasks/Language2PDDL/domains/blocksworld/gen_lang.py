import random
from collections import defaultdict
from tarski.io import PDDLReader
from tarski.syntax.formulas import *
from pathlib import Path
from copy import deepcopy
from Language2PDDL.scripts.utils import extract_context_goal_tuple
from Language2PDDL.domains.blocksworld.simulator import BlocksWorldManager, parse_problem_file

def get_goal_str(instance_path):
    problem = Path(instance_path).read_text()
    return extract_context_goal_tuple(problem)[1]

def naive_variable_replacement(problem, object_dict):
    vars = problem.split(' ')
    output = []
    for var in vars:
        if var in object_dict:
            output.append(object_dict[var])
            continue
        if len(var) > 1 and var[1] == ')' and var[0] in object_dict:
            output.append(object_dict[var[0]] + var[1:])
            continue
        output.append(var)
        continue
    return " ".join(output)

class GoalTranslatorBase:
    def __init__(self, domain_path):
        self.domain_path = domain_path

    def instance_to_text(self, instance_path):
        '''
        :param instance: the **path** to the instance(problem) file
        :return (GOAL_NL, GOAL_PDDL)
        '''
        raise NotImplementedError

    def __call__(self, instance_path):
        return self.instance_to_text(instance_path)

#### start of code from gpt-plan-benchmark ####

class BinaryTranslator(GoalTranslatorBase):
    def __init__(self, domain_path, shuffle=False):
        '''
        :param shuffle: whether to shuffle the order of predicates in the goal
        '''
        super().__init__(domain_path)
        self.predicate_dict = {
            "ontable": "the {} is on the table",
            "clear": "the {} is clear",
            "handempty": "the hand is empty",
            "on": "the {} is on top of the {}"
        }
        self.shuffle = shuffle

    def instance_to_text(self, instance_path):
        reader = PDDLReader(raise_on_error=True)
        reader.parse_domain(self.domain_path)
        instance = reader.parse_instance(instance_path)
        return (self.parse_problem(instance, self.shuffle), get_goal_str(instance_path))

    def get_sorted(self, init_atoms):
        return sorted(init_atoms, key=lambda x: x.symbol.name+" "+" ".join([subterm.name for subterm in x.subterms]))
    
    def get_natural_name(self, object):
        return " ".join(object.split("_"))

    def parse_problem(self, problem, shuffle):
        '''
        :param problem: the result problem object parsed by tarski
        :param data: config dict, should contain 'predicates' and 'encoded_objects' key
        '''
        def parse(init_goal_preds):
            TEXT = ""
            predicates = []

            init_goal_preds = list(init_goal_preds)
            for atom in init_goal_preds:
                objs = []
                for subterm in atom.subterms:
                    objs.append(self.get_natural_name(subterm.name))
                predicates.append(self.predicate_dict[atom.symbol.name].format(*objs))
            if len(predicates) > 1:
                TEXT += ", ".join(predicates[:-1]) + f" and {predicates[-1]}"
            else:
                TEXT += predicates[0]
            return TEXT
        goal_preds = self.get_sorted(problem.goal.subformulas) if hasattr(problem.goal, 'subformulas') else [problem.goal]
        if shuffle:
            random.shuffle(goal_preds)
        GOAL = parse(goal_preds)

        return GOAL

#### end of code from gpt-plan-benchmark ####

counting_list = ["zero", "one", "two", "three", "four", 
                 "five", "six", "seven", "eight", 
                 "nine", "ten", "eleven", "twelve"]



def sample_verb():
    return random.choice(["Build", "Create", "Make"])
        
class StackTranslator(GoalTranslatorBase):
    def __init__(self, domain_path, reversed=False):
        super().__init__(domain_path)
        self.reversed = reversed

    def instance_to_text(self, instance_path):
        return self.instance_to_text_tower(self.domain_path, instance_path)

    def get_natural_name(self, obj):
        return " ".join(obj.split("_"))

    def instance_to_text_tower(self, domain_path, instance_path):    
        objects, _, goals = parse_problem_file(domain_path, instance_path)
        goal_stacks, _, _, _, _ = BlocksWorldManager.facts_to_stack_state(objects, goals, extend=True)
        # counting_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight"]
        # GOAL = "There {} {} {}. ".format("exist" if len(goal_stacks) > 1 else "exists", counting_list[len(goal_stacks)], "stacks" if len(goal_stacks) > 1 else "stack")
        GOAL = "{} {} {}. ".format(sample_verb(), counting_list[len(goal_stacks)], "stacks" if len(goal_stacks) > 1 else "stack")
        
        indexing_list = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth" ]
        for i, tower in enumerate(goal_stacks):
            GOAL += "In the {} stack, ".format(indexing_list[i])
            if len(tower) == 1:
                GOAL += "there is the {} only. ".format(self.get_natural_name(tower[0]))
            else:
                GOAL += "there are "
                if self.reversed:
                    tower.reverse()
                for j, object in enumerate(tower):
                    if j != len(tower)-1:
                        GOAL += "the " + self.get_natural_name(object) + ", "
                    else:
                        GOAL += "and the " + self.get_natural_name(object)
                        GOAL += " from bottom to top. " if not self.reversed else " from top to bottom. "
        # not using the init language anyway
        return (GOAL.strip(), get_goal_str(instance_path))

###############################
# Constraint Class Definition #
###############################

def stacks_to_prdicates_blocksworld(stacks, reversed=False):
    goals = []
    for stack in stacks:
        stack_goal = []
        stack_goal.append(["ontable", stack[0]])
        for i in range(len(stack)-1):
            stack_goal.append(["on", stack[i+1], stack[i]])
        stack_goal.append(["clear", stack[-1]])
        
        if reversed:
            stack_goal.reverse()
        goals.extend(stack_goal)
    return goals

class ConstrSpecBase:
    def __init__(self):
        pass
    
    def evaluate(self, goal_stacks, objects):
        raise NotImplementedError
    
    def get_example(self, domain_path, instance_path):
        objects, _, _ = parse_problem_file(domain_path, instance_path)
        goals = self.solve_parsed(objects)
        
        goal_stacks = BlocksWorldManager.facts_to_stack_state(objects, goals, extend=True)[0]
        if not self.evaluate(goal_stacks, objects):
            print("self check error: ", goal_stacks)
        
        goals = [ "(" + " ".join(x) + ")" for x in goals ]
        goal = "(:goal\n(and\n{}\n)\n)".format("\n".join(goals))
        return goal
        
    def solve_parsed(self, objects):
        raise NotImplementedError
    
    def constr_to_text(self):
        raise NotImplementedError
    
    def dump(self):
        raise NotImplementedError
    
    @classmethod
    def load(cls, dumped: dict):
        cls_name = dumped["class"]
        dumped.pop("class")
        return eval(cls_name)(**dumped)

class BinaryConstr(ConstrSpecBase):
    def __init__(self, goal_stacks):
        self.goal_stacks = goal_stacks
        self.hash_goal_stacks = [ self.hash_stack(s) for s in goal_stacks ]

    def hash_stack(self, stack):
        return " ".join(stack)
    
    def get_natural_name(self, obj):
        return " ".join(obj.split("_"))
      
    def evaluate(self, stacks, objects):
        # No repeated stacks here so no need to make a dict
        hash_stacks = [ self.hash_stack(stack) for stack in stacks ]
        for seq in self.hash_goal_stacks:
            if not seq in hash_stacks:
                return False
        return True

    def solve_parsed(self, objects):
        return stacks_to_prdicates_blocksworld(self.goal_stacks)
    
    def constr_to_text(self):
        goal_stacks = deepcopy(self.goal_stacks)
        GOAL = "{} {} {}. ".format(sample_verb(), counting_list[len(goal_stacks)], "stacks" if len(goal_stacks) > 1 else "stack")
        
        self.predicate_dict = {
            "ontable": "the {} is on the table",
            "clear": "there is nothing on the {}",
            "handempty": "the hand is empty",
            "on": "the {} is on top of the {}"
        }

        indexing_list = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth" ]
        for i, tower in enumerate(goal_stacks):
            GOAL += "In the {} stack, ".format(indexing_list[i])
            GOAL += "the {} is on the table, ".format(self.get_natural_name(tower[0]))
            
            for j in range(1, len(tower)):
                GOAL += "the {} is on top of the {}, ".format(self.get_natural_name(tower[j]), self.get_natural_name(tower[j-1]))
            
    
            GOAL += "and there is nothing on the {}. ".format(self.get_natural_name(tower[-1]))        
        return GOAL.strip()
    
    def dump(self):
        return {
            "class": type(self).__name__,
            "goal_stacks": self.goal_stacks,
        }
       

class StackSeqConstr(ConstrSpecBase):
    def __init__(self, goal_stacks, reversed, rev_pddl_order=False):
        self.goal_stacks = goal_stacks
        self.hash_goal_stacks = [ self.hash_stack(s) for s in goal_stacks ]
        self.reversed = reversed
        self.rev_pddl_order = rev_pddl_order
      
    def hash_stack(self, stack):
        return " ".join(stack)
    
    def get_natural_name(self, obj):
        return " ".join(obj.split("_"))
      
    def evaluate(self, stacks, objects):
        # No repeated stacks here so no need to make a dict
        hash_stacks = [ self.hash_stack(stack) for stack in stacks ]
        for seq in self.hash_goal_stacks:
            if not seq in hash_stacks:
                return False
        return True
        # for seq in hash_stacks:
        #     if not seq in self.hash_goal_stacks:
        #         return False
        # return True

    def solve_parsed(self, objects):
        return stacks_to_prdicates_blocksworld(self.goal_stacks, reversed=self.rev_pddl_order)
    
    def constr_to_text(self):
        goal_stacks = deepcopy(self.goal_stacks)
        GOAL = "{} {} {}. ".format(sample_verb(), counting_list[len(goal_stacks)], "stacks" if len(goal_stacks) > 1 else "stack")
        
        indexing_list = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth" ]
        for i, tower in enumerate(goal_stacks):
            GOAL += "In the {} stack, ".format(indexing_list[i])
            if len(tower) == 1:
                GOAL += "there is the {} only. ".format(self.get_natural_name(tower[0]))
            else:
                GOAL += "there are "
                if self.reversed:
                    tower.reverse()
                for j, object in enumerate(tower):
                    if j != len(tower)-1:
                        GOAL += "the " + self.get_natural_name(object) + ", "
                    else:
                        GOAL += "and the " + self.get_natural_name(object)
                        GOAL += " from bottom to top. " if not self.reversed else " from top to bottom. "
        
        return GOAL.strip()
    
    def dump(self):
        return {
            "class": type(self).__name__,
            "goal_stacks": self.goal_stacks,
            "reversed": self.reversed
        }
       
 
class HeightSingleConstr(ConstrSpecBase):
    def __init__(self, height):
        self.height = height
        
    def evaluate(self, goal_stacks, objects):
        for stack in goal_stacks:
            if len(stack) == self.height:
                return True
        return False
    
    def solve_parsed(self, objects):
        objects = list(objects) # copy
        random.shuffle(objects)
        return stacks_to_prdicates_blocksworld([ objects[:self.height], ])
    
    def constr_to_text(self):
        height = self.height
        # GOAL = "There is a stack that contains {} {}.".format(counting_list[height], "block" if height == 1 else "blocks")
        GOAL = "{} a stack that contains {} {}.".format(sample_verb(), counting_list[height], "block" if height == 1 else "blocks")
        
        return GOAL
    
    def dump(self):
        return {
            "class": type(self).__name__,
            "height": self.height    
        }
    
class HeightEqualConstr(ConstrSpecBase):
    def __init__(self, num):
        self.num = num
     
    def evaluate(self, goal_stacks, objects):
        if not len(goal_stacks) == self.num:
            return False
        # loose metric:
        # npstack = len(goal_stacks[0])
        npstack = len(objects) // self.num
        for stack in goal_stacks:
            if len(stack) != npstack:
                return False
        return True
    
    def solve_parsed(self, objects):
        objects = list(objects) # copy
        random.shuffle(objects)
        h = len(objects) // self.num
        stacks = [
            objects[lo:lo+h] for lo in range(0, h*self.num, h) 
        ]
        return stacks_to_prdicates_blocksworld(stacks)
       
    def constr_to_text(self):
        # GOAL = "There are {} stacks that are the same height.".format(counting_list[self.num])
        # GOAL = "{} exactly {} stacks that are of the same height.".format(sample_verb(), counting_list[self.num])
        GOAL = "Using all blocks specified in the problem, {} exactly {} stacks that are of the same height.".format(sample_verb().lower(), counting_list[self.num])
        
        return GOAL

    def dump(self):
        return {
            "class": type(self).__name__,
            "num": self.num    
        }
        
class HeightPrimeConstr(ConstrSpecBase):       
    def prime_check(self, x):
        for i in range(2, x):
            if x % i == 0:
                return False
        return True

    def evaluate(self, goal_stacks, objects):
        # Loose metric
        for stack in goal_stacks:
            if self.prime_check(len(stack)):
                return True
        return False
        
    def solve_parsed(self, objects):
        objects = list(objects) # copy
        random.shuffle(objects)
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        h = random.choice(small_primes)
        while h > len(objects):
            h = random.choice(small_primes)
        return stacks_to_prdicates_blocksworld([ objects[:h], ])
        
    def constr_to_text(self):
        GOAL = "{} a stack with a prime number of blocks.".format(sample_verb())
        return GOAL
        
    def dump(self):
        return {
            "class": type(self).__name__
        }

def get_color_seq_dict(stacks):
        color_seqs = defaultdict(int)
        for stack in stacks:
            color_seq = " ".join([ x.split("_")[0] for x in stack ])
            color_seqs[color_seq] += 1
        return color_seqs
            
class ColorConstr(ConstrSpecBase):
    def __init__(self, goal_stacks):
        self.goal_stacks = goal_stacks
        self.color_seqs = get_color_seq_dict(goal_stacks)

    def evaluate(self, stacks, objects):
        target_color_seqs = get_color_seq_dict(stacks)
        for seq in self.color_seqs:
            if not seq in target_color_seqs or target_color_seqs[seq] < self.color_seqs[seq]:
                return False
        return True    
    
    def solve_parsed(self, objects):
        return stacks_to_prdicates_blocksworld(self.goal_stacks)
    
    def dump(self):
        return {
            "class": type(self).__name__,
            "goal_stacks": self.goal_stacks
        }
    
class ColorEqualConstr(ConstrSpecBase):
    def __init__(self, num):
        self.num = num
    
    def evaluate(self, goal_stacks, objects):
        if len(goal_stacks) != self.num:
            return False
        vis_map = { obj:False for obj in objects }
        for stack in goal_stacks:
            for block in stack:
                vis_map[block] = True
        for val in vis_map.values():
            if not val:
                return False
            
        color_dict = get_color_seq_dict(goal_stacks)
        for key in color_dict:
            color_seq = key.split()
            color = color_seq[0]
            for c in color_seq:
                if c != color: # not pure color
                    return False
        return True
    
    def solve_parsed(self, objects):
        objects = list(objects)
        random.shuffle(objects)
        color_dict = {}
        for obj in objects:
            color = obj.split("_")[0]
            if not color in color_dict:
                color_dict[color] = []
            color_dict[color].append(obj)
        sep_stacks = deepcopy(list(color_dict.values()))
        while len(sep_stacks) < self.num:
            max_len = 0
            max_len_idx = -1
            for i, ele in enumerate(sep_stacks):
                if len(ele) > max_len:
                    max_len = len(ele)
                    max_len_idx = i
            lo, hi = list(sep_stacks[max_len_idx][:max_len // 2]), list(sep_stacks[max_len_idx][max_len // 2:])
            sep_stacks[max_len_idx] = lo
            sep_stacks.append(hi)
        return stacks_to_prdicates_blocksworld(sep_stacks)
       
    def constr_to_text(self):
        GOAL = "Using all blocks specified in the problem, {} {} stacks where each stack comprises blocks with the same color.".format(sample_verb().lower(), counting_list[self.num])
        return GOAL

    def dump(self):
        return {
            "class": type(self).__name__,
            "num": self.num
        }

class DomainCheckerBase:
    def __init__(self):
        pass

    def evaluate(self, answer, objects, facts):
        raise NotImplementedError
    
    def solve_parsed(self, objects, facts):
        raise NotImplementedError

    def dump(self):
        raise NotImplementedError

# class ObjectListChecker(DomainCheckerBase):
#     def __init__(self):
#         self.objects = None

#     def evaluate(self, answer, objects, facts):
#         obj_seq = answer.split()
#         obj_set = set(obj_seq)
#         if not len(obj_set) == len(obj_seq):
#             return False # duplicating elements
#         for obj in objects:
#             if not obj in obj_set:
#                 return False # missing objects
#         if not len(obj_set) == len(objects):
#             return False # redundant objects
#         return True
    
#     def solve_parsed(self, objects, facts):
#         return " ".join(objects)
    
#     def dump(self):
#          return {
#             "class": type(self).__name__,
#          }



class ObjectListSampler(GoalTranslatorBase):
    def instance_to_text(self, instance_path):
        objects, _, _ = parse_problem_file(self.domain_path, instance_path)
        GOAL = "List all the objects that appear in the PDDL problem definition. Separate the objects by spaces."
        completion = " ".join(objects)
        return GOAL, completion
    
class ColorListSampler(GoalTranslatorBase):
    def get_color(self, obj):
        return obj.split("_")[0]
    
    def instance_to_text(self, instance_path):
        objects, _, _ = parse_problem_file(self.domain_path, instance_path)
        color_maps = {}
        for obj in objects:
            color = self.get_color(obj)
            if not color in color_maps:
                color_maps[color] = []

            color_maps[color].append(obj)
        color_list = list(color_maps.keys())
        color_list.sort()
        chosen_color = random.choice(color_list)
        GOAL = "List all the objects in the PDDL problem definition that has the {} color. Separate the objects by spaces.".format(chosen_color)
        completion = " ".join(color_maps[chosen_color])
        return GOAL, completion
    
class OnPredicateSampler(GoalTranslatorBase):
    def instance_to_text(self, instance_path):
        objects, facts, _ = parse_problem_file(self.domain_path, instance_path)
        query_fact = []
        on_fact_set = [ fact for fact in facts if fact[0] == "on" ]
        if len(on_fact_set) == 0:
            negate = True
            query_fact = ["on", objects[0], objects[1]]
        else:    
            query_fact = random.choice(on_fact_set)
            negate = random.random() < 0.5
            if negate:
                obj = random.choice(objects)
                while obj == query_fact[1] or obj == query_fact[2]:
                    obj = random.choice(objects)
                query_fact[1] = obj
        GOAL = "Determine whether the {} is on the top of the {} in the initial state. Answer with yes or no.".format(query_fact[1], query_fact[2])
        completion = "no" if negate else "yes"
        return GOAL, completion
    
class TablePredicateSampler(GoalTranslatorBase):
    def instance_to_text(self, instance_path):
        objects, facts, _ = parse_problem_file(self.domain_path, instance_path)
        on_table_set = [ fact[1] for fact in facts if fact[0] == "ontable" ]
        tset = set(on_table_set)
        not_on_table_set = [ obj for obj in objects if not obj in tset ]
        
        negate = random.random() < 0.5
        if negate:
            obj = random.choice(not_on_table_set)
        else:
            obj = random.choice(on_table_set)
        GOAL = "Determine whether the {} is on the table in the initial state. Answer with yes or no.".format(obj)
        completion = "no" if negate else "yes"
        return GOAL, completion
    
class ClearPredicateSampler(GoalTranslatorBase):
    def instance_to_text(self, instance_path):
        objects, facts, _ = parse_problem_file(self.domain_path, instance_path)
        clear_set = [ fact[1] for fact in facts if fact[0] == "clear" ]
        cset = set(clear_set)
        not_clear_set = [ obj for obj in objects if not obj in cset ]
        
        negate = random.random() < 0.5
        if negate:
            obj = random.choice(not_clear_set)
        else:
            obj = random.choice(clear_set)
        GOAL = "Determine whether there is nothing on the top of the {} in the initial state. Answer with yes or no.".format(obj)
        completion = "no" if negate else "yes"
        return GOAL, completion
    
#################################
# Constraint Sampler Definition #
#################################

class StandardTranslator(GoalTranslatorBase):
    def __init__(self, domain_path):
        super().__init__(domain_path)
    
    def instance_to_text(self, instance_path):
        objects, _, goals = parse_problem_file(self.domain_path, instance_path)
        goal_stacks, _, _, _, _ = BlocksWorldManager.facts_to_stack_state(objects, goals, extend=True)
        constr = BinaryConstr(goal_stacks)
        return (constr.constr_to_text(), constr.get_example(self.domain_path, instance_path), constr.dump())
 

class StackSeqTranslator(GoalTranslatorBase):
    def __init__(self, domain_path, reversed, rev_pddl_order=False):
        super().__init__(domain_path)
        self.reversed = reversed
        self.rev_pddl_order = rev_pddl_order
    
    def instance_to_text(self, instance_path):
        objects, _, goals = parse_problem_file(self.domain_path, instance_path)
        goal_stacks, _, _, _, _ = BlocksWorldManager.facts_to_stack_state(objects, goals, extend=True)
        constr = StackSeqConstr(goal_stacks, reversed=self.reversed, rev_pddl_order=self.rev_pddl_order)
        return (constr.constr_to_text(), constr.get_example(self.domain_path, instance_path), constr.dump())
  
class HeightConstrSampler(GoalTranslatorBase):        
    def instance_to_text(self, instance_path):
        objects, _, goals = parse_problem_file(self.domain_path, instance_path)
        goal_stacks, _, _, _, _ = BlocksWorldManager.facts_to_stack_state(objects, goals, extend=True)
        height = len(random.choice(goal_stacks))
        constr = HeightSingleConstr(height)
        return (constr.constr_to_text(), constr.get_example(self.domain_path, instance_path), constr.dump())

class HeightEqualConstrSampler(GoalTranslatorBase):        
    def instance_to_text(self, instance_path):
        objects, _, goals = parse_problem_file(self.domain_path, instance_path)
        # goal_stacks, _, _, _, _ = BlocksWorldManager.facts_to_stack_state(objects, goals, extend=True)
        n_obj = len(objects)
        cand = [ x for x in range(2, n_obj) if n_obj % x == 0 ]
        
        num = random.choice(cand)
        constr = HeightEqualConstr(num)
        return (constr.constr_to_text(), constr.get_example(self.domain_path, instance_path), constr.dump())


class HeightPrimeConstrSampler(GoalTranslatorBase):
    def instance_to_text(self, instance_path):
        constr = HeightPrimeConstr()
        return (constr.constr_to_text(), constr.get_example(self.domain_path, instance_path), constr.dump())

  
class ColorBinaryTranslator(StackTranslator):   
    def get_natural_name(self, object):
        return " ".join(object.split("_")[:2])
    
    def instance_to_text(self, instance_path):
        return self.instance_to_text_tower(self.domain_path, instance_path)

    def instance_to_text_tower(self, domain_path, instance_path):    
        objects, _, goals = parse_problem_file(domain_path, instance_path)
        goal_stacks, _, _, _, _ = BlocksWorldManager.facts_to_stack_state(objects, goals, extend=True)
        # counting_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight"]
        # GOAL = "There {} {} {}. ".format("exist" if len(goal_stacks) > 1 else "exists", counting_list[len(goal_stacks)], "stacks" if len(goal_stacks) > 1 else "stack")
        GOAL = "{} {} {}. ".format(sample_verb(), "a" if len(goal_stacks) == 1 else counting_list[len(goal_stacks)], "stacks" if len(goal_stacks) > 1 else "stack")
        indexing_list = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth" ]
        
        def get_article(obj):
            # naive rule
            if obj[0] in ['a', 'e', 'o']:
                return "an"
            return "a"
        
        for i, tower in enumerate(goal_stacks):
            if len(goal_stacks) == 1:
                GOAL += "In this stack, "
            else:
                GOAL += "In the {} stack, ".format(indexing_list[i])  
            natural_tower = [ self.get_natural_name(x) for x in tower ]
            if len(tower) == 1:
                GOAL += "there is {} {} only. ".format(get_article(natural_tower[0]), natural_tower[0])
            else:
                for j in range(1, len(tower)):
                    if j == len(tower)-1 and j != 1:
                        GOAL += "and "
                    # GOAL += "a " if j == 1 else "the "
                    GOAL += "{} ".format(get_article(natural_tower[j]))
                    # GOAL += natural_tower[j] + " is on top of {} {}".format(get_article(natural_tower[j-1]), natural_tower[j-1])
                    GOAL += natural_tower[j] + " is on top of {} {}".format("the" if j>1 else get_article(natural_tower[j-1]), natural_tower[j-1])
                    GOAL += ", " if j < len(tower)-1 else ". "
        # return (GOAL.strip(), get_goal_str(instance_path), ColorConstr(goal_stacks).dump())
        constr = ColorConstr(goal_stacks)
        return (GOAL.strip(), constr.get_example(self.domain_path, instance_path), constr.dump())
        # return (GOAL.strip(), get_goal_str(instance_path), constr.dump())

class ColorEqualConstrSampler(GoalTranslatorBase):
    def instance_to_text(self, instance_path):
        objects, _, _ = parse_problem_file(self.domain_path, instance_path)
        color_dict = {}
        for obj in objects:
            color = obj.split("_")[0]
            if not color in color_dict:
                color_dict[color] = 0
            color_dict[color] += 1
        num = random.choice(range(len(color_dict), len(color_dict)+3))
        constr = ColorEqualConstr(num)
        return (constr.constr_to_text(), constr.get_example(self.domain_path, instance_path), constr.dump())



