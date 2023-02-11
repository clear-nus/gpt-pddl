import argparse

import openai
import time
import random
import os
import json

from constants import (
    oneshot_problem_goal_pddl_dict,
    one_shot_nl_dict,
    oneshot_problem_nogoal_pddl_dict,
    nl_questions,
    synonym_to_type_dict,
)


# define a retry decorator
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (openai.error.RateLimitError,),
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specified errors
            except errors as e:
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper


@retry_with_exponential_backoff
def completions_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)


def gen_goal(
    domain_file,
    nl,
    init_state_file,
    goal_state_file,
    one_shot=False,
    is_question=False,
    scene="",
):
    with open(init_state_file, "r") as f:
        problem_nogoal_pddl = f.read()

    domain_pddl = open(domain_file, "r").read()
    translation_prompt_instruction = "Write the instruction to goal state in PDDL. "
    translation_prompt = (
        "PDDL: "
        + domain_pddl
        + "\n"
        + "Task: "
        + "\n"
        + problem_nogoal_pddl
        + "\n"
        + nl
        + "\n"
    )

    if not is_question:
        translation_prompt += translation_prompt_instruction

    if one_shot:
        print("performing one shot")
        translation_prompt = "PDDL: " + domain_pddl + "\n"
        oneshot_problem_goal_pddl = oneshot_problem_goal_pddl_dict[scene]
        oneshot_nl = one_shot_nl_dict[scene]
        oneshot_problem_nogoal_pddl = oneshot_problem_nogoal_pddl_dict[scene]
        translation_prompt += (
            "Task: "
            + oneshot_problem_nogoal_pddl
            + "\n"
            + oneshot_nl
            + "\n"
            + "Answer: "
            + oneshot_problem_goal_pddl
        )
        translation_prompt += "Task: \n" + problem_nogoal_pddl + "\n" + nl + "\n"
        if not is_question:
            translation_prompt += translation_prompt_instruction + "\n" + "Answer:"

    # print(translation_prompt_instruction)
    # print(domain_pddl)
    # print(problem_nogoal_pddl)
    # print(translation_prompt)
    try:
        response = completions_with_backoff(
            # model="text-embedding-ada-002",
            model="text-davinci-003",
            # model="code-davinci-002",
            prompt=translation_prompt,
            temperature=0,
            max_tokens=180,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            # stop=[]
        )
        translation_response = response["choices"][0]["text"]
    except:
        print("error")
        return
    with open(goal_state_file.replace("goal_state", "input_to_model"), "w") as f:
        f.write(translation_prompt)
    with open(goal_state_file, "w") as f:
        f.write(translation_response)
    f.close()

    return translation_response


parser = argparse.ArgumentParser(
    prog="ProgramName",
    description="What the program does",
    epilog="Text at the bottom of help",
)
parser.add_argument("-scene", "--scene", required=True, type=str)
parser.add_argument("--case", type=int, default=0)
parser.add_argument(
    "--init_path",
    type=str,
    required=True,
    help="Please specify the path to the initial states",
)
parser.add_argument(
    "--gen_path",
    type=str,
    required=True,
    help="Please specify which path to save the generation to",
)
parser.add_argument(
    "--domain_file", type=str, required=False, default="domain_updated.pddl"
)
parser.add_argument("--num_cases", type=int, default=100)
parser.add_argument("--zero_shot", action="store_true")

args = parser.parse_args()

random.seed(1333)

scenes = [args.scene]
assert len(scenes) == 1
if not args.case:
    case_number = range(1, args.num_cases + 1)
else:
    case_number = [args.case]

ONE_SHOT = not args.zero_shot


