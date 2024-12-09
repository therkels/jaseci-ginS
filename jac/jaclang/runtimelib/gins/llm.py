import pickle
import os
import re
from typing import List
from jaclang.runtimelib.gins.model import Gemini


def read_cfg_files(prefix='cfg', extension='.pkl'):
    directory = os.path.dirname(os.path.abspath(__file__))
    for i in range(3):
        directory = os.path.dirname(directory)
    directory = os.path.join(
        directory, 'examples', 'gins_scripts', 'preds')

    files = [f for f in os.listdir(directory) if f.startswith(
        prefix) and f.endswith(extension)]

    sorted_files = sorted(files, key=lambda x: int(
        re.search(r'\d+', x).group()))

    cfgs = []
    inputs = []
    for filename in sorted_files[:-1]:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'rb') as f:
            pickled_ghost = pickle.load(f)
            sem_ir = pickled_ghost["sem_ir"]
            cfgs.append(pickled_ghost["cfgs"])
            inputs.append(pickled_ghost["input"])

    filepath = os.path.join(directory, sorted_files[-1])
    with open(filepath, 'rb') as f:
        pickled_ghost = pickle.load(f)
        sem_ir = pickled_ghost["sem_ir"]
        inputs.append(pickled_ghost["input"])
        cfgs.append(pickled_ghost["cfgs"])

    return sem_ir, inputs, cfgs


def merge_cfgs(cfgs: List, inputs: List, num_cfgs: int = 25, start: int = 0):
    merged_cfgs = []
    merged_inputs = []
    for i in range(start, len(cfgs), num_cfgs):
        merged_cfg = cfgs[i]
        merged_input = [inputs[i]]
        for module in merged_cfg.keys():
            for j in range(i+1, i + num_cfgs):
                if j >= len(cfgs):
                    break
                merged_cfg[module] += cfgs[j][module]
                merged_input += [inputs[j]]
        merged_cfgs.append(merged_cfg)
        merged_inputs.append(merged_input)
    return merged_cfgs, merged_inputs


def prompt_llm():

    prompt = """
    Given a program with the following static CFG:
    With each basic block's instructions as follows:
    {instructions}
    and the following Semantic and Type information from source code:
    {sem_ir}
    From the following sequence of inputs and dynamic profile information, you must identify the missing profile information for the new inputs.
    {cfgs}
    """

    sem_ir, inputs, unmerged_cfgs = read_cfg_files()
    merged_cfgs, merged_inputs = merge_cfgs(unmerged_cfgs, inputs)

    cfg_string = ""
    ins_string = ""

    for i, cfgs in enumerate(merged_cfgs[:-1]):
        for module, cfg in cfgs.items():
            ins_string += f"Module: {module}\n{cfg.display_instructions()}"

    for i, cfgs in enumerate(merged_cfgs[:-1]):
        cfg_string += f"Inputs: {merged_inputs[i]}"
        for module, cfg in cfgs.items():
            cfg_history = cfg.get_cfg_repr()
            cfg_string += f"Module: {module}\n{cfg_history}"

    # print(cfg_string)

    prompt = prompt.format(
        cfgs=cfg_string,
        instructions=ins_string,
        sem_ir=sem_ir.pp()
    )

    print(f"ground truth: {merged_cfgs[-1]}")
    # prompt += f"I have the following inputs:\n{merged_inputs[-1]}\n"
    # print(prompt)

    # model = Gemini()
    # response = model.generate_structured(prompt)
    #
    # return response


prompt_llm()
