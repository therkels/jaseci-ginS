import os
from natsort import natsorted
import pickle
from jaclang.runtimelib.gins.cfg import CFG
from jaclang.runtimelib.gins.model import Gemini
from jaclang.compiler.semtable import SemRegistry
import random

def get_all_filenames(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
directory_path = os.path.join(os.path.dirname(__file__), "preds")

sorted_file_names = natsorted(get_all_filenames(directory_path))
# print(sorted_file_names)

data = []
sem_ir = ''

for file_name in sorted_file_names:
    with open(os.path.join(directory_path, file_name), "rb") as file:
        cfg_data=(pickle.load(file))
        if sem_ir == '':
            sem_ir = cfg_data['sem_ir']
        data.append({'input':cfg_data['input'], 'cfgs':cfg_data['cfgs']['hot_path']})

data = data[:-1]
frame_size = 10
counter = 0
new_cfg = data[0]['cfgs']
inputs = []
dataframe = []
for snapshot in data:
    if (counter-1) % frame_size == 0:
        
        dataframe.append({'input':inputs, 'cfgs':new_cfg})
        new_cfg = snapshot['cfgs']
        inputs = []
    else:
        new_cfg.__add__(snapshot['cfgs'])

    # print(snapshot['cfgs'].edge_counts)
    inputs.append(snapshot['input'])
    counter += 1

# print(len(dataframe))

# Shuffle the dataframe
random.shuffle(dataframe)

# Split the dataframe into 20:80 test and train set
split_index = int(len(dataframe) * 0.4)
test_set = dataframe[:split_index]
train_set = dataframe[split_index:]

def prompt_llm(data: dict, verbose: bool = False):
    prompt = """The following information is available for the program:
    Instructions per basic block:
    {instructions}
    Semantic and Type information from source code:
    {sem_ir}
    Control Flow Graph and edge frequency history:
    {cfgs}
    Inputs which crrrespond to the CFGs:
    {inputs}
    """

    cfg_history = ""
    ins_history = ""

    # Select 3 data from the train set arbitrarily
    selected_data = random.sample(train_set, 3)
    for i, snapshot in enumerate(selected_data):
        cfg = snapshot['cfgs']
        inputs = snapshot['input']
        cfg_history += f"CFG {i} of 3\n{cfg}"
        ins_history += f"Input set {i} of 3\n{inputs}"

    ins_string = ""
    
    ins_string += f"\n{data['cfgs'].display_instructions()}"

    prompt = prompt.format(
        cfgs=cfg_history, instructions=ins_string, sem_ir=sem_ir.pp(), inputs=ins_history
    )

    prompt += "\nPredict the edge frequency for the next basic block in the CFG"
    # prompt += "\n(Reason about the program using cfg, semantic and type information. Instead of saying what BB could be improved, reason about the program itself and what improvements could be made.)"
    # prompt += "\n If variable values are available, reason about at what point did a variable cause an issue"
    # prompt += "\n Please use the following information fill in predicted_edges[freq] for each BB edge with something completely random"
    if verbose:
        print(prompt)
    
    model = Gemini()
    cfg_predict = model.generate_structured(prompt)

    return cfg_predict

for i,data in enumerate(test_set):
    print(f"Predicting for {i} of {len(test_set)}")
    predict = prompt_llm(data)
    test_set[i]['Predicted'] = predict
    # print(test_set[i])


with open(os.path.join(directory_path, "predictions.pkl"), "wb") as file:
    pickle.dump(test_set, file)
