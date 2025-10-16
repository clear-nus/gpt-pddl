from openai import OpenAI
import os


client = OpenAI(api_key='your_api_key') #yj


path = '../generated_tasks_pddl/'
oneshot = True


def generation(domain_file, nl, init_state_file,scene, instance_id, oneshot_id, translation_prompt_instruction_q):
    if oneshot_id > 0:
        oneshot_problem_file = os.path.join(path, 'task_%s.pddl' % oneshot_id)
        oneshot_problem_nogoal_file = os.path.join(path, 'task_%s_nogoal.pddl' % oneshot_id)
        oneshot_problem_goal_file = os.path.join(path, 'task_%s_goal.pddl' % oneshot_id)
        oneshot_nl_file = os.path.join(path, 'task_%s.nl' % oneshot_id)
        oneshot_problem_pddl = open(oneshot_problem_file, "r").read()
        oneshot_problem_nogoal_pddl = open(oneshot_problem_nogoal_file, "r").read()
        oneshot_problem_goal_pddl = open(oneshot_problem_goal_file, "r").read()
        oneshot_nl = open(oneshot_nl_file, "r").read()

    elif oneshot_id == -1:  # kitchen example
        oneshot_problem_goal_pddl = '''
        (:goal (and
                (objectAtLocation Cup1 Cabinet1)
                (objectAtLocation Pot1 CounterTop1)
                (objectAtLocation Bread1 Fridge1)
                (objectAtLocation Mug1 Cabinet1)
                (objectAtLocation Potato1 Fridge1)
                (objectAtLocation Tomato1 Fridge1)
                (objectAtLocation Plate1 Cabinet1)
                (objectAtLocation Egg1 Fridge1)
                (objectAtLocation Spatula1 Cabinet1)
                (objectAtLocation SoapBottle1 CounterTop1)
            )
        )
        '''
        oneshot_nl = "Clean up the kitchen."
        oneshot_problem_nogoal_pddl = '''
        (:objects 
     	(Pot1 - object)
     	(Spatula1 - object)
     	(Cup1 - object)
     	(Plate1 - object)
     	(Bread1 - object)
     	(Egg1 - object)
     	(SoapBottle1 - object)
     	(Mug1 - object)
     	(Tomato1 - object)
     	(Potato1 - object)
     	(Plate2 - receptacle)
     	(CounterTop3 - receptacle)
     	(GarbageCan2 - receptacle)
     	(Bowl1 - receptacle)
     	(CounterTop2 - receptacle)
     	(Cabinet1 - receptacle)
     	(Plate1 - receptacle)
     	(Fridge1 - receptacle)
     	(GarbageCan1 - receptacle)
     	(CounterTop1 - receptacle)
     	(Sink1 - receptacle)
     	(Oven1 - receptacle)
     	(Microwave1 - receptacle)
     	(Floor1 - receptacle)
     )
    (:init 
     	(sliceable Egg1)
     	(sliceable Bread1)
     	(sliceable Tomato1)
     	(sliceable Potato1)
     	(heatable Plate2)
     	(heatable Cup1)
     	(heatable Plate1)
     	(heatable Bread1)
     	(heatable Egg1)
     	(heatable Mug1)
     	(heatable Tomato1)
     	(heatable Potato1)
     	(coolable Plate2)
     	(coolable Bowl1)
     	(coolable Pot1)
     	(coolable Cup1)
     	(coolable Plate1)
     	(coolable Bread1)
     	(coolable Egg1)
     	(coolable Mug1)
     	(coolable Tomato1)
     	(coolable Potato1)
     	(objectAtLocation Cup1 Floor1)
     	(objectAtLocation Pot1 Fridge1)
     	(objectAtLocation Bread1 CounterTop2)
     	(objectAtLocation Mug1 Plate1)
     	(objectAtLocation Potato1 Microwave1)
     	(objectAtLocation Tomato1 CounterTop3)
     	(objectAtLocation Plate1 Cabinet1)
     	(objectAtLocation Egg1 Plate2)
     	(objectAtLocation Spatula1 Bowl1)
     	(objectAtLocation SoapBottle1 CounterTop1)
     )'''
    elif oneshot_id == -2:  # living room example
        oneshot_problem_goal_pddl = '''
        (:goal (and
                (objectAtLocation CreditCard1 Desk1)
                (objectAtLocation KeyChain1 Drawer1)
                (objectAtLocation RemoteControl1 Desk1)
                (objectAtLocation Cloth1 Desk1)
                (objectAtLocation KeyChain2 Drawer1)
                (objectAtLocation KeyChain3 Drawer1)
                (objectAtLocation KeyChain4 Drawer1)
                (objectAtLocation Mug1 Desk1)
                (objectAtLocation Pillow1 Sofa5)
                (objectAtLocation RemoteControl2 Desk1)
            )
        )
        '''
        oneshot_nl = 'Clean up the living room'
        oneshot_problem_nogoal_pddl = '''
        (:objects 
     	(Pillow1 - object)
     	(RemoteControl1 - object)
     	(KeyChain2 - object)
     	(KeyChain4 - object)
     	(RemoteControl2 - object)
     	(KeyChain1 - object)
     	(Cloth1 - object)
     	(KeyChain3 - object)
     	(CreditCard1 - object)
     	(Sofa5 - receptacle)
     	(Box2 - receptacle)
     	(Bowl1 - receptacle)
     	(Sofa6 - receptacle)
     	(Sofa3 - receptacle)
     	(Plate1 - receptacle)
     	(Box1 - receptacle)
     	(Sofa2 - receptacle)
     	(Mug1 - receptacle)
     	(Sofa1 - receptacle)
     	(Bowl2 - receptacle)
     	(Sofa4 - receptacle)
     	(Desk1 - receptacle)
     	(Floor1 - receptacle)
     )
    (:init 
     	(heatable Plate1)
     	(heatable Mug1)
     	(coolable Plate1)
     	(coolable Bowl2)
     	(coolable Mug1)
     	(coolable Bowl1)
     	(objectAtLocation CreditCard1 Floor1)
     	(objectAtLocation KeyChain1 Bowl1)
     	(objectAtLocation RemoteControl1 Bowl2)
     	(objectAtLocation Cloth1 Sofa2)
     	(objectAtLocation KeyChain2 Sofa2)
     	(objectAtLocation KeyChain3 Sofa3)
     	(objectAtLocation KeyChain4 Plate1)
     	(objectAtLocation Box1 Sofa4)
     	(objectAtLocation Pillow1 Sofa5)
     	(objectAtLocation RemoteControl2 Sofa1)
     )
        '''
    elif oneshot_id == -3:  # cut vegatables example
        oneshot_problem_goal_pddl = '''
        (:goal (and
                (isSliced Tomato1)
                (isSliced Potato1)
                (inReceptacle Tomato1 Plate1)
                (inReceptacle Potato1 Plate2)
            )
        )
        '''
        oneshot_nl = "Cut me some vegetables."
        oneshot_problem_nogoal_pddl = '''
        (:objects 
     	(Pot1 - object)
     	(Spatula1 - object)
     	(Cup1 - object)
     	(Plate1 - object)
     	(Bread1 - object)
     	(Egg1 - object)
     	(SoapBottle1 - object)
     	(Mug1 - object)
     	(Tomato1 - object)
     	(Potato1 - object)
     	(Plate2 - receptacle)
     	(CounterTop3 - receptacle)
     	(GarbageCan2 - receptacle)
     	(Bowl1 - receptacle)
     	(CounterTop2 - receptacle)
     	(Cabinet1 - receptacle)
     	(Plate1 - receptacle)
     	(Fridge1 - receptacle)
     	(GarbageCan1 - receptacle)
     	(CounterTop1 - receptacle)
     	(Sink1 - receptacle)
     	(Oven1 - receptacle)
     	(Microwave1 - receptacle)
     	(Floor1 - receptacle)
     )
    (:init 
     	(sliceable Egg1)
     	(sliceable Bread1)
     	(sliceable Tomato1)
     	(sliceable Potato1)
     	(sliceable Apple1)
     	(heatable Plate2)
     	(heatable Cup1)
     	(heatable Plate1)
     	(heatable Bread1)
     	(heatable Egg1)
     	(heatable Mug1)
     	(heatable Tomato1)
     	(hetable Apple1)
     	(heatable Potato1)
     	(coolable Plate2)
     	(coolable Bowl1)
     	(coolable Pot1)
     	(coolable Cup1)
     	(coolable Plate1)
     	(coolable Bread1)
     	(coolable Egg1)
     	(coolable Mug1)
     	(coolable Tomato1)
     	(coolable Potato1)
     	(coolable Apple1)
     	(objectAtLocation Cup1 Floor1)
     	(objectAtLocation Pot1 Fridge1)
     	(objectAtLocation Bread1 CounterTop2)
     	(objectAtLocation Mug1 Plate1)
     	(objectAtLocation Potato1 Microwave1)
     	(objectAtLocation Tomato1 CounterTop3)
     	(objectAtLocation Plate1 Cabinet1)
     	(objectAtLocation Egg1 Plate2)
     	(objectAtLocation Spatula1 Bowl1)
     	(objectAtLocation SoapBottle1 CounterTop1)
     )'''




    with open(init_state_file, 'r') as f:
        problem_nogoal_pddl = f.read()
    domain_pddl = open(domain_file, "r").read()

    translation_prompt_instruction = 'Write the goal state in pddl. Do not use "not" in goal specification. '
    translation_prompt_instruction_nl = 'Write the goal specification in natural language.'
    translation_prompt = domain_pddl + '\n' + problem_nogoal_pddl + '\n' + nl + '\n' + translation_prompt_instruction
    translation_prompt_nl = domain_pddl + '\n' + problem_nogoal_pddl + '\n' + nl + '\n' + translation_prompt_instruction_nl
    translation_prompt_q = domain_pddl + '\n' + problem_nogoal_pddl + '\n' + nl + '\n' + translation_prompt_instruction_q

    if oneshot:
        translation_prompt = domain_pddl + '\n' + 'Q: '+ oneshot_problem_nogoal_pddl + '\n' + oneshot_nl + '\n' + translation_prompt_instruction + 'A: ' + oneshot_problem_goal_pddl + '\n' + 'Q: ' + problem_nogoal_pddl + '\n' + nl + '\n' + translation_prompt_instruction + 'A: '

        translation_prompt_nl = domain_pddl + '\n' + 'Q: ' + oneshot_problem_nogoal_pddl + '\n' + oneshot_nl + '\n' + translation_prompt_instruction + 'A: ' + oneshot_problem_goal_pddl + '\n' + 'Q: ' + problem_nogoal_pddl + '\n' + nl + '\n' + translation_prompt_instruction_nl + 'A: '

        translation_prompt_q = domain_pddl + '\n' + 'Q: ' + oneshot_problem_nogoal_pddl + '\n' + oneshot_nl + '\n' + translation_prompt_instruction + 'A: ' + oneshot_problem_goal_pddl + '\n' + 'Q: ' + problem_nogoal_pddl + '\n' + nl + '\n' + translation_prompt_instruction_q + 'A: '

    completion = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": "You will read PDDL domain and PDDL problem files, along with a natural language instruction. You need to translate the natural language instruction into a PDDL goal state. Don't include any explanation nor description. Output PDDL goal state only."},
        {"role": "user", "content": translation_prompt}
    ]
    )
    translation_response = completion.choices[0].message.content

    completion = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": "You will read PDDL domain and PDDL problem files, along with a natural language instruction. You need to translate the natural language instruction into a PDDL goal state. Don't include any explanation nor description. Output PDDL goal state only."},
        {"role": "user", "content": translation_prompt_nl}
    ]
    )
    translation_response_nl = completion.choices[0].message.content

    completion = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": "You will read PDDL domain and PDDL problem files, along with a natural language instruction. You need to translate the natural language instruction into a PDDL goal state. Don't include any explanation nor description. Output PDDL goal state only."},
        {"role": "user", "content": translation_prompt_q}
    ]
    )
    translation_response_q = completion.choices[0].message.content


    
    temp_output = "\n########### {} - {} ##########\n".format(scene, instance_id)

    temp_output += "\n******* problem file for debug *********\n"
    temp_output += problem_nogoal_pddl
    temp_output += '\nOutput:\n'
    temp_output += translation_response
    temp_output += "\n****** Goal in Natural Language query ********\n"
    temp_output += translation_prompt_instruction_nl
    temp_output += '\nOutput:\n'
    temp_output += translation_response_nl
    temp_output += "\n******* Domain understanding query ********\n"
    temp_output += translation_prompt_instruction_q
    temp_output += '\nOutput:\n'
    temp_output += translation_response_q

    return temp_output

