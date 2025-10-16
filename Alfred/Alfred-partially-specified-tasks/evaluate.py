import argparse
import re
import os
import json


def load_joined_goal_state(prefix, scene, i):
    goal_state = []

    with open(os.path.join(prefix, scene, f"goal_state_{str(i)}.pddl"), "r") as f:
        for line in f:
            goal_state.append(line.strip())
    return " ".join(goal_state).strip()


def load_data_raw(init_prefix, goal_prefix, scene, i):
    init_state = []
    goal_state = []
    with open(
        os.path.join(init_prefix, scene, "init_state_" + str(i) + ".pddl"), "r"
    ) as f:
        for line in f:
            init_state.append(line.strip())
    with open(
        os.path.join(goal_prefix, scene, "goal_state_" + str(i) + ".pddl"), "r"
    ) as f:
        for line in f:
            goal_state.append(line.strip())
    query_dict = json.load(
        open(os.path.join(goal_prefix, scene, f"goal_{i}.json"), "r")
    )
    return init_state, goal_state, query_dict


def extract_all_bracket_content(goal_state_string):
    """
    Extract all content inside the brackets
    param:
    goal_state_string:
    sample:
    (:goal (and (isClean Book1) (isClean Pencil1) (isClean Pencil2) (isClean Laptop1) (isClean Pencil3) (isClean Pen1) (isClean CD1) (isClean CD2) (isClean CreditCard1) (isClean KeyChain1) (isClean CellPhone1) ))
    return result:
    [['isClean','Book1'], 'isClean Pencil1', 'isClean Pencil2', 'isClean Laptop1', 'isClean Pencil3', 'isClean Pen1', 'isClean CD1', 'isClean CD2', 'isClean CreditCard1', 'isClean KeyChain1', 'isClean CellPhone1']
    """
    # print("Goal state string", goal_state_string)
    result = re.findall("(?<=\()([^)]+)(?=\))", goal_state_string)
    cleaned_result = []
    for bracket_content in result:
        if "(" in bracket_content:
            cleaned_result.append(bracket_content.split("(")[-1])
        else:
            cleaned_result.append(bracket_content)
    # print(cleaned_result)
    # split the results
    cleaned_result = [x.split() for x in cleaned_result]

    return cleaned_result


def evaluate_triple(triple, object1_prefix, object2_prefix, relation=None):
    if not relation:
        # only check the objects
        return triple[1].startswith(object1_prefix) and triple[2].startswith(
            object2_prefix
        )
    else:
        return (
            triple[0] == relation
            and triple[1].startswith(object1_prefix)
            and triple[2].startswith(object2_prefix)
        )


def evaluate_attribute(two_element_tuple, attribute, object_prefix):
    return two_element_tuple[0] == attribute and two_element_tuple[1].startswith(
        object_prefix
    )


def evaluate_question_mark(scene, goal_state):
    if "?" in goal_state:
        return False
    else:
        return True


def evaluate_parenthesis_validity(scene, goal_state):
    # a stndard coding question, copying the answer from https://stackoverflow.com/questions/73175952/valid-parentheses-including-characters
    # check for balanced parentheses in an expression
    def isValid(test_str):
        par_dict = {"(": ")", "{": "}", "[": "]"}
        stack = []
        for char in test_str:
            if char in par_dict.keys():
                stack.append(char)
            elif char in par_dict.values():
                if stack == []:
                    return False
                open_brac = stack.pop()
                if char != par_dict[open_brac]:
                    return False
        return stack == []

    return isValid(goal_state)


def check_keyword_goal(scene, goal_state):
    return "(:goal" in goal_state


def check_keyword_isclean(scene, goal_state):
    return "isClean" in goal_state


def remove_unnecessary_keywords(goal_state):
    # remove all content after these prefix, so only goal remains
    unnecessary_prefix = ["\(\:action", "\(\:task"]
    for prefix in unnecessary_prefix:
        goal_state = re.sub(prefix + ".*", "", goal_state)
    return goal_state


