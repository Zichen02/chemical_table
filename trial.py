import json
import os
from substance import substance
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple, Any

class trial:

    def __init__(self, name="", exp_name = "", composite=None, master=None, substance_conc=None, total_amount = 0, id = "", existing_amount = 0, stock=False, solvent = False, info=None):
        """
        需要all_trial都带上（键为trial的名字，值为列表（0：id，1：路由），隶属于Experiment类），进行查表找到地址的trial。试样唯一的标识符是名称，姑且带一个id好了，这个id可以在外部制定序号指定为唯一可寻的方式
        初始化一个Trial实例
        :param name: 试样的名字
        :param exp_name: 字符串，从属的实验名称，需要从属实验
        :param info: 试样的信息字典
        :param composite: 试样使用的其他试样的字典（由哪些些别人合成），key是试样名字字符串，value是用量 (应由地址计算或初始化得到)
        :param master: 试样被使用到其他试样的字典（用在了哪些合成中用了多少），key是试样名字字符串，value是用量 (应由地址计算或初始化得到)
        :param id: 用于更改名字？
        :param substance_conc: 试样的浓度字典，key是试样名字字符串，value是浓度
        :param existing_amount: float数字，剩余的数量，一般是体积，-1则为无限量
        :param total_amount: float数字，总共的数量，一般是体积，-1则为无限量
        :param stock: 布尔值，表示是否为实验最初制备的试样，没有composite，仅有substance_conc
        :param solvent: 布尔值，表示是否为实验中使用的试剂，没有composite，substance_conc可以自定（如摩尔数量每体积）
        """
        self.name = name
        self.info = info if info is not None else {}
        self.composite = composite if composite is not None else {}
        self.master = master if master is not None else {}
        self.substance_conc = substance_conc if substance_conc is not None else {}
        self.existing_amount = float(existing_amount)
        self.total_amount = float(total_amount)
        self.stock = bool(stock)
        self.solvent = bool(solvent)
        self.id = id
        self.exp_name = exp_name

    @staticmethod
    def create_stock(stock_name="", substance_conc=None, total_amount = -1, exp_name = "", solvent = False, id = "", s_info=None):
        """
        :param stock_name:
        :param substance_conc:
        :param total_amount:
        :param exp_name:
        :param solvent:
        :param s_info:
        :return: 该stock路由
        注意：引用此方法时需要在外部注意为all_trials 添加这个stock
        """
        the_stock = trial(name = stock_name, substance_conc=substance_conc, exp_name = exp_name, id = id, info=s_info,
                          total_amount = total_amount, existing_amount=total_amount, solvent= solvent, stock = True)
        return the_stock

    def compose(self, dict_of_trial, all_trials):
        """compose things from other trials, create trial object
        把自己一个个都拿出来，再按新的给的字典一个个加一遍
        :param dict_of_trial: key:name of other trial, value: amount to add in this trial
        """
        for trial_name, trial_number in self.composite.items():
            self.remove_from_composite(all_trials[trial_name], trial_number, all_trials)
        for trial_name, trial_number in dict_of_trial.items():
            self.add_to_composite(all_trials[trial_name], trial_number, all_trials)

    def is_regular_sample(self):
        """可能可以扩展"""
        if not self.stock and not self.solvent:
            return True
        else:
            return False

    def reaction_clear(self,reaction_rules):
        """
        更新可能的反应，加入后有反应的物质通过此计算得到反应结束后的状态，目前仅为预留
        :return:
        """
        pass


    def add_to_composite(self, trial_name, amount, all_trials, regardless_of_negative_amount = False):
        """
        加入，不含重算浓度函数，但master已经确保搞定
        :param trial_name:名字
        :param amount:
        :param all_trials:全trial查表，格式（键为trial的名字，值为列表（0：id，1：路由）
        :return:
        """
        if regardless_of_negative_amount:
            if all_trials[trial_name][1].existing_amount == -1:
                if trial_name in self.composite:
                    self.composite[trial_name] += amount
                    all_trials[trial_name][1].master[self.name] += amount
                else:
                    self.composite[trial_name] = amount
                    all_trials[trial_name][1].master[self.name] = amount
            else:
                if trial_name in self.composite:
                    self.composite[trial_name] += amount
                    all_trials[trial_name][1].master[self.name] += amount
                    all_trials[trial_name][1].existing_amount -= amount
                else:
                    self.composite[trial_name] = amount
                    all_trials[trial_name][1].master[self.name] = amount
                    all_trials[trial_name][1].existing_amount -= amount
        else:
            if trial_name in self.composite:
                if all_trials[trial_name][1].existing_amount == -1:
                    self.composite[trial_name] += amount
                    all_trials[trial_name][1].master[self.name] += amount
                elif all_trials[trial_name][1].existing_amount > amount:
                    self.composite[trial_name] += amount
                    all_trials[trial_name][1].master[self.name] += amount
                    all_trials[trial_name][1].existing_amount -= amount
                else:
                    raise ValueError("not enough to add")
            else:
                if all_trials[trial_name][1].existing_amount == -1:
                    self.composite[trial_name] = amount
                    all_trials[trial_name][1].master[self.name] = amount
                elif all_trials[trial_name][1].existing_amount > amount:
                    self.composite[trial_name] = amount
                    all_trials[trial_name][1].master[self.name] = amount
                    all_trials[trial_name][1].existing_amount -= amount
                else:
                    raise ValueError("not enough to add")
        print(f"trial: add_to_composite trial: {trial_name} added to: {self.name} amount: {amount}, current_self_composite: {self.composite}")

    def remove_from_composite(self, trial_name, amount, all_trials:Dict[str,List[Any]]):
        """
        从composite中减少一个trial的用量或移除
        :param trial_name: 待删除试样对象名
        :param amount: 用量，可以设定为-1来全部去除
        :param all_trials: 全trial查表，格式（键为trial的名字，值为列表（0：id，1：路由）
        """
        if trial_name in self.composite:
            if amount == -1:
                amount = self.composite[trial_name]
            if self.composite[trial_name] > amount:
                self.composite[trial_name] -= amount
                all_trials[trial_name][1].master[self.name] -= amount
            else:
                del self.composite[trial_name]
                del all_trials[trial_name][1].master[self.name]
            if not all_trials[trial_name][1].existing_amount == -1:
                all_trials[trial_name][1].existing_amount += amount
        else:
            raise ValueError(f"{trial_name} does not compose the trial f{self.name}")

    def change_name(self, new_name, all_trials):
        """
        修改试样的名字，同时更新所有引用此名字的地方
        :param new_name: 新名字
        :param all_trials: 全trial查表，格式（键为trial的名字，值为列表（0：id，1：路由）
        """
        old_name = self.name
        self.name = new_name

        for target_name, amount in self.composite.items():
            the_trial = all_trials[target_name][1]
            the_trial.master[new_name] = the_trial.master[old_name]
            del the_trial.master[old_name]
        for target_name, amount in self.master.items():
            the_trial = all_trials[target_name][1]
            the_trial.composite[new_name] = the_trial.composite[old_name]
            del the_trial.composite[old_name]

    def update_substance_conc(self, all_trials, assigned_amount=None):
        """
        通过composite中数量和composite中trial对象的substance_conc计算并更新该trial的substance_conc
        适用于composite已经加入完毕的情况，仅由composite更新substance_conc的情况, 使用了直接相乘除，需统一单位
        """
        if assigned_amount:
            total_amount = assigned_amount
        else:
            total_amount = sum(self.composite.values())
        if total_amount == 0 or total_amount < 0:
            raise Exception("amount<0")

        self.substance_conc = {}

        for the_trial_name, trial_num in self.composite.items():
            if the_trial_name in all_trials:
                the_trial = all_trials[the_trial_name][1]
                for sub_substance, sub_substance_conc in the_trial.substance_conc.items():
                    if sub_substance not in self.substance_conc:
                        self.substance_conc[sub_substance] = sub_substance_conc * trial_num / total_amount
                    else:
                        self.substance_conc[sub_substance] += sub_substance_conc * trial_num / total_amount

    @staticmethod
    def trial_design_recur(all_trials):
        pass

    def save_to_txt(self, filename):
        """将对象的属性数据保存为 JSON 文件"""
        data = self.__dict__.copy()
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_txt(cls, filename):
        """从 JSON 文件中加载数据并创建新的 trial 对象"""
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls(**data)