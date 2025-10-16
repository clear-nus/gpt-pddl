import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import pygame.freetype
from pygame.locals import *

import yaml
import argparse
from pathlib import Path
from tarski.io import PDDLReader
from tarski.syntax import CompoundFormula, formulas, Tautology, Atom

import networkx as nx

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300

object_color_map = {
    "red_block": (240, 0, 0),
    "blue_block": (0, 0, 240),
    "orange_block": (255, 165, 0),
    "yellow_block": (240, 240, 0),
    "white_block": (240, 240, 240),
    "magenta_block": (240, 0, 240),
    "black_block": (50, 50, 50),
    "cyan_block": (0, 100, 100)
}

class BlocksWorldManager():
    def __init__(self):
        self.objects = None
        self.facts = None
        self.stacks = None
        self.holding = None
        self.prev_map = None
        self.next_map = None
        
    
    @classmethod
    def facts_to_stack_state(cls, objects, facts, extend=False, strict=False):
        prev_map = {}
        next_map = {}
        vis_map = {}
        holding = None
        for obj in objects:
            prev_map[obj] = None
            next_map[obj] = None
            vis_map[obj] = False
            
        G = nx.DiGraph()
        for obj in objects:
            G.add_node(obj)
        G.add_node("table")
        G.add_node("air")
        
        # TODO rewrite this with dict
        for fact in facts:
            if fact[0] == 'handempty':
                if holding and holding != 'empty':
                    # print("handempty error")
                    return False
                holding = 'empty'
            elif fact[0] == 'holding':
                obj = fact[1]
                if holding and holding != obj:
                    # print("holding error")
                    return False
                holding = obj
            elif fact[0] == 'ontable':
                obj = fact[1]
                if prev_map[obj] and prev_map[obj] != 'table':
                    # print("ontable error")
                    return False
                G.add_edge("table", obj)
                prev_map[obj] = 'table'
            elif fact[0] == 'clear':
                obj = fact[1]
                if next_map[obj] and next_map[obj] != 'air':
                    # print("clear error")
                    return False
                G.add_edge(obj, "air")
                next_map[obj] = 'air'
            elif fact[0] == 'on':
                hi, lo = fact[1], fact[2]
                if prev_map[hi] and prev_map[hi] != lo:
                    # print("prev error")
                    return False
                if next_map[lo] and next_map[lo] != hi:
                    # print("next error")
                    return False
                G.add_edge(lo, hi)
                prev_map[hi] = lo
                next_map[lo] = hi
        
        if len(list(nx.simple_cycles(G))) > 0:
            # print("cycle found.")
            return False
        
        stacks = []
        # This branch is actually an erroneous transformation. Kept for compatibility.
        if extend:
            for obj in objects:
                if prev_map[obj] == 'table':
                    new_stack = []
                    cur_obj = obj
                    while cur_obj and cur_obj != 'air':
                        new_stack.append(cur_obj)
                        vis_map[cur_obj] = True
                        cur_obj = next_map[cur_obj]                
                    stacks.append(new_stack)

            if holding and holding != 'empty':
                vis_map[holding] = True
        
            for obj in objects:
                if prev_map[obj] == None and holding != obj:
                    new_stack = []
                    cur_obj = obj
                    while cur_obj and cur_obj != 'air':
                        new_stack.append(cur_obj)
                        vis_map[cur_obj] = True
                        cur_obj = next_map[cur_obj]
                    stacks.append(new_stack)
        else:
            if holding and holding != 'empty':
                vis_map[holding] = True
                
            for obj in objects:
                if vis_map[obj]:
                    continue
                cur_obj = obj
                incomplete = 0
                while prev_map[cur_obj] != None and prev_map[cur_obj] != 'table':
                    cur_obj = prev_map[cur_obj]
                new_stack = []
                if prev_map[cur_obj] == None:
                    incomplete += 1
                while cur_obj and cur_obj != 'air':
                    new_stack.append(cur_obj)
                    vis_map[cur_obj] = True
                    cur_obj = next_map[cur_obj]  
                if cur_obj == None:
                    incomplete += 1
                if incomplete == 0 or incomplete == 1 and not strict:
                    stacks.append(new_stack)
        
        return stacks, holding, prev_map, next_map, vis_map
        
    def initialize(self, objects, facts):
        res = self.facts_to_stack_state(objects, facts)
        if res:
            stacks, holding, prev_map, next_map, vis_map = res
        else:
            return
        for obj in objects:
            if not vis_map[obj]:
                print("vis error")
                return False
        
        self.objects = objects
        self.facts = facts
        self.stacks = stacks
        self.holding = holding
        self.prev_map = prev_map
        self.next_map = next_map

        while len(self.stacks) < len(self.objects):
            stacks.append([])
        return True
    
    @classmethod
    def generate_naive_plan(cls, objects, facts, goals):
        init_stacks, init_holding, _, _, _ = cls.facts_to_stack_state(objects, facts)
        goal_stacks, goal_holding, goal_prev, goal_next, vis_map = cls.facts_to_stack_state(objects, goals)
        for obj in objects:
            if goal_prev[obj] == None and goal_holding != obj:
                new_stack = []
                cur_obj = obj
                while cur_obj and cur_obj != 'air':
                    new_stack.append(cur_obj)
                    vis_map[cur_obj] = True
                    cur_obj = goal_next[cur_obj]
                goal_stacks.append(new_stack)
        
        plan = []
        if init_holding != "empty":
            plan.append(("put_down", init_holding))
        for stack in init_stacks:
            for i in range(len(stack)-1, 0, -1):
                plan.append(("unstack", stack[i], stack[i-1]))
                plan.append(("put-down", stack[i]))
        
        for stack in goal_stacks:
            for i in range(len(stack)-1):
                plan.append(("pick-up", stack[i+1]))
                plan.append(("stack", stack[i+1], stack[i]))
        return plan
      

    def step(self, action):
        operator = action[0]
        if operator == 'pick-up':
            if self.holding != 'empty':
                return False
            obj = action[1]
            for i, stack in enumerate(self.stacks):
                if len(stack) == 1 and stack[-1] == obj:
                    self.holding = obj
                    self.stacks[i].pop()
                    break
        
        elif operator == 'put-down':
            obj = action[1]
            if self.holding != obj:
                return False
            for i, stack in enumerate(self.stacks):
                if len(stack) == 0:
                    self.holding = 'empty'
                    self.stacks[i].append(obj)
                    break

        elif operator == 'stack':
            hi, lo = action[1], action[2]
            if self.holding != hi:
                return False
            for i, stack in enumerate(self.stacks):
                if len(stack) > 0 and stack[-1] == lo:
                    self.holding = 'empty'
                    self.stacks[i].append(hi)
                    break

        elif operator == 'unstack':
            hi, lo = action[1], action[2]
            if self.holding != 'empty':
                return False
            for i, stack in enumerate(self.stacks):
                if len(stack) >= 2 and stack[-1] == hi and stack[-2] == lo:
                    self.holding = hi
                    self.stacks[i].pop()
                    break

    def draw_box_on_surface(self, surface):
        WIDTH = 40
        if self.holding != 'empty':
            pygame.draw.rect(surface, object_color_map[self.holding],
                             pygame.Rect(SCREEN_WIDTH / 2 + 30, 50, WIDTH, WIDTH))
        for i, stack in enumerate(self.stacks):
            for j, obj in enumerate(stack):
                color = object_color_map[obj]
                pygame.draw.rect(surface, color, 
                    pygame.Rect(30+(WIDTH*i)*1.5, SCREEN_HEIGHT-60-WIDTH*j, WIDTH, WIDTH))