def find_whatson_object(state, receptacle_name):
    agent_location = ""
    agent_holds = False
    hold_object = ""
    for line in state:
        if line.startswith("(:goal") and (
            "objectAtLocation" in line or "inReceptacle" in line
        ):
            obj = line.split()[-2]
            if line.split()[-1].strip(")") == receptacle_name:
                return obj

        if ("objectAtLocation" in line or "inReceptacle" in line) and line.strip(
            ")"
        ).split()[-1] == receptacle_name:
            return line.split()[1]
        if "holds" in line and not "not" in line and "agent" in line:
            agent_holds = True
            hold_object = line.split()[-1].strip(")")
        if "atLocation" in line and "agent" in line:
            agent_location = line.strip(")").split()[-1]

        if agent_location and agent_holds and agent_location == receptacle_name:
            return hold_object
    print(("item not found on {} in {}".format(receptacle_name, state)))
    return ""


def find_location_of_object(state, object_name):
    agent_location = ""
    agent_holds = False
    for line in state:
        if line.startswith("(:goal") and (
            "objectAtLocation" in line or "inReceptacle" in line
        ):
            obj = line.split()[-2]
            if object_name == obj:
                return line.split()[-1].strip(")")

        if (
            "objectAtLocation" in line or "inReceptacle" in line
        ) and object_name == line.split()[1]:
            return line.strip(")").split()[-1]
        if (
            "holds" in line
            and not "not" in line
            and "agent" in line
            and object_name == line.split()[-1].strip(")")
        ):
            agent_holds = True
        if "atLocation" in line and "agent" in line:
            agent_location = line.strip(")").split()[-1]
    if agent_location and agent_holds:
        return agent_location
    print(("item not found {} in {}".format(object_name, state)))
    return ""


def evaluate_same_location(init_state, goal_state, object1, object2):
    location1 = find_location_of_object(init_state, object1)
    location2 = find_location_of_object(goal_state, object2)
    print(f"Location {object1}:{location1} and {object2}:{location2}")
    if not location2 == location1:
        print("Not equal!")
    return location1 == location2


def evaluate_correct_count_moved(
    init_state, goal_state, object, target_type, goal_count
):
    count_dict = evaluate_object_count_in_initial(init_state, object_type=target_type)
    location = find_location_of_object(goal_state, object)
    print(f"Object {object} moved to location {location}", "count dict: ", count_dict)
    if not count_dict.get(location, -1) == goal_count:
        print("Wrong!")
    return count_dict.get(location, -1) == goal_count


def evaluate_book_count(init_state):
    book_count = {}
    for line in init_state:
        if ("objectAtLocation" in line or "inReceptacle" in line) and line.split()[
            1
        ].startswith("Book"):
            location = line.split()[-1].strip(")")
            if location not in book_count:
                book_count[location] = 0
            book_count[location] += 1
    return book_count


def evaluate_object_count_in_initial(init_state, object_type):
    book_count = {}
    # print(init_state, object_type)
    for line in init_state:
        if ("objectAtLocation" in line or "inReceptacle" in line) and line.split()[
            1
        ].startswith(object_type):
            location = line.split()[-1].strip(")")
            if location not in book_count:
                book_count[location] = 0
            book_count[location] += 1
    return book_count


def find_box_with_count(init_state, object_type, count):
    count_dict = evaluate_object_count_in_initial(init_state, object_type)
    print("Box count dict", count_dict)
    for item, curr_count in count_dict.items():
        if curr_count == count and item.startswith("Box"):
            return item
    raise ValueError("No box with such count!")


def find_nested_location_of_object(state, object_name):
    for line in state:
        if (
            "objectAtLocation" in line or "inReceptacle" in line
        ) and object_name == line.split()[1]:
            location = line.strip(")").split()[-1]
            return find_nested_location_of_object(state, location) or location
    # print(("item not found {} in {}".format(object_name, state)))
    return ""


def evaluate_correct_move_nested_location(
    init_state, goal_state, moved_object, target_object
):
    moved_to_location = find_location_of_object(
        state=goal_state, object_name=moved_object
    )
    target_object_location = find_nested_location_of_object(init_state, target_object)
    if target_object_location == "":
        print(target_object, init_state)

    if not moved_to_location == target_object_location:
        print(
            f"Wrong destination moved. Moved {moved_object} to {moved_to_location}, but {target_object} is at {target_object_location}"
        )
    return moved_to_location == target_object_location


def state_has_gent(goal_state):
    has_agent = False
    for line in goal_state:
        if "agent" in line:
            return True
    return False


