import json
from domain_constants import (
    VAL_ACTION_OBJECTS,
    VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS,
    Object_Types_in_Scenes,
)

import random
import os
import argparse


parser = argparse.ArgumentParser(
    prog="generate_initial_states",
    description="Generate the initial states for analysis",
    epilog="Text at the bottom of help",
)
parser.add_argument(
    "-scene",
    "--scene",
    type=str,
    default="all",
    help="Please specify scene number for evaluation",
)
parser.add_argument(
    "--init_path",
    type=str,
    required=True,
    help="Please specify the path to save the initial states",
)

args = parser.parse_args()
scenes = [
    "scene9",
    # "scene10",
    "scene11",
    "scene12",
    "scene13",
    "scene14",
    "scene22",  # synonym
]
init_state_path = args.init_path
if args.scene != "all":
    assert (
        args.scene in scenes
    ), "The specified scene is not valid, please use scenes from {}".format(scenes)
    scenes = [args.scene]  # override all scenes

Heatable_list = list(VAL_ACTION_OBJECTS["Heatable"])
Coolable_list = list(VAL_ACTION_OBJECTS["Coolable"])
Cleanable_list = list(VAL_ACTION_OBJECTS["Cleanable"])
Toggable_list = list(VAL_ACTION_OBJECTS["Toggleable"])
Sliceable_list = list(VAL_ACTION_OBJECTS["Sliceable"])

NUM_CASES = 101


def pick_k_from_lst(lst, k):
    shuffled_lst = lst[:]
    random.shuffle(shuffled_lst)
    return shuffled_lst[:k]