def run(objects, facts, action_seq):    
    manager = BlocksWorldManager()
    manager.initialize(objects, facts)
    
    action_ptr = 0
    
    pygame.init()
    pygame.font.init()
                   
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # my_font = pygame.freetype.Font("resources/Pixeled.ttf", 20)
    my_font = pygame.font.SysFont(None, 30)
    # text_surface, text_rect = my_font.render('HOLDING: ', False, (255, 255, 255), 0)
    text_surface = my_font.render('HOLDING: ', False, (255, 255, 255), (0, 0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            # Did the user hit a key?
            if event.type == KEYDOWN:
                # Was it the Escape key? If so, stop the loop.
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_n and action_ptr < len(action_seq):
                    manager.step(action_seq[action_ptr])
                    action_ptr += 1
                elif event.key == K_r:
                    manager.initialize(objects, facts)
                    action_ptr = 0
            # Did the user click the window close button? If so, stop the loop.
            elif event.type == QUIT:
                running = False
        
        screen.fill((0, 0, 0))
        screen.blit(text_surface, (SCREEN_WIDTH / 2 - 80, 50))    
        manager.draw_box_on_surface(screen)
        pygame.display.flip()


def parse_problem_string(domain_string, problem_string):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain_string(domain_string)
    problem = reader.parse_instance_string(problem_string)
    lang = problem.language
    objects = lang.constants()
    objects_str = [ str(obj) for obj in objects ]

    facts = problem.init.as_atoms()
    facts_str = []
    for fact in facts:
        fact_str = []
        fact_str.append(fact.symbol.name)
        for subterm in fact.subterms:
            fact_str.append(subterm.name)
        facts_str.append(fact_str)
        
    goals_str = []
    goal = problem.goal
    if isinstance(goal, Tautology):
        pass
    elif isinstance(goal, Atom):
        goals_str.append([goal.symbol.symbol] + [subt.symbol for subt in goal.subterms])
    else:
        for subformula in goal.subformulas:
            goals_str.append([subformula.symbol.symbol ] +  [i.symbol for i in subformula.subterms])
    
    return objects_str, facts_str, goals_str
    
 
def parse_problem_file(domain_path, problem_path):
    domain = Path(domain_path).read_text()
    problem = Path(problem_path).read_text()
    return parse_problem_string(domain, problem)
    
    
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain(domain_path)
    problem = reader.parse_instance(problem_path)
    lang = problem.language
    objects = lang.constants()
    objects_str = [ str(obj) for obj in objects ]

    facts = problem.init.as_atoms()
    facts_str = []
    for fact in facts:
        fact_str = []
        fact_str.append(fact.symbol.name)
        for subterm in fact.subterms:
            fact_str.append(subterm.name)
        facts_str.append(fact_str)
        
    goals_str = []
    goal = problem.goal
    if isinstance(goal, Tautology):
        pass
    elif isinstance(goal, Atom):
        goals_str.append([goal.symbol.symbol] + [subt.symbol for subt in goal.subterms])
    else:
        for subformula in goal.subformulas:
            goals_str.append([subformula.symbol.symbol ] +  [i.symbol for i in subformula.subterms])
    
    return objects_str, facts_str, goals_str
       
def parse_plan_file(plan_path):
    action_seq = []
    with open(plan_path, "r") as f:
        actions = f.readlines()
        for action_raw in actions:
            action_raw = action_raw.strip()
            if action_raw.startswith(";"):
                continue
            action_seq.append(action_raw[1:-1].split())
    return action_seq

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain_path", type=str, required=True)
    parser.add_argument("--problem_path", type=str, required=True)
    parser.add_argument("--plan_path", type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    domain_path = args.domain_path
    problem_path = args.problem_path
    plan_path = args.plan_path
    objects, facts, _ = parse_problem_file(domain_path, problem_path)
    action_seq = parse_plan_file(plan_path)
    print(objects, facts, action_seq)
    run(objects, facts, action_seq)