parser = argparse.ArgumentParser(
    prog="evaluate",
    description="evaluate the performance of the GPT generation",
    epilog="Text at the bottom of help",
)
parser.add_argument(
    "-scene",
    "--scene",
    type=str,
    required=True,
    help="Please specify scene number for evaluation",
)
parser.add_argument(
    "--init_path", type=str, required=True, help="Please specify a initial path"
)
parser.add_argument(
    "--gen_path",
    type=str,
    required=True,
    help="Please specify a generated goal state path",
)
parser.add_argument("--num_cases", type=int, default=100)
parser.add_argument("--zero_shot", action="store_false")

args = parser.parse_args()
scenes = [args.scene]

NUM_CASES = args.num_cases + 1

if not args.zero_shot:
    print("Using one shot")
    ONE_SHOT = True
else:
    ONE_SHOT = False


def main():
    if ONE_SHOT:
        assert (
            "one_shot" in args.gen_path
        ), "You are running one-shot validation, but gen_path doesn't have one_shot"

    goal_prefix = args.gen_path
    init_prefix = args.init_path

    # evaluation functions should take  (scene, goal_state) as the parameters
    evaluation_functions = {
        # "condition satisfaction": evaluate,
        "no question mark existence": evaluate_question_mark,
        "parenthesis validity": evaluate_parenthesis_validity,
        'has keyword "(:goal"': check_keyword_goal,
    }
    scenes_scores = {}
    for function_name, function in evaluation_functions.items():
        for scene in scenes:
            scenes_scores[scene] = 0
        for scene in scenes:
            for i in range(1, NUM_CASES):
                goal_state = load_joined_goal_state(goal_prefix, scene, i)
                goal_state = remove_unnecessary_keywords(goal_state)
                if function(scene, goal_state):
                    scenes_scores[scene] += 1
        print("Simple evaluation for {}".format(function_name), scenes_scores)

    for scene in scenes:
        scenes_scores[scene] = {}

    for scene in scenes:
        if ONE_SHOT:
            file_name = f"{scene}_one_shot_result.json"
        else:
            file_name = f"{scene}_result.json"
        result_dict = json.load(open(file_name, "r"))[scene]
        for i in range(1, NUM_CASES):
            init_state, goal_state, goal_dict = load_data_raw(
                init_prefix=init_prefix, goal_prefix=goal_prefix, scene=scene, i=i
            )
            loose_success = False
            strict_success = False
            domain_success = False
            inf_success = False

            print("Current i", i)
            if scene in ("scene9") and goal_dict["goal"][0] == "shareLocation":
                object1, object2 = goal_dict["goal"][1:]
                target_initial_location = find_location_of_object(
                    init_state, object_name=object2
                )
                if evaluate_same_location(init_state, goal_state, object2, object1):
                    loose_success = True
                    # scenes_scores[scene][0] += 1
                    # print(find_location_of_object(state=goal_state, object_name=object1).strip(),
                    #       target_initial_location)

                    if (
                        find_location_of_object(
                            state=goal_state, object_name=object1
                        ).strip()
                        == target_initial_location
                    ):
                        if not state_has_gent(goal_state):
                            strict_success = True

                if target_initial_location in result_dict[str(i)]["domain"]:
                    domain_success = True
                if target_initial_location in result_dict[str(i)]["inf"]:
                    inf_success = True

            if scene in ["scene11", "scene12", "scene10"]:
                if scene == "scene11":  # scene 11 has three objects
                    goal_count = 3
                if scene == "scene12" or scene == "scene10":
                    goal_count = 2

                target, moved_object, target_type = goal_dict["goal"]
                assert target == "find_count"
                if evaluate_correct_count_moved(
                    init_state,
                    goal_state,
                    moved_object,
                    target_type=target_type,
                    goal_count=goal_count,
                ):
                    loose_success = True
                    if not state_has_gent(goal_state):
                        strict_success = True
                # print('init state', init_state)
                initial_box_with_count = find_box_with_count(
                    init_state=init_state, object_type=target_type, count=goal_count
                )
                # print(result_dict[str(i)]['domain'])
                if initial_box_with_count in result_dict[str(i)]["domain"]:
                    domain_success = True
                if initial_box_with_count in result_dict[str(i)]["inf"]:
                    inf_success = True

            if scene in ["scene13", "scene14"]:  # one layer of nested
                # success = False
                target, moved_object, target_object = goal_dict["goal"]
                if evaluate_correct_move_nested_location(
                    init_state, goal_state, moved_object, target_object
                ):
                    # scenes_scores[scene][0] += 1
                    loose_success = True
                    if not state_has_gent(goal_state):
                        strict_success = True

                # print(init_state, target_object)
                target_sofa = find_nested_location_of_object(init_state, target_object)
                # print(target_sofa)
                assert target_sofa.startswith("Sofa")
                # print("domain is ", result_dict[str(i)]["domain"])

                if target_sofa in result_dict[str(i)]["domain"]:
                    # print("domain is ", result_dict[str(i)]["domain"])
                    domain_success = True

                if target_sofa in result_dict[str(i)]["inf"]:
                    inf_success = True

            if scene == "scene22":
                target, nl_word, test_type, moved_object = goal_dict["goal"]
                # print(goal_dict["goal"])
                assert target == "synonym"

                # location = find_location_of_object(state=goal_state, object_name=moved_object).strip()
                # print(location)
                if test_type in ["GarbageCan", "Sofa"]:
                    if (
                        find_location_of_object(
                            state=goal_state, object_name=moved_object
                        )
                        .strip()
                        .startswith(test_type)
                    ):
                        loose_success = True
                        if not state_has_gent(goal_state):
                            strict_success = True
                    if "yes" in result_dict[str(i)]["domain"].lower():
                        # if test_type in result_dict[str(i)]['domain']:
                        domain_success = True
                    if test_type in result_dict[str(i)]["inf"]:
                        inf_success = True
                elif test_type in ["CellPhone", "KeyChain", "Watch"]:
                    # TODO: write this evaluation logic
                    if (
                        find_whatson_object(state=goal_state, receptacle_name="Desk1")
                        .strip()
                        .startswith(test_type)
                    ):
                        loose_success = True
                        if not state_has_gent(goal_state):
                            strict_success = True
                    if (
                        result_dict[str(i)]["domain"] is not None
                        and "yes" in result_dict[str(i)]["domain"].lower()
                    ):
                        # if test_type in result_dict[str(i)]['domain']:
                        domain_success = True
                    if test_type in result_dict[str(i)]["inf"]:
                        inf_success = True
                else:
                    raise ValueError("No such type for the test. ")

            scenes_scores[scene][i] = {
                "loose_success": loose_success,
                "strict_success": strict_success,
                "domain_success": domain_success,
                "inf_success": inf_success,
            }

    process_scores(scenes_scores)


