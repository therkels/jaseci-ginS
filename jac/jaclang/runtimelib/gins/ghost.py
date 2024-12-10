"""The Shell Ghost code for gins
"""

import os
import sys
import threading
import pickle


from jaclang.runtimelib.gins.model import Gemini
from jaclang.runtimelib.gins.tracer import CFGTracker, CfgDeque


class ShellGhost:
    def __init__(self):
        self.cfgs = None
        self.cfg_cv = threading.Condition()
        self.tracker = CFGTracker()
        self.sem_ir = None

        self.finished_exception_lock = threading.Lock()
        self.exception = None
        self.finished = False
        self.variable_values = None

        self.model = Gemini()

        self.deque_lock = threading.Lock()
        self.__cfg_deque_dict = dict()
        self.__cfg_deque_size = 1000

        parent_dir = os.path.dirname(os.path.abspath(__file__))
        for i in range(3):
            parent_dir = os.path.dirname(parent_dir)

        self.input_path = os.path.join(
            parent_dir, 'examples/gins_scripts', 'preds/tmp_cfg.pkl')

    def set_cfgs(self, cfgs):
        self.cfg_cv.acquire()
        self.cfgs = cfgs
        self.cfg_cv.notify()
        self.cfg_cv.release()

    def update_cfg_deque(self, cfg, module):
        self.deque_lock.acquire()
        if module not in self.__cfg_deque_dict:
            self.__cfg_deque_dict[module] = CfgDeque(self.__cfg_deque_size)
        self.__cfg_deque_dict[module].add_cfg(cfg)
        self.deque_lock.release()

    def get_cfg_deque_repr(self):
        return self.__cfg_deque.display_cfgs()

    def start_ghost(self):
        self.__ghost_thread = threading.Thread(target=self.worker)
        self.__ghost_thread.start()

    def set_finished(self, exception: Exception = None):
        self.finished_exception_lock.acquire()
        self.exception = exception
        self.finished = True
        self.finished_exception_lock.release()

    def worker(self):
        # get static cfgs
        self.cfg_cv.acquire()
        if self.cfgs == None:
            print("waiting")
            self.cfg_cv.wait()
        # for module_name, cfg in self.cfgs.items():
        #     print(f"Name: {module_name}")
        self.cfg_cv.release()

        # Once cv has been notifie, self.cfgs is no longer accessed across threads
        current_executing_bbs = {}

        def update_cfg():
            exec_insts = self.tracker.get_exec_inst()

            # don't prompt if there's nothing new
            if exec_insts == {}:
                return

            for module, offset_list in exec_insts.items():
                try:
                    cfg = self.cfgs[module]

                    if (
                        module not in current_executing_bbs
                    ):  # this means start at bb0, set exec count for bb0 to 1
                        current_executing_bbs[module] = 0
                        cfg.block_map.idx_to_block[0].exec_count = 1

                    for offset in offset_list:
                        if (
                            offset
                            not in cfg.block_map.idx_to_block[
                                current_executing_bbs[module]
                            ].bytecode_offsets
                        ):
                            for next_bb in cfg.edges[current_executing_bbs[module]]:
                                if (
                                    offset
                                    in cfg.block_map.idx_to_block[
                                        next_bb
                                    ].bytecode_offsets
                                ):
                                    cfg.edge_counts[
                                        (current_executing_bbs[module], next_bb)
                                    ] += 1
                                    # do some deque op
                                    cfg.block_map.idx_to_block[next_bb].exec_count += 1
                                    current_executing_bbs[module] = next_bb
                                    break
                        assert (
                            offset
                            in cfg.block_map.idx_to_block[
                                current_executing_bbs[module]
                            ].bytecode_offsets
                        )
                except Exception as e:
                    self.set_finished(e)
                    print(e)
                    return

            self.variable_values = self.tracker.get_variable_values()
            self.update_cfg_deque(cfg.get_cfg_repr(), module)
            # self.logger.info(cfg.to_json())

        print("\nUpdating cfgs at the end")
        update_cfg()
        input_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples/gins_scripts')
        if not os.path.exists(os.path.dirname(input_dir)):
            os.makedirs(os.path.dirname(input_dir))
        pickled_ghost = {"input": float(
            sys.argv[-1]), "sem_ir": self.sem_ir, "cfgs": self.cfgs}
        with open(self.input_path, 'wb') as f:
            pickle.dump(pickled_ghost, f)