for scene in scenes:
    random.seed(1023)
    if not os.path.exists(os.path.join(init_state_path)):
        os.mkdir(os.path.join(init_state_path))
        os.mkdir(os.path.join(init_state_path + "_global_random"))
        os.mkdir(os.path.join(init_state_path + "_local_random"))

    if not os.path.exists(os.path.join(init_state_path, scene)):
        os.mkdir(os.path.join(init_state_path, scene))
        os.mkdir(os.path.join(init_state_path + "_global_random", scene))
        os.mkdir(os.path.join(init_state_path + "_local_random", scene))
    if scene == "food_pre1" or scene == "scene10":
        pre_obj = ["Tomato1", "Bread1"]
        pre_rec = ["Plate1"]
    elif scene == "food_pre2":
        pre_obj = ["Apple1"]
        pre_rec = ["Plate1"]
    elif scene == "food_pre3":
        pre_obj = ["Tomato1", "Bread1"]
        pre_rec = ["Plate1"]
    elif scene == "food_pre4":
        pre_obj = ["Egg1", "Lettuce1"]
        pre_rec = ["DiningTable1"]
    elif scene == "scene1":
        pre_obj = ["IceCream1"]
        pre_rec = ["Fridge1"]
    elif scene == "scene2":
        pre_obj = ["IceCream1"]
        pre_rec = ["Fridge1"]
    elif scene == "scene3":
        pre_obj = ["Newspaper1", "RemoteControl1", "KeyChain1"]
        pre_rec = ["Sofa1", "Desk1", "Drawer1"]
    elif scene == "scene4":  # double
        pre_obj = [
            "Cup1",
            "Bowl1",
            "Plate1",
            "Fork1",
            "Spoon1",
            "Knife1",
            "Cup2",
            "Bowl2",
            "Plate2",
            "Fork2",
            "Spoon2",
            "Knife2",
        ]
        pre_rec = ["DiningTable1"]
    elif scene == "scene5":
        pre_obj = ["Cup1", "Bowl1", "Plate1", "Fork1", "Spoon1", "Knife1"]
        pre_rec = ["DiningTable1"]
    elif scene == "scene6":
        pre_obj = []
        pre_rec = ["SinkBasin1", "Oven1", "Microwave1", "Floor1", "Fridge1"]
    elif scene == "scene7":
        pre_obj = []
        pre_rec = ["Sofa1", "Floor1", "Desk1", "Drawer1"]
    elif scene == "scene8":
        pre_obj = []
        pre_rec = ["Bed1", "Floor1", "Desk1", "Drawer1"]
    elif scene == "scene9" or scene == "scene21":
        pre_obj = [
            "Book1",
            "Candle1",
            "Book2",
            "Book3",
            "Book4",
            "Book5",
            "KeyChain1",
            "KeyChain2",
            "Pencil1",
            "Pencil2",
            "Pen1",
            "Pen2",
            "Watch1",
            "Watch2",
        ]
        pre_rec = ["Bed1", "Floor1", "Desk1", "Drawer1", "Sofa3", "Desk5"]
    elif scene == "scene11":
        object_class_lst = ["Book", "Pencil", "Laptop", "KeyChain"]
        book_counts_per_box = (3, 2, 1)
        pre_rec = [f"Box{i}" for i in range(1, 4)] + [f"Sofa{i}" for i in range(1, 3)]
    elif scene == "scene12":
        # scene 12, count 2 objects
        object_class_lst = ["Book", "Pencil", "Laptop", "KeyChain"]
        book_counts_per_box = (2, 1)
        pre_rec = [f"Box{i}" for i in range(1, 3)] + [f"Sofa{i}" for i in range(1, 5)]
    elif scene == "scene13" or scene == "scene14":
        object_class_lst = ["Book", "KeyChain", "AlarmClock", "Pencil"]
        # # scene 13, nested boxes
        # pre_obj = [f"Book{i}" for i in range(1,6)] + ["Pen1", "KeyChain1"]
        boxs = [f"Box{i}" for i in range(1, 5)]
        pre_rec = boxs + [f"Sofa{i}" for i in range(1, 4)]
    elif scene == "scene22":
        pre_obj = [
            "Book1",
            "Candle1",
            "Book2",
            "Book3",
            "Book4",
            "Book5",
            "KeyChain1",
            "Pencil1",
            "Pencil2",
            "Pen1",
            "Pen2",
            "Watch1",
            "CellPhone1",
        ]
        pre_rec = [
            "Bed1",
            "Floor1",
            "Desk1",
            "Drawer1",
            "Sofa1",
            "Desk5",
            "GarbageCan1",
        ]

    for i in range(1, NUM_CASES):
        if scene in ["scene12", "scene11"]:
            target_obj, moved_obj = pick_k_from_lst(object_class_lst[:], k=2)
            if scene == "scene12":
                target_lst = [f"{target_obj}{i}" for i in range(1, 4)]
                moved_lst = [f"{moved_obj}{i}" for i in range(1, 3)]
            if scene == "scene11":
                target_lst = [f"{target_obj}{i}" for i in range(1, 7)]
                moved_lst = [f"{moved_obj}{i}" for i in range(1, 3)]
            pre_obj = target_lst + moved_lst
            moved_obj = random.choice(moved_lst)
        if scene in ["scene12", "scene11"]:
            target_obj, moved_obj = pick_k_from_lst(object_class_lst[:], k=2)
            if scene == "scene12":
                target_lst = [f"{target_obj}{i}" for i in range(1, 4)]
                moved_lst = [f"{moved_obj}{i}" for i in range(1, 3)]
            if scene == "scene11":
                target_lst = [f"{target_obj}{i}" for i in range(1, 7)]
                moved_lst = [f"{moved_obj}{i}" for i in range(1, 3)]
            pre_obj = target_lst + moved_lst
            moved_obj = random.choice(moved_lst)

        if scene in ["scene13", "scene14"]:
            target_type, moved_type = pick_k_from_lst(object_class_lst[:], k=2)
            # target_type, moved_type = object_class_lst
            target_lst = [f"{target_type}{i}" for i in [1]]
            moved_lst = [f"{moved_type}{i}" for i in [1]]
            pre_obj = target_lst + moved_lst
            moved_obj = random.choice(moved_lst)
            target_obj = random.choice(target_lst)
            # print("MT", moved_obj, target_obj)

        with open(
            os.path.join(init_state_path, scene, "init_state_{}.pddl".format(i)), "w"
        ) as f1, open(
            os.path.join(
                init_state_path + "_local_random", scene, "init_state_{}.pddl".format(i)
            ),
            "w",
        ) as f2, open(
            os.path.join(
                init_state_path + "_global_random",
                scene,
                "init_state_{}.pddl".format(i),
            ),
            "w",
        ) as f3:
            for f in [f1, f2, f3]:
                f.write("(:objects \r ")

            TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS = []
            for relationship in VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS:
                if (
                    relationship.split()[1][:-1] in Object_Types_in_Scenes[scene]
                    and relationship.split()[2][:-1] in Object_Types_in_Scenes[scene]
                ):  # if and, in some scenes, there will be less then 10 relationships.
                    TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS.append(relationship)
            if len(TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS) < 15:
                count = 25 - len(TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS)
                for relationship in VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS:
                    if (
                        relationship.split()[1][:-1] in Object_Types_in_Scenes[scene]
                        or relationship.split()[2][:-1] in Object_Types_in_Scenes[scene]
                    ):  # if and, in some scenes, there will be less then 10 relationships.
                        TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS.append(relationship)
                        count -= 1
                    if count == 0:
                        break

            # print(len(TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS))
            randomInt = random.randint(10, 15)
            # print(len(TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS))
            if randomInt > len(TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS):
                randomInt = len(TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS)
                # print(randomInt, len(TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS))
            PART_TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS = random.sample(
                TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS, randomInt
            )
            objects = set()
            receptacle_objects = set()

            hea = set()
            coo = set()
            cle = set()
            tog = set()
            sli = set()
            NEW_PART_TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS = []
            for relationship in PART_TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS:
                if relationship.split()[1] in objects:
                    maxInt = 1
                    while relationship.split()[1][:-1] + str(maxInt) in objects:
                        maxInt += 1
                    # print(relationship)
                    relationship = relationship.replace(
                        relationship.split()[1],
                        relationship.split()[1][:-1]
                        + str(int(relationship.split()[1][-1]) + maxInt - 1),
                    )
                    # sprint(relationship)
                if relationship.split()[2] in receptacle_objects:
                    maxInt = 1
                    while (
                        relationship.split()[2][:-1] + str(maxInt) in receptacle_objects
                    ):
                        maxInt += 1
                    relationship = relationship.replace(
                        relationship.split()[2],
                        relationship.split()[2][:-1]
                        + str(int(relationship.split()[2][-1]) + maxInt - 1),
                    )

                objects.add(relationship.split()[1])

                if relationship.split()[1][:-1] in Sliceable_list:
                    sli.add(relationship.split()[1])
                receptacle_objects.add(relationship.split()[2])
                if relationship.split()[2][:-1] in Sliceable_list:
                    sli.add(relationship.split()[2])

                if relationship.split()[1][:-1] in Heatable_list:
                    hea.add(relationship.split()[1])
                if relationship.split()[2][:-1] in Heatable_list:
                    hea.add(relationship.split()[2])

                if relationship.split()[1][:-1] in Cleanable_list:
                    cle.add(relationship.split()[1])
                if relationship.split()[2][:-1] in Cleanable_list:
                    cle.add(relationship.split()[2])

                if relationship.split()[1][:-1] in Toggable_list:
                    tog.add(relationship.split()[1])
                if relationship.split()[2][:-1] in Toggable_list:
                    tog.add(relationship.split()[2])

                if relationship.split()[1][:-1] in Coolable_list:
                    coo.add(relationship.split()[1])
                if relationship.split()[2][:-1] in Coolable_list:
                    coo.add(relationship.split()[2])

                NEW_PART_TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS.append(relationship)
            for f in [f1, f2, f3]:
                f.write("\t({} - agent)\r ".format("agent1"))
            for obj in objects:
                for f in [f1, f2, f3]:
                    f.write("\t({} - object)\r ".format(obj))

            for rec in receptacle_objects:
                for f in [f1, f2, f3]:
                    if rec.startswith("Box"):
                        f.write("\t({} - receptacle_object)\r ".format(rec))
                    else:
                        f.write("\t({} - receptacle)\r ".format(rec))

            for p_obj in pre_obj:
                if p_obj not in objects:
                    for f in [f1, f2, f3]:
                        f.write("\t({} - object)\r ".format(p_obj))

            # for book in books:
            #     f.write('\t({} - object)\r '.format(book))

            for p_rec in pre_rec:
                if p_rec not in receptacle_objects:
                    for f in [f1, f2, f3]:
                        if p_rec.startswith("Box"):
                            f.write("\t({} - receptacle_object)\r ".format(p_rec))
                        else:
                            f.write("\t({} - receptacle)\r ".format(p_rec))

            for f in [f1, f2, f3]:
                f.write(")\n")

            for f in [f1, f2, f3]:
                f.write("(:init \r ")
            for s in sli:
                for f in [f1, f2, f3]:
                    f.write("\t(sliceable {})\r ".format(s))

            for h in hea:
                for f in [f1, f2, f3]:
                    f.write("\t(heatable {})\r ".format(h))
            # for c in cle:
            #     f.write('\t(cleanable {})\r '.format(c))
            for t in tog:
                for f in [f1, f2, f3]:
                    f.write("\t(toggable {})\r ".format(t))
            for c in coo:
                for f in [f1, f2, f3]:
                    f.write("\t(coolable {})\r ".format(c))

            if scene == "scene6" or scene == "scene7" or scene == "scene8":
                tmp_obj = random.sample(objects, 1)[0]
                for f in [f1, f2, f3]:
                    f.write("\t(objectAtLocation {} Floor1)\r ".format(tmp_obj))
                for rel in NEW_PART_TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS:
                    if rel.split()[1] == tmp_obj:
                        NEW_PART_TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS.remove(rel)
                        break

            all_predicates = []
            print_list = []
            # print("target obj", target_obj)
            for relationship in NEW_PART_TMP_VAL_RECEPTACLE_OBJECTS_RELATIONSHIPS:
                if scene in ["scene11", "scene12"]:  # control all books location
                    if target_obj in relationship or "Box" in relationship:
                        # print("relationship", relationship)
                        continue
                if scene in ["scene13", "scene14"]:
                    # print("Selected item is ", target_obj)

                    if target_obj in relationship or "Box" in relationship:
                        continue
                all_predicates.append(
                    (
                        relationship.split()[0],
                        relationship.split()[1],
                        relationship.split()[2],
                    )
                )
                # for f in [f1, f2, f3]:
                #
                #     f.write(
                #         '\t({} {} {})\r '.format(relationship.split()[0], relationship.split()[1], relationship.split()[2]))
                print_list.append(relationship.split()[1])
            # print("All predicates1", all_predicates)

            for obj in pre_obj:
                if obj not in receptacle_objects and obj not in print_list:
                    if scene in [
                        "scene12",
                        "scene13",
                        "scene11",
                        "scene10",
                        "scene14",
                    ] and obj.startswith(target_obj):
                        # print(all_predicates, target_obj)

                        continue
                    random_picked = random.sample(receptacle_objects, 1)[0]
                    all_predicates.append(("objectAtLocation", obj, random_picked))
            # print("All predicates", all_predicates)
            for relation, o1, o2 in all_predicates:
                for f in [f1, f2]:
                    f.write("\t({} {} {})\r ".format(relation, o1, o2))
            temp_lst = []
            if scene == "scene12" or scene == "scene11":
                temp_lst = []
                if scene == "scene12":
                    desks = [f"Box{i}" for i in range(1, 3)]
                if scene == "scene11":
                    desks = [f"Box{i}" for i in range(1, 4)]
                books = target_lst[:]
                # print(desks)
                # print(books, desks)
                for book_count in book_counts_per_box:
                    random.shuffle(desks)
                    random.shuffle(books)
                    curr_desk = desks.pop()
                    while book_count != 0:
                        book_count -= 1
                        temp_lst.append((curr_desk, books.pop()))
                random.shuffle(temp_lst)
                for result in temp_lst:
                    f.write(
                        "\t(objectAtLocation {} {})\r ".format(result[1], result[0])
                    )

                pre_obj = {
                    "target_type": target_obj,
                    "moved_object": moved_obj,
                }
            if scene in ["scene13", "scene14"]:
                if scene == "scene13":
                    temp_lst = []
                    # pick a destination book
                    temp_lst.append(
                        (
                            f"Box{random.randint(1, len(boxs))}",
                            target_obj,
                        )
                    )

                    # random place boxs on sofa
                    for box in boxs:
                        sofa = f"Sofa{random.randint(1,3)}"
                        temp_lst.append((sofa, box))

                    pre_obj = {"target_object": target_obj, "moved_object": moved_obj}

                if scene == "scene14":
                    temp_lst = []
                    # pick a destination book
                    box_layer_1 = f"Box{random.randint(1, len(boxs))}"
                    box_layer_2 = box_layer_1
                    while box_layer_2 == box_layer_1:
                        box_layer_2 = f"Box{random.randint(1, len(boxs))}"

                    temp_lst.append(
                        (
                            box_layer_1,
                            target_obj,
                        )
                    )
                    temp_lst.append((box_layer_2, box_layer_1))

                    # random place boxs on sofa
                    for box in boxs:
                        if box == box_layer_1:
                            continue
                        sofa = f"Sofa{random.randint(1,3)}"
                        temp_lst.append((sofa, box))

                    # random.shuffle(temp_lst)
                    pre_obj = {"target_object": target_obj, "moved_object": moved_obj}

                # print("Before", temp_lst)

            for result in temp_lst:
                f1.write("\t(objectAtLocation {} {})\r ".format(result[1], result[0]))
            random.shuffle(temp_lst)
            # print("After", temp_lst)
            for result in temp_lst:
                f2.write("\t(objectAtLocation {} {})\r ".format(result[1], result[0]))

            for o1, o2 in temp_lst:
                all_predicates.append(("objectAtLocation", o2, o1))

            random.shuffle(all_predicates)
            for relation, o1, o2 in all_predicates:
                f3.write("\t({} {} {})\r ".format(relation, o1, o2))

            for f in [f1, f2, f3]:
                f.write(")")

            json.dump(
                pre_obj,
                open(os.path.join(init_state_path, scene, f"pre_obj_{i}.json"), "w"),
            )
            json.dump(
                pre_obj,
                open(
                    os.path.join(
                        init_state_path + "_local_random", scene, f"pre_obj_{i}.json"
                    ),
                    "w",
                ),
            )
            json.dump(
                pre_obj,
                open(
                    os.path.join(
                        init_state_path + "_global_random", scene, f"pre_obj_{i}.json"
                    ),
                    "w",
                ),
            )
