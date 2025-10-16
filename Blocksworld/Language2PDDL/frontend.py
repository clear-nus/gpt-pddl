from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os
import yaml
import json

app = Dash(__name__)

RESULT_DIR = "results/completion/pddl_files/blocksworld"
dataset_list = os.listdir(RESULT_DIR)
dataset_list = [ x for x in dataset_list if x.endswith(".txt") ]
CONFIG_DIR = "domains/blocksworld/gen_data_config.yaml"
config = None
dataset_types = []
with open(CONFIG_DIR) as f:
    config = yaml.safe_load(f)
    for key, value in config.items():
        if isinstance(value, dict):
            dataset_types.append({"label": value["description"], "value": key})

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            options=[
                {"label": "Corresponding example", "value": "oneshot"},
                {"label": "Standard example", "value": "weak_oneshot"},
            ],
            value="oneshot",
            id="example"
        ),
        dcc.Dropdown(
            options=[
                "code-davinci-002",
            ],
            value="code-davinci-002",
            id="model"
        ),
        dcc.Dropdown(
            options=dataset_types,
            id="dataset-type"
        ),
        dcc.Dropdown(id="obj-num"),
        dcc.Dropdown(id="variant"),
        # dcc.Dropdown(
        #     options=dataset_list,
        #     id='completion-name'
        # ),
        dcc.Dropdown(
            options=[],
            id='instance-idx'
        ),
        dcc.RadioItems(
            ["goal", "list", "lang", "check_obj_list", "check_color_list", "check_on_pred", "check_table_pred", "check_clear_pred"],
            value="goal",
            id="mode-option"
        ),
        dcc.Checklist(
            ["Show prompt"],
             id="display-option"
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div(id="instance")          
], style={'width': '48%', 'float': 'left', 'display': 'inline-block'})

@app.callback(
    Output('obj-num', 'options'),
    Output('variant', 'options'),
    Output('instance-idx', 'options'),
    Output('instance', 'children'),
    Input('example', 'value'),
    Input('model', 'value'),
    Input('dataset-type', 'value'),
    Input('obj-num', 'value'),
    Input('variant', 'value'),
    # Input('completion-name', 'value'),
    Input('instance-idx', 'value'),
    Input('display-option', 'value'),
    Input('mode-option', 'value'))
def update_instance(example, model, dataset_type, obj_num, variant, instance_idx, display_option, mode_option):
    obj_num_options = []
    variant_options = []
    instance_options = []
    instance = ""
    
    if not type(dataset_type) == str:
        return obj_num_options, variant_options, instance_options, instance
    obj_num_options = config[dataset_type]["n_obj_list"]

    if not type(obj_num) == int:
        return obj_num_options, variant_options, instance_options, instance
    
    dataset_name = config[dataset_type]["dataset_template"].format(obj=obj_num, shuffled="True", mode="test")
    result_prefix = "{}-{}-{}".format(example, model, dataset_name)
    for candidate in dataset_list:
        if candidate.startswith(result_prefix):
            variant_options.append(candidate[len(result_prefix):])
    
    if not type(variant) == str or not variant in variant_options:
        return obj_num_options, variant_options, instance_options, instance
            
    completion_name = result_prefix + variant
    print(completion_name)
    completion_path = os.path.join(RESULT_DIR, completion_name)
    dataset_path = "data/prob_finetuning_dataset/goal_pred_{}.txt".format(dataset_name)
    
    if mode_option != "goal":
        if mode_option.startswith("check"):
            completion_path = completion_path.replace("pddl_files", "check_refined_files")
            completion_path = completion_path.replace("mode_test", "mode_{}".format(mode_option))
            dataset_path = dataset_path.replace("prob_finetuning_dataset", "check_refined_finetuning_dataset")
            dataset_path = dataset_path.replace("mode_test", "mode_{}".format(mode_option))
        else:
            completion_path = completion_path.replace("pddl_files", mode_option+"_files")
            dataset_path = dataset_path.replace("prob_finetuning_dataset", mode_option+"_finetuning_dataset")
        if not os.path.exists(completion_path) or not os.path.exists(dataset_path):
            print("not found:", completion_path, dataset_path)
            return obj_num_options, variant_options, instance_options, instance
        

    with open(completion_path) as fc, open(dataset_path) as fd:
        targets = fc.readlines()
        labels = fd.readlines()
        instance_options = list(range(len(targets)))
        if not isinstance(instance_idx, int) or instance_idx >= len(targets):
            print("invalid instance index")
            return obj_num_options, variant_options, instance_options, instance
        label = labels[instance_idx]
        target = targets[instance_idx]
        entry = json.loads(target.strip())
        label = json.loads(label.strip())
        prompt = entry["prompt"]
        answer = entry["completion"]
        goal = label["goal"]
        if type(display_option) == list and "Show prompt" in display_option:
            instance = "prompt:\n{}\ngoal:\n{}\nanswer:\n{}".format(prompt, goal, answer)
        else:
            instance = "goal:\n{}\nanswer:\n{}".format(goal, answer)
        text_list = instance.split("\n")
        content = []
        for t in text_list:
            content.append(t)
            content.append(html.Br())
        instance = html.P(content)
        return obj_num_options, variant_options, instance_options, instance

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)