def process_scores(scenes_scores):
    strict_success = 0
    loose_success = 0
    domain_failure_fail = 0
    inf_failure_fail = 0
    domain_failure_suc = 0
    inf_failure_suc = 0
    for scene in scenes_scores:
        for i, item_dict in scenes_scores[scene].items():
            if item_dict["loose_success"]:
                loose_success += 1
                if item_dict["strict_success"]:
                    strict_success += 1
                if not item_dict["domain_success"]:
                    domain_failure_suc += 1
                if not item_dict["inf_success"]:
                    inf_failure_suc += 1
            else:
                if not item_dict["domain_success"]:
                    domain_failure_fail += 1
                if not item_dict["inf_success"]:
                    inf_failure_fail += 1
    print("Scene {}".format(scene))
    print(f"Strict success {strict_success}", f"loose_success {loose_success}")
    print(
        f"domain_failure in fail: {domain_failure_fail} {domain_failure_fail/(100-loose_success)*100:.2f}"
    )
    print(
        f"inf_failure in fail {inf_failure_fail} {inf_failure_fail/(100-loose_success)*100:.2f}"
    )
    print(
        f"domain_failure in suc {domain_failure_suc} {domain_failure_suc/(loose_success)*100:.2f}"
    )
    print(
        f"inf failure in suc {inf_failure_suc} {inf_failure_suc/(loose_success)*100:.2f}"
    )
    json.dump(
        {
            "strict_success": strict_success,
            "loose_success": loose_success,
            "domain_failure_fail": domain_failure_fail,
            "inf_failure_fail": inf_failure_fail,
            "domain_failure_suc": domain_failure_suc,
            "inf_failure_suc": inf_failure_suc,
        },
        open(f"eval_results/eval_result_{scene}.json", "w"),
    )


if __name__ == "__main__":
    main()