NEED_SAMPLE_SCENES = {
    "scene9": 2,
    "scene22": 1,
}  # in these scenes, we need to perform random sampling from the list of objects
if __name__ == "__main__":
    generated_dir = args.gen_path
    init_state_dir = args.init_path
    domain_file = args.domain_file

    if ONE_SHOT:
        print("You are doing one-shot learning")
        assert (
            "one_shot" in generated_dir
        ), "You are strongly suggested to put `one_shot` in the gen_path, as this prevents confusion with the zero shot learning"
    else:
        print("You are doing zero shot learning!")
        assert "one_shot" not in generated_dir

    generation_dirs = [generated_dir, generated_dir + "_domain", generated_dir + "_inf"]
    for dir in generation_dirs:
        if not os.path.exists(dir):
            os.mkdir(dir)

    result_dict = {}
    for scene in scenes:
        result_dict[scene] = {}
        if scene not in nl_questions:
            continue
        for i in case_number:
            init_state_file = os.path.join(
                init_state_dir, scene, f"init_state_{i}.pddl"
            )
            objects_list = json.load(
                open(os.path.join(init_state_dir, scene, f"pre_obj_{i}.json"))
            )

            for dir in generation_dirs:
                if not os.path.exists(os.path.join(dir, scene)):
                    os.mkdir(os.path.join(dir, scene))

            goal_state_files = [
                os.path.join(generated_dir, scene, f"goal_state_{i}.pddl"),
                os.path.join(generated_dir + "_domain", scene, f"goal_state_{i}.pddl"),
                os.path.join(generated_dir + "_inf", scene, f"goal_state_{i}.pddl"),
            ]
            if scene in NEED_SAMPLE_SCENES:
                if scene == "scene9":
                    # ---- for object moving
                    picked_objects = random.sample(objects_list, 2)
                    moved_object, target_object = picked_objects
                    queries = [
                        nl_questions[scene][0].format(
                            moved_object, target_object, target_object
                        ),
                        nl_questions[scene][1].format(target_object),
                        nl_questions[scene][2].format(
                            moved_object, target_object, target_object, moved_object
                        ),
                    ]

                    goal = {"goal": ("shareLocation", moved_object, target_object)}

                if scene == "scene22":
                    nl_word, test_type = random.choice(
                        list(synonym_to_type_dict.items())
                    )

                    if test_type in ["Watch", "CellPhone", "KeyChain"]:
                        queries = [
                            nl_questions[scene][0].format(nl_word),
                            nl_questions[scene][1].format(nl_word, nl_word),
                            nl_questions[scene][2].format(nl_word),
                        ]
                    moved_object = ""
                    if test_type in ["Sofa", "GarbageCan"]:
                        prep = "on" if test_type == "Sofa" else "in"
                        picked_objects = random.sample(objects_list, 1)
                        moved_object = picked_objects[0]
                        queries = [
                            "Put the {} {} a {}.".format(moved_object, prep, nl_word),
                            #
                            # "Is there a {} in the initial state?".format(nl_word),
                            "Is there a {} in the environment?".format(nl_word),
                            # "There is a {} in the environment. Which object is likely a {}?".format(nl_word, nl_word),
                            "Put the {} {} a {}. Where should we put {}?".format(
                                moved_object, prep, nl_word, moved_object
                            ),
                        ]

                    goal = {"goal": ("synonym", nl_word, test_type, moved_object)}

            elif scene in ["scene12", "scene11", "scene10"]:
                moved_object = objects_list["moved_object"]
                target_type = objects_list["target_type"]

                queries = [
                    nl_questions[scene][0].format(moved_object, target_type.lower()),
                    nl_questions[scene][1].format(target_type.lower()),
                    nl_questions[scene][2].format(
                        moved_object, target_type.lower(), moved_object
                    ),
                ]

                goal = {"goal": ("find_count", moved_object, target_type)}

            elif scene in ["scene13", "scene14"]:
                moved_object = objects_list["moved_object"]
                target_object = objects_list["target_object"]
                queries = [
                    nl_questions[scene][0].format(moved_object, target_object),
                    nl_questions[scene][1].format(target_object),
                    nl_questions[scene][2].format(
                        moved_object, target_object, moved_object
                    ),
                ]
                goal = {"goal": ("find_source", moved_object, target_object)}
            else:
                query = nl_questions[scene]
                goal = {}

            print("Queries:", queries)
            print("####################", scene, i, "####################")
            goal["query"] = queries
            generations = []
            for j, query in enumerate(queries):
                if query.endswith("?"):
                    # only the second and the third query should be a question
                    is_question = True
                    assert j == 1 or j == 2
                else:
                    is_question = False
                    assert j == 0
                goal_state_file = goal_state_files[j]
                gen = gen_goal(
                    domain_file,
                    query,
                    init_state_file,
                    goal_state_file,
                    one_shot=ONE_SHOT,
                    is_question=is_question,
                    scene=scene,
                )
                generations.append(gen)
                print(f"Question{i}-{j}: {query}")
                print(f"Answer: {gen}")
            result_dict[scene][i] = {
                "question": generations[0],
                "domain": generations[1],
                "inf": generations[2],
                "objects": objects_list,
            }
            json.dump(
                goal, open(os.path.join(generated_dir, scene, f"goal_{i}.json"), "w")
            )
        # print(result_dict)
        if ONE_SHOT:
            json.dump(result_dict, open(f"{scene}_one_shot_result.json", "w"))
        else:
            json.dump(result_dict, open(f"{scene}_result.json", "w"))

    print(f"Finished generation from {init_state_dir} to {generated_dir}")
