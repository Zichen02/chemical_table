from trial import trial
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import json
from collections import defaultdict, deque

class Experiment:

    def __init__(self, name, sample_dict: Dict[str, List[Any]]  = {},
                 substance_dict: Dict[str, List[Any]] = {},
                 id_trial_name: Dict[str, str] = {}, table_id=None, extra_info=None, date=None):
        """
        这里需要一个id管理系统，与前端挂钩
        :param name:
        :param sample_dict:all_trials 就是所有的trial名字为键，trial的值为列表[id，路由]
        :param id_trial_name: id:trial名字 的字典
        :param table_id:
        :param substance_dict: 就是所有的substance名字为键，substance的值为列表[id，路由]
        :param extra_info:
        :param date:
        """
        self.name = name
        self.sample_dict = sample_dict
        ##sample_dict 是名字：地址，用来储存所有相关sample访问方式
        self.substance_dict = substance_dict
        ##substance_dict 是名字：地址，用来储存所有相关sample访问方式，则为仅有名字的简单物质记录
        self.table_id = table_id if table_id else Experiment.generate_serial_number()
        self.id_trial_name = id_trial_name
        self.extra_info = extra_info if extra_info is not None else {}
        self.date = date

    def get_trial(self, trial_name=None, trial_id=None):
        if trial_name:
            if trial_name not in self.sample_dict:
                print(f"trial_name {trial_name} not found in sample_dict")
            trial_in_sample_dict = self.sample_dict[trial_name]
            the_trial = trial_in_sample_dict[1]
            return the_trial
        elif trial_id:
            if trial_id not in self.id_trial_name:
                print(f"trial_id {trial_id} not found in id_trial_name")
            trial_name = self.id_trial_name[trial_id]
            trial_in_sample_dict = self.sample_dict[trial_name]
            the_trial = trial_in_sample_dict[1]
            return the_trial
        else:
            print("Either trial_name or trial_id must be provided")


    @staticmethod
    def generate_serial_number(ini=None):
        """
        生成一个随机序列号，可以根据需要修改逻辑
        """
        import random
        suffix = str(ini) if ini is not None else ""
        return "Experiment-" + str(random.randint(10000000, 99999999))

    def gen_substance_trial_dict(self):
        returning_dict = {}
        for trial_keys, trial_lists in self.sample_dict.items():
            the_trial = trial_lists[1]
            for substance_name, substance_concs in the_trial.substance_conc.items():
                if substance_concs > 0:
                    if substance_name in returning_dict:
                        returning_dict[substance_name].append(trial_keys)
                    else:
                        returning_dict[substance_name] = [trial_keys]
        self.extra_info["substance_trial_dict"] = returning_dict
        return returning_dict


    def generate_trial(self, the_trial):
        #总之这里就是你得先创建一个trial再加进来
        print(f"generate_trial: Adding trial: id: {the_trial.id}, name:{the_trial.name} into Experiment {self.name}")
        self.sample_dict[the_trial.name] = [the_trial.id, the_trial]
        if the_trial.id in self.id_trial_name:
            ori_trial_name = self.id_trial_name[the_trial.id]
            ori_trial = self.sample_dict[ori_trial_name][1]
            self.remove_trial(ori_trial)
            del self.id_trial_name[the_trial.id]
        self.id_trial_name[the_trial.id] = the_trial.name
        for keys, conc_num in the_trial.substance_conc.items():
            if keys not in self.substance_dict:
                self.substance_dict[keys] = []

    def remove_trial(self, the_trial:trial, trial_name = None, keep_substance = False):
        #keep_substance 0 and 1, whether keep the substances，从substance_dict中抹除
        print(f"removing trial {the_trial.name}, {the_trial.id}")
        if the_trial:
            trial_obj = the_trial
        else:
            trial_obj = self.get_trial(trial_name=trial_name)

        del self.id_trial_name[trial_obj.id]
        del self.sample_dict[trial_obj.name]

        if not keep_substance:
            substance_trial_dict = self.gen_substance_trial_dict()
            for substances, trial_lists in substance_trial_dict.items():
                if trial_name in trial_lists:
                    trial_lists.remove(trial_name)
            for substances, trial_lists in substance_trial_dict.items():
                if trial_lists == []:
                    del self.substance_dict[substances]
        else:
            pass

    def change_trial_name(self, new_trial_name:str, trial_id : str = None, ori_trial_name:str = None, ori_trial:trial =None):
        ##修改一个id所对应的trial的名字及其相关，不含trial中互作的情况
        if trial_id is None and ori_trial_name is None and ori_trial is None:
            print("No original trial info input to change name")

        if ori_trial:
            ori_trial_name = ori_trial.name
        elif ori_trial_name:
            ori_trial = self.get_trial(trial_name=ori_trial_name)
        elif trial_id:
            ori_trial_name = self.id_trial_name[trial_id]
            self.id_trial_name[trial_id] = new_trial_name
            ori_trial = self.get_trial(trial_name=ori_trial_name)

        list_trial = self.sample_dict[ori_trial_name]
        del (self.sample_dict[ori_trial_name])
        self.sample_dict[new_trial_name] = list_trial

        print(f"name of trial changed: {ori_trial_name} into {new_trial_name}")


    def stock_from_2d_array(self,
        stacked_chem_op_2D_array: Dict[str, Dict[str, float]],
        id_array: [List[str]] = None):
        print("success getting into stock_from_2d_array")
        num_trials = len(stacked_chem_op_2D_array)
        if id_array is None or "":
            id_array = [Experiment.generate_serial_number() + str(i) for i in range(num_trials)]
        if len(id_array) != num_trials:
            print("stock_from_2d_array: id_array长度必须与输入数据行数一致")
            id_array = [Experiment.generate_serial_number() + str(i) for i in range(num_trials)]
        #创建所有stock
        try:
            for (trial_name, substance_dict), trial_id in zip(
                stacked_chem_op_2D_array.items(), id_array):
                    print("stock_creation initialized")

                    if len(substance_dict) == 0 or substance_dict is None:
                        new_trial = trial(
                            name=trial_name,
                            exp_name=self.name,
                            id=trial_id,
                            stock=True,
                            solvent = True
                        )
                    # 创建试样实例（假设Trial类已正确定义）
                    else:
                        new_trial = trial(
                        name=trial_name,
                        exp_name=self.name,
                        id = trial_id,
                        substance_conc=substance_dict,
                        stock= True
                        )
                    #将试样添加到实验（假设generate_trial处理注册到sample_dict）
                    if trial_name in self.sample_dict:
                        self.sample_dict[trial_name][1] = new_trial
                    else:
                        self.generate_trial(new_trial)
                    print(f"stock generated: {new_trial}, name: {new_trial.name}, substance_conc: {new_trial.substance_conc}\n")

        except Exception as e:
            print("stock generation failed from stock_from_2d_array")
            raise RuntimeError(f"创建试样失败: {str(e)}") from e


    def new_exp_from_2d_array(
        self,
        stacked_chem_op_2D_array,
        id_array: List[str] = None,) -> None:
        print("success getting into new_exp_from_2d_array")
        """
        从二维字典结构批量创建试样并建立组分关系（优化后版本）

        Args:
            stacked_chem_op_2D_array: 外层键为试样名，内层键为组分名，值为用量。
                                     示例: {"Sample1": {"Water": 10.0, "Salt": 5.0}}
            id_array: 每个试样的ID列表，长度需与stacked_chem_op_2D_array一致，必选，根据这个调整或创建
            changed_rows: 与id array同长度，顺序地用1表示“该行内容被修改过”，0为“未被修改”
        Raises:
            ValueError: 输入数据格式错误或依赖缺失
            还需要考虑到stock的问题，因为stock会在conc表格更新后加入到exp表格，也许在此时进行一次update_exp
        """
        if not stacked_chem_op_2D_array:
            return  # 无数据直接返回

        # 预处理ID数组
        num_trials = len(stacked_chem_op_2D_array)
        if id_array is None or all(item == "" for item in id_array):
            fake_root = Experiment.generate_serial_number()
            id_array = [fake_root + str(i) for i in range(num_trials)]
        elif len(id_array) != num_trials:
            print("new_exp_from_2d_array: id_array长度必须与输入数据行数一致")
            fake_root = Experiment.generate_serial_number()
            id_array = [fake_root + str(i) for i in range(num_trials)]

        # 第零阶段：清空自身除stock外trial
        print("new_exp_from_2d_array: starting, phase 0 clearing")
        keys_to_remove = []
        for names, id_adds in self.sample_dict.items():
            the_trial = id_adds[1]
            if the_trial.stock and names in stacked_chem_op_2D_array:
                pass
            else:
                keys_to_remove.append(names)

        for key in keys_to_remove:
            id_adds = self.sample_dict[key]
            self.sample_dict.pop(key)
            self.id_trial_name.pop(id_adds[0])

        # 第一阶段：创建所有试样
        print("new_exp_from_2d_array: starting, phase 1 generating")
        try:
            for (trial_name, composite_dict), trial_id in zip(
                stacked_chem_op_2D_array.items(), id_array
            ):


                if trial_id in self.id_trial_name:
                    the_trial_name = self.id_trial_name[trial_id]
                    the_trial = self.sample_dict[the_trial_name][1]
                    self.change_trial_name(trial_name, ori_trial= the_trial)

                else:
                    # 创建试样实例（假设Trial类已正确定义）
                    new_trial = trial(
                    name=trial_name,
                    exp_name=self.name,
                    id=trial_id,
                    composite={},  # 先初始化空字典，后续填充
                    )
                    #将试样添加到实验（假设generate_trial处理注册到sample_dict）
                    self.generate_trial(new_trial)
        except Exception as e:
            raise RuntimeError(f"创建试样失败: {str(e)}") from e
        print("new_exp_from_2d_array: Success creating trials","\n","self sample_dict:",self.sample_dict)
        # 第二阶段：建立组分关系
        for (trial_name, composite_dict), trial_id in zip(
                stacked_chem_op_2D_array.items(), id_array,
        ):


                try:
                    subject_trial = self.get_trial(trial_id=trial_id)
                except KeyError:
                    raise ValueError(f"试样 {trial_id}:{trial_name} 未成功注册到sample_dict") from None

                for composite_name, composite_num in subject_trial.composite.items():
                    subject_trial.remove_from_composite(composite_name, -1, self.sample_dict)

                for composite_name, composite_num in composite_dict.items():
                    # 跳过无效数值
                    if not isinstance(composite_num, (int, float)):
                        print(f"警告: {composite_name} 的用量 {composite_num} 不是数字，已跳过")
                        continue

                    # 检查组分是否存在
                    composite_trial = self.sample_dict.get(composite_name)
                    if composite_trial is None:
                        raise ValueError(f"组分 {composite_name} 未找到，请检查输入数据")

                    # 添加组分关系（假设add_to_composite处理双向关联）
                    try:
                        subject_trial.add_to_composite(
                            trial_name=composite_name,
                            amount=float(composite_num),
                            all_trials = self.sample_dict,
                            regardless_of_negative_amount =True  # 假设支持用量验证
                        )
                    except ValueError as e:
                        raise ValueError(
                            f"试样 {trial_name} 添加组分 {composite_name} 失败: {str(e)}"
                        ) from e

    def update_all_concentrations(self):
        print(f"success getting into update_all_concentrations;\nself_sample_dict: {self.sample_dict}")
        """更新所有试样的浓度（适配 sample_dict 结构）"""
        trials = []
        stock = {}
        for v in self.sample_dict.values():
            if len(v) == 2:
                if not v[1].stock and not v[1].solvent:
                    trials.append(v[1])
                else:
                    stock[v[0]] = v[1].substance_conc
        if not trials:
            return
        print(f"\nall current stocks v.s. concs: update_all_concentrations says stock: {stock}")
        # 构建依赖图
        adj = defaultdict(list)
        in_degree = defaultdict(int)
        for trial in trials:
            for comp_name in trial.composite:
                comp_entry = self.sample_dict.get(comp_name)
                if not comp_entry:
                    print(f"composite {comp_name} not found")
                    continue
                comp_trial = comp_entry[1]
                if comp_trial in trials:
                    adj[comp_trial].append(trial)
                    in_degree[trial] += 1

        # 拓扑排序
        queue = deque([t for t in trials if in_degree.get(t, 0) == 0])
        sorted_trials = []
        while queue:
            current = queue.popleft()
            sorted_trials.append(current)
            for neighbor in adj[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        remaining_nodes = [t for t in trials if t not in sorted_trials]
        for node in remaining_nodes:
            if in_degree.get(node, 0) > 0:
                raise ValueError(f"存在循环依赖: 涉及试样 {node.name}")

        # 计算浓度
        for trial in sorted_trials:
            self._calculate_trial_concentration(trial)

    def _calculate_trial_concentration(self, trial: trial):
        print(f"success getting into _calculate_trial_concentration, trial: {trial.name}:{trial}")
        """浓度计算逻辑"""
        if trial.stock or trial.solvent:
            return

        ##total_vol = trial.total_amount
        total_vol = sum(trial.composite.values())
        """if total_vol <= 0:
            print(f"试样{trial.name}的 total_amount 无效")
            raise ValueError(f" {trial.name} 的 total_amount 无效")"""

        substance_amounts = defaultdict(float)
        for comp_name, vol_used in trial.composite.items():
            print(f"_calculate_trial_concentration:{trial.name}","comp_name & vol_used:",comp_name," ", vol_used)
            comp_entry = self.sample_dict.get(comp_name)
            if not comp_entry:
                continue
            comp_trial = comp_entry[1]
            for sub, conc in comp_trial.substance_conc.items():
                substance_amounts[sub] += conc * vol_used

        trial.substance_conc = {
            sub: amount / total_vol
            for sub, amount in substance_amounts.items()
        }
        print(f"{trial.name}'s substance_conc:{trial.substance_conc}")
    """
    def generate_trial(self, name="", exp_name = "", composite=None, master=None, substance_conc=None, total_amount = None, id = "", existing_amount = None, stock=False, solvent = False, info=None):

        the_stock = trial.create_stock(stock_name, substance_conc, total_amount, exp_name, solvent = False, id = id, s_info=s_info)
        self.sample_dict[stock_name] = [id,the_stock]
        for substances, substance_concs in substance_conc:
            if substances not in self.substance_dict:
                self.substance_dict[substances] = []
    """

    def design_concentration_advanced(
            self,
            target_conc: Dict[str, float],
            total_volume: float,
            min_volume: float = 1.0,
            max_volume: float = 100.0,
            max_retries: int = 3
    ) -> Tuple[str, Dict[str, float]]:
        """
        高级浓度设计算法（按物质约束优先+动态回退）

        Args:
            target_conc: 目标浓度 {物质: 浓度}
            total_volume: 总体积要求
            min_volume: 单试样最小使用体积
            max_volume: 单试样最大使用体积
            max_retries: 最大回退次数

        Returns:
            (试样名, {试样名: 使用体积})
        """
        # 生成物质-试样映射
        substance_trial_map = self.gen_substance_trial_dict()

        # 确定必须处理的物质（排除溶剂）
        target_substances = [k for k in target_conc if k != "solvent"]
        if not target_substances:
            raise ValueError("必须指定至少一个非溶剂物质")

        # 按物质的可选试样数量排序（最少优先）
        sorted_substances = sorted(
            target_substances,
            key=lambda x: len(substance_trial_map.get(x, [])))

        # 初始化体积分配
        used_trials = defaultdict(float)
        remaining_volume = total_volume

        # 递归尝试分配
        result = self._allocate_volumes_recursive(
            substances=sorted_substances,
            substance_trial_map=substance_trial_map,
            target_conc=target_conc,
            total_volume=total_volume,
            used_trials=used_trials,
            remaining_volume=remaining_volume,
            min_volume=min_volume,
            max_volume=max_volume,
            retry_count=0,
            max_retries=max_retries
        )

        if not result:
            raise ValueError("无法找到可行方案")

        # 处理溶剂体积
        final_volumes = self._handle_solvent(result, total_volume)

        # 创建最终试样
        final_name = f"MIX_ADV_{hash(tuple(sorted(target_conc)))}"
        self._create_final_trial(final_name, final_volumes, target_conc)
        return (final_name, final_volumes)

    def _allocate_volumes_recursive(
            self,
            substances: List[str],
            substance_trial_map: Dict[str, List[str]],
            target_conc: Dict[str, float],
            total_volume: float,
            used_trials: Dict[str, float],
            remaining_volume: float,
            min_volume: float,
            max_volume: float,
            retry_count: int,
            max_retries: int
    ) -> Optional[Dict[str, float]]:
        print(substances)
        print(used_trials)
        # 终止条件：所有物质处理完成
        if not substances:
            return dict(used_trials)

        current_sub = substances[0]
        candidates = substance_trial_map.get(current_sub, [])

        # 遍历当前物质的所有可用试样
        for trial_name in candidates:
            trial = self.sample_dict[trial_name][1]
            conc = trial.substance_conc.get(current_sub, 0)

            # 计算理论所需体积
            required_vol = (target_conc[current_sub] * total_volume) / conc
            required_vol = round(required_vol, 2)

            print(required_vol)
            print(min_volume)
            print(max_volume)

            # 体积约束检查
            if not (min_volume <= required_vol <= max_volume):
                continue


            # 临时分配
            used_copy = used_trials.copy()
            used_copy[trial_name] += required_vol
            new_remaining = remaining_volume - required_vol

            print(used_copy)

            # 递归处理下一个物质
            result = self._allocate_volumes_recursive(
                substances[1:],
                substance_trial_map,
                target_conc,
                total_volume,
                used_copy,
                new_remaining,
                min_volume,
                max_volume,
                retry_count,
                max_retries
            )

            if result is not None:
                return result

        # 回退机制：尝试更换前序物质的试样
        if retry_count < max_retries and len(substances) > 1:
            for i in range(1, len(substances)):
                prev_sub = substances[i]
                prev_candidates = substance_trial_map.get(prev_sub, [])
                if len(prev_candidates) > 1:
                    new_substances = substances.copy()
                    new_substances.pop(i)
                    new_substances.insert(0, prev_sub)
                    return self._allocate_volumes_recursive(
                        new_substances,
                        substance_trial_map,
                        target_conc,
                        total_volume,
                        used_trials,
                        remaining_volume,
                        min_volume,
                        max_volume,
                        retry_count + 1,
                        max_retries
                    )
        return None


    def _handle_solvent(
            self,
            volumes: Dict[str, float],
            total_volume: float
    ) -> Dict[str, float]:
        """处理溶剂体积"""
        current_total = sum(volumes.values())
        solvent_vol = total_volume - current_total
        if solvent_vol < 0:
            raise ValueError("体积超限")

        # 自动寻找溶剂（浓度全为0的试样）
        solvent_candidates = [
            name for name, (_, t) in self.sample_dict.items()
            if all(c == 0 for c in t.substance_conc.values())
        ]
        if solvent_candidates:
            solvent = solvent_candidates[0]
            volumes[solvent] = solvent_vol
        else:
            volumes["Solvent"] = solvent_vol  # 虚拟溶剂记录
        return volumes

    def _create_final_trial(
            self,
            name: str,
            volumes: Dict[str, float],
            target_conc: Dict[str, float]
    ):
        """创建最终试样记录"""
        final_trial = trial(
            name=name,
            exp_name=self.name,
            composite=volumes,
            total_amount=sum(volumes.values()),
            substance_conc=target_conc
        )
        self.generate_trial(final_trial)

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