nl = {
    'food_pre1': 'Put the sliced tomato on the sliced bread and then put them on the plate.',
    'food_pre2': 'Cut some fruits and put them on the plate',
    'food_pre3': 'Make a tomato sandwich.',
    'food_pre4': 'Prepare a meal and put it on the table.',
    'scene1': 'Put the ice cream in the fridge.',
    'scene2': 'Put the ice cream where it belongs.',
    'scene3': 'Put the newspaper where it belongs.',
    'scene4': 'Set the table for two persons.',
    'scene5': 'Set the table.',
    'scene6': 'Clean up the kitchen.',
    'scene7': 'Clean up the living room',
    'scene8': 'Clean up the bedroom.'
}
domain_understanding_q = {
    # 'food_pre1': 'Put the sliced tomato on the sliced bread and then put them on the plate.',
    'food_pre2': 'What are the fruits?',
    # 'food_pre3': 'Make a tomato sandwich.',
    'food_pre4': 'What does "prepare a meal" mean? What are the relevant objects for preparing a meal?',
    # 'scene1': 'Put the ice cream in the fridge.',
    'scene2': 'Where does the ice-cream belong?',
    # 'scene3': 'Put the newspaper where it belongs.',
    'scene4': 'What does "set the table" mean? What are the relevant objects for setting the table?',
    # 'scene5': 'Set the table.',
    'scene6': 'What does "clean up the kitchen" mean? What are the objects relevant objects for cleaning up the kitchen? Where to put them?',
    # 'scene7': 'Clean up the living room',
    # 'scene8': 'Clean up the bedroom.'
}
oneshot_example_id = {'food_pre2': -3, 'food_pre4': -3, 'scene2': 97146, 'scene4': 97146, 'scene6': -1}

if __name__ == '__main__':
    base_dir = './'
    domain_file = './domain/domain_updated.pddl'
    # scenes = ['food_pre2', 'food_pre4', 'scene2', 'scene4', 'scene6']
    scenes = ['food_pre4']
    if oneshot:
        save_name = '.oneshot.pddl'
    else:
        save_name = '.zeroshot.pddl'
    for scene in scenes:
        oneshot_id = oneshot_example_id[scene]
        translation_prompt_instruction_q = domain_understanding_q[scene]
        for i in range(1,21):
            init_state_file = base_dir + scene + '/init_state_' + str(i) + '.pddl'
            goal_state_file = base_dir + scene + '/goal_state_' + str(i) + save_name
            output = generation(domain_file, nl[scene], init_state_file, scene, i, oneshot_id, translation_prompt_instruction_q)

            print (output)
            with open(goal_state_file, 'w') as f:
                f.write(output)
        f.close()