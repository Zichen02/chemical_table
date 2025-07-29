from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from Experiment import Experiment
from trial import trial

class chem_interface:

    """dict_of 是json传来的信息全字典，含有 词条：list """
    def __init__(self, dict_of_experiment={}, id_exp_name={}):
        """
        :param dict_of_experiment: Experiment，键为名字，值为列表[前端赋予exp的id，地址]
        :param id_exp_name: 指 id:experiment名字的字符串
        """
        self.dict_of_experiment = dict_of_experiment
        self.id_exp_name = id_exp_name
        self.property_vocab_list = []

    def get_experiment(self, exp_name=None, exp_id=None):
        """
        根据实验名称或实验ID获取对应的实验对象

        Args:
            exp_name: 实验名称
            exp_id: 实验ID

        Returns:
            Experiment: 对应的实验对象

        Raises:
            ValueError: 如果未提供exp_name或exp_id，或找不到对应的实验
        """
        if exp_name:
            if exp_name not in self.dict_of_experiment:
                print(f"实验名称 {exp_name} 不存在于dict_of_experiment中")
            exp_entry = self.dict_of_experiment[exp_name]
            return exp_entry[1]  # 返回实验对象（假设存储在列表的第二个位置）
        elif exp_id:
            if exp_id not in self.id_exp_name:
                print(f"实验ID {exp_id} 不存在于id_exp_name中")
            exp_name = self.id_exp_name[exp_id]
            exp_entry = self.dict_of_experiment[exp_name]
            return exp_entry[1]  # 返回实验对象
        else:
            print("必须提供exp_name或exp_id参数")

    def add_experiment(self, exp_name, exp_id, exp_address):
        """
        添加实验到interface
        :param exp_name: 实验名称
        :param exp_id: 前端赋予的实验ID
        :param exp_address: 实验地址
        """
        self.dict_of_experiment[exp_name] = [exp_id, exp_address]
        self.id_exp_name[exp_id] = exp_name

    def remove_experiment(self, exp_id = None, exp_name = None):
        """
        从interface中删除实验
        :param identifier: 实验的ID或名称
        """
        if exp_id:  # 如果传入的是ID
            if exp_id in self.id_exp_name:
                exp_name = self.id_exp_name[exp_id]
                del self.dict_of_experiment[exp_name]
                del self.id_exp_name[exp_id]
        elif exp_name:  # 如果传入的是名称
            if exp_name in self.dict_of_experiment:
                exp_id = self.dict_of_experiment[exp_name][0]
                del self.dict_of_experiment[exp_name]
                del self.id_exp_name[exp_id]

    @staticmethod
    def dict_to_table(nested_dict, symmetric=False):
        """
        将嵌套字典转换为带表头的二维数组。

        输入格式要求：
        {
            "元素名称1": {"表头1": 值1, "表头2": 值2, ...},
            "元素名称2": {"表头1": 值3, "表头2": 值4, ...},
            ...
        }

        参数:
            nested_dict (dict): 嵌套字典数据
            symmetric (bool): 是否使用对称模式，即表头行和表头列使用相同的键

        返回格式（标准模式）:
        [
            ["", "表头1", "表头2", ...],
            ["元素名称1", 值1, 值2, ...],
            ["元素名称2", 值3, 值4, ...],
            ...
        ]

        返回格式（对称模式）:
        [
            ["", "键1", "键2", "键3", ...],
            ["键1", 值1-1, 值1-2, 值1-3, ...],
            ["键2", 值2-1, 值2-2, 值2-3, ...],
            ...
        ]
        """
        try:
            if not isinstance(nested_dict, dict):
                raise ValueError("输入必须是字典")
            if not nested_dict:  # 空字典
                return []
        except ValueError as e:
            print(f"错误: {e}")
            return []  # 返回空数组表示转换失败

        if symmetric:
            # 对称模式：使用相同的键作为表头行和表头列
            keys = list(nested_dict.keys())
            if not keys:
                return []

            # 初始化结果数组，第一行为表头
            result_array = [[""] + keys]

            # 处理每个键对应的行
            for key in keys:
                row_data = [key]  # 行首为键名
                row_dict = nested_dict.get(key, {})

                # 按照表头顺序填充数据
                for col_key in keys:
                    value = row_dict.get(col_key, "")  # 默认值为空字符串
                    row_data.append(value)

                result_array.append(row_data)

            return result_array
        else:
            # 标准模式：使用外层键作为表头列，内层键作为表头行
            # 收集所有可能的表头（内层字典键）
            all_headers = set()
            for element_data in nested_dict.values():
                all_headers.update(element_data.keys())

            # 将表头排序并添加空字符串作为第一个元素（对应表头列的位置）
            sorted_headers = [""] + sorted(all_headers)

            # 初始化结果数组，第一行为表头
            result_array = [sorted_headers]

            # 处理每个元素
            for element_name, element_data in sorted(nested_dict.items()):
                row = [element_name]  # 初始化行，第一个元素为元素名称

                # 按照表头顺序填充数据
                for header in sorted_headers[1:]:  # 跳过第一个元素（空字符串）
                    value = element_data.get(header, "")  # 默认值为空字符串
                    row.append(value)

                result_array.append(row)

            return result_array

    @staticmethod
    def table_to_dict(chem_op_2D_array):
        """
        将包含表头的二维数组转换为嵌套字典结构。

        输入格式要求：
        - 第一行为表头
        - 第一列为各元素的名字
        - 其余单元格为数值或空值

        返回格式：
        {
            "元素名称1": {"表头1": 值1, "表头2": 值2, ...},
            "元素名称2": {"表头1": 值3, "表头2": 值4, ...},
            ...
        }
        """
        try:
            if not isinstance(chem_op_2D_array[0], list):
                raise ValueError("输入必须是二维数组")
        except ValueError as e:
            print(f"错误: {e}")
            return {}  # 返回空字典表示转换失败

        header = chem_op_2D_array[0]  # 获取表头行
        data_rows = chem_op_2D_array[1:]  # 获取数据行

        result_dict = {}

        for row in data_rows:
            if not isinstance(row, list) or len(row) == 0:
                continue  # 跳过空行或无效行

            element_name = row[0]  # 第一列为元素名称
            element_data = {}  # 存储当前元素的数据

            # 遍历表头和对应的数据列
            for col_idx in range(1, min(len(header), len(row))):
                cell_value = row[col_idx]
                if cell_value not in (None, ""):  # 跳过空值
                    try:
                        # 尝试将值转换为浮点数
                        element_data[header[col_idx]] = float(cell_value)
                    except (ValueError, TypeError):
                        # 非数字值保持原样
                        element_data[header[col_idx]] = cell_value

            result_dict[element_name] = element_data

        return result_dict

    def get_processor(self, table_type, instruction):
        processors = {
            "conc": {
                "update": self._process_conc_update,
            },
            "exp": {
                "update": self._process_exp_update,
                "exp_table": self._process_exp_table,
                "conc_table": self._process_conc_table,
                "substance_table": self._process_substance_table,
            },
            "substance": {
                "update": self._process_substance_update,
            }
        }
        return processors.get(table_type, {}).get(instruction)  # 直接返回函数或 None

        # 获取对应的处理方法


    # ===== Conc 表格处理方法 =====
    def _process_conc_update(self, name_of_exp, table_rootId, table_content, header_cell_content, the_request):
        print("_process_conc_update")
        name_of_exp = header_cell_content["Stocks of Experiment name"]
        self.update_stock(name_of_exp, table_rootId, table_content, header_cell_content, the_request)

        # 更新 exp 表格
        exp_table_content = self.Get_exp_table(name_of_exp, rootId=table_rootId)
        exp_header_config = {'headerContents': [name_of_exp], 'headerMutables': [True],
                             'headerLabels': ["Experiment name"]}
        exp_json_config = self.json_config_composer(table_rootId, "exp", exp_table_content, exp_header_config,
                                                    the_request)
        # 可以考虑返回 exp 表格的配置，或者同时返回 conc 和 exp 表格的配置
        return exp_json_config

    def _process_conc_table(self, name_of_exp, table_rootId, table_content, header_cell_content, the_request):
        """处理 conc 表格的特殊请求"""
        print("in _process_conc_table")
        name_of_exp = header_cell_content["Experiment name"]
        conc_header_config = {'headerContents': [name_of_exp],'headerMutables': [False],'headerLabels':["Stocks of Experiment name"]}
        conc_table_content = self.Get_conc_table(name_of_exp, rootId=table_rootId)
        conc_json_config = self.json_config_composer(table_rootId, "conc", conc_table_content, conc_header_config)
        return conc_json_config

    # ===== Exp 表格处理方法 =====
    def _process_exp_update(self, name_of_exp, table_rootId, table_content, header_cell_content, the_request):
        """处理 exp 表格的更新请求"""
        print("in _process_exp_update")
        name_of_exp = header_cell_content["Experiment name"]
        return self.update_exp(name_of_exp, table_rootId, table_content, header_cell_content, the_request)

    def _process_exp_table(self, name_of_exp, table_rootId, table_content, header_cell_content, the_request):
        """处理 exp 表格的特殊请求"""
        print("in _process_exp_table", header_cell_content)
        name_of_exp = header_cell_content["Experiment name"]
        conc_header_config = {'headerContents': [name_of_exp],'headerMutables': [True],'headerLabels':["Experiment name"]}
        conc_table_content = self.Get_exp_table(name_of_exp, rootId=table_rootId)
        conc_json_config = self.json_config_composer(table_rootId, "exp", conc_table_content, conc_header_config, the_request)
        return conc_json_config

    def _process_substance_update(self, name_of_exp, table_rootId, table_content, header_cell_content, the_request):
        """处理 substance 表格的更新请求"""
        name_of_exp = header_cell_content["Substances of Experiment name"]
        return self.update_substance(name_of_exp, table_rootId, table_content, header_cell_content, the_request)

    def _process_substance_table(self, name_of_exp, table_rootId, table_content, header_cell_content, the_request):
        """处理 substance 表格的特殊请求"""
        name_of_exp = header_cell_content["Experiment name"]
        conc_header_config = {'headerContents': [name_of_exp], 'headerMutables': [False],'headerLabels': ["Substances of Experiment name"]}
        conc_json_config = self.json_config_composer(table_rootId, "substance", table_content, conc_header_config,
                                                     the_request)
        return conc_json_config



    def _common_processing(self, name_of_exp, table_rootId, table_content, header_cell_content, table_type, instruction):
        print(f"Processing {instruction} for {table_type} table with exp name: {name_of_exp} and rootId: {table_rootId}")
        # 这里可以添加通用的处理逻辑
        return {"status": f"{instruction} {table_type} table success"}

    def json_config_composer(self, rootId, table_type, table_data, header_config=None, other_config=None):
        """
        生成表格配置JSON

        参数:
            table_type (str): 表格类型，可选值: 'exp', 'conc', 'substance'
            table_data (list): 表格数据，二维数组
            header_config (dict, optional): 表头配置，包含headerContents, headerMutables, headerLabels
            other_config (dict, optional): 其他配置，将合并到最终配置中

        返回:
            dict: 完整的表格配置JSON
        """

        # 根据table_type设置按钮配置
        if table_type == 'exp':
            buttons_config = {
                'addRow': False,
                'removeRow': False,
                'addColumn': False,
                'removeColumn': False,
                'addRowAndColumn': True,  # exp类型支持同时增删行列
                'submit': True,
                'cancel': True,
                'floatingWindow': False,
                'exp_table': False,
                'conc_table': True,
                'substance_table': True
            }
        else:  # conc和substance类型
            buttons_config = {
                'addRow': True,
                'removeRow': True,
                'addColumn': True,
                'removeColumn': True,
                'addRowAndColumn': False,  # conc和substance不支持同时增删行列
                'submit': True,
                'cancel': True,
                'floatingWindow': True,
                'exp_table': False,
                'conc_table': False,
                'substance_table': False
            }

        # 构建完整配置
        config = {
            'expName': "实验数据表格",  # 根据示例固定为这个名称
            'rootId': rootId,
            'config': {
                'buttons': buttons_config,
                'headerContents': header_config.get('headerContents', []) if header_config else [],
                'headerMutables': header_config.get('headerMutables', []) if header_config else [],
                'headerLabels': header_config.get('headerLabels', []) if header_config else [],
                'mutables' : None,
                'table_type': table_type,
                'tableArray': table_data
            }
        }

        # 合并其他配置
        if other_config:
            config['config'].update(other_config)

        return config

    @staticmethod
    def Chem_op_header_handler(chem_op_2D_array, row_id_table = None, row_changed = None):
        print("Chem_op_header_handler")
        ##输入针对特别列表：第一行为表头，第一列为各元素的名字，且内部都是数字（主要是在掌握输入值为空的时候）
        ##further arrays 是2D_array的每一行
        ##返回值：stacked_chem_op_2D_array 是字典组成的字典，字典键为最左列内容，值为字典（即表头值：本行输入值），代表输入的一列中和表头对应的内容
        ##返回值命名为：stacked_chem_op_2D_array
        try:
            if not isinstance(chem_op_2D_array, list):
                raise ValueError("need to pass 2D array")
            if len(chem_op_2D_array) == 0 or not isinstance(chem_op_2D_array[0], list):
                raise ValueError("need to pass 2D array")
        except ValueError as e:
            print(f"出现错误: {e}")
        header = chem_op_2D_array[0]
        del chem_op_2D_array[0]

        if row_id_table:
            del row_id_table[0]
        if row_changed is None:
            row_changed = [1]*len(row_id_table)
        stacked_chem_op_2D_array = {}
        for further_arrays in chem_op_2D_array:
            dict_in_return = {}
            index_here = int(1)
            while index_here < len(further_arrays):
                if further_arrays[index_here] != "" and further_arrays[index_here] is not None:
                    dict_in_return[header[index_here]] = float(further_arrays[index_here])
                index_here += 1
            stacked_chem_op_2D_array[further_arrays[0]] = dict_in_return
        print(f"stacked_chem_op_2D_array: {stacked_chem_op_2D_array}, row_id_table: {row_id_table}, row_changed: {row_changed}")

        return stacked_chem_op_2D_array, row_id_table, row_changed

    def _update_experiment_info(self, name_of_exp, rootId):
        if rootId not in self.id_exp_name:
            an_exp = Experiment(name=name_of_exp, table_id=rootId)
            self.dict_of_experiment[name_of_exp] = [rootId, an_exp]
            self.id_exp_name[rootId] = name_of_exp
        else:
            prior_name = self.id_exp_name[rootId]
            prior_id_address = self.dict_of_experiment[prior_name]
            del self.id_exp_name[rootId]
            del self.dict_of_experiment[prior_name]
            self.id_exp_name[rootId] = name_of_exp
            self.dict_of_experiment[name_of_exp] = prior_id_address
        return self.dict_of_experiment[name_of_exp][1]

    def update_exp(self, name_of_exp, rootId, list_of_fetch, header_cell_content, the_request):
        #加入其他composite而构成的trial
        print("success in getting into update_exp")
        the_exp = self._update_experiment_info(name_of_exp, rootId)
        print(f"update_exp: experiment in operation: {the_exp}\n")

        dict_of_create = chem_interface.table_to_dict(list_of_fetch)
        the_exp.new_exp_from_2d_array(dict_of_create, the_request.get("trial_ids"))
        the_exp.update_all_concentrations()
        return {'status':'create_new_trial_success'}


    def update_stock(self, name_of_exp, rootId, list_of_fetch, header_cell_content, the_request):
        print("success in getting into update_stock")

        the_exp = self._update_experiment_info(name_of_exp, rootId)

        dict_of_create = chem_interface.table_to_dict(list_of_fetch)

        the_exp.stock_from_2d_array(dict_of_create, the_request.get("trial_ids"))
        the_exp.update_all_concentrations()
        return {'status': 'stock_update_success'}



    def update_substance(self, name_of_exp, table_rootId, table_content, header_cell_content, the_request):
        """处理 substance 表格的更新请求"""
        print("success in getting into update_substance")
        the_exp = self._update_experiment_info(name_of_exp, table_rootId)

        dict_of_create = chem_interface.table_to_dict(table_content)
        the_exp.substance_from_2d_array(dict_of_create, the_request.get("trial_ids"))  # 假设 Experiment 类有 substance_from_2d_array 方法
        the_exp.update_all_concentrations()
        return {'status': 'substance_update_success'}

    def Get_substance_table(self, exp_name=None, rootId=None, table_header=None):
        print("success getting into Get_substance_table")
        # 解析目标实验
        target_exp=self.get_experiment(exp_name, rootId)

        print(f"Get_substance_table: 找到实验 {target_exp.name} (rootId: {target_exp.table_id})")

        # 构建嵌套字典（适用于 dict_to_table 的对称模式）
        substance_dict = {}
        for substance_name, substance_info in target_exp.substance_dict.items():  # 假设 Experiment 类有 substance_dict 属性
            substance_properties = substance_info.get_properties()  # 假设 substance_info 有 get_properties 方法
            substance_dict[substance_name] = substance_properties  # 外层键为 substance 名，内层键为特性名

        # 自动获取表头（若未指定则使用所有 substance 名）
        if not table_header:
            table_header = list(substance_dict.keys()) if substance_dict else []

        # 调用 dict_to_table 生成对称表格
        return self.dict_to_table(substance_dict, symmetric=True)

    def Get_conc_table(self, exp_name=None, rootId=None, table_header=None):
        print("success in getting into GET_conc")
        # 解析目标实验
        target_exp=self.get_experiment(exp_name, rootId)

        print(f"Get_conc: 找到实验 {target_exp.name} (rootId: {target_exp.table_id})")

        # 构建嵌套字典（适用于 dict_to_table 的对称模式）
        conc_dict = {}
        for trial_name, id_add_list in target_exp.sample_dict.items():
            the_trial = id_add_list[1]
            trial_conc = the_trial.substance_conc
            conc_dict[trial_name] = trial_conc  # 外层键为 trial 名，内层键为物质名

        # 自动获取表头（若未指定则使用所有物质名）
        if not table_header:
            table_header = list(conc_dict.keys()) if conc_dict else []

        # 调用 dict_to_table 生成对称表格
        return self.dict_to_table(conc_dict, symmetric=False)



    def Get_exp_table(self, exp_name=None, rootId=None, table_header=None):
        print("success getting into Get_exp_table")
        # 解析目标实验
        target_exp=self.get_experiment(exp_name, rootId)

        print(f"Get_exp_table: 找到实验 {target_exp.name} (rootId: {target_exp.table_id})")

        # 构建嵌套字典（适用于 dict_to_table 的对称模式）
        composite_dict = {}
        for trial_name, id_add_list in target_exp.sample_dict.items():
            the_trial = id_add_list[1]
            trial_composite = the_trial.composite
            composite_dict[trial_name] = trial_composite  # 外层键为 trial 名，内层键为组分名

        # 自动获取表头（若未指定则使用所有 trial 名）
        if not table_header:
            table_header = list(composite_dict.keys()) if composite_dict else []

        # 调用 dict_to_table 生成对称表格
        return self.dict_to_table(composite_dict, symmetric=True)

    def create_exp(self, exp_name, exp_id):
        # 假设实验地址暂时使用 None 代替，后续可根据实际情况修改
        exp_address = Experiment(exp_name,table_id=exp_id)
        # 添加新实验到 interface
        self.add_experiment(exp_name, exp_id, exp_address)
        # 获取实验表格数据
        exp_table_content = self.Get_exp_table(exp_name=exp_name, rootId=exp_id)
        # 表头配置
        header_config = {
            'headerContents': [exp_name],
            'headerMutables': [True],
            'headerLabels': ["Experiment name"]
        }
        # 生成表格配置 JSON
        return self.json_config_composer(exp_id, "exp", exp_table_content, header_config)



app = Flask(__name__, template_folder=os.getcwd())
this_interface = chem_interface()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

#发送前端数据时从这里补充
@app.route('/config_acceptor', methods = ['POST'])
def method_segregator():
        if request.method == 'POST':
            try:
                # 获取前端传递的数据
                the_request = request.get_json()
                name_of_exp = the_request.get('exp_name')
                table_rootId = the_request.get('rootId')
                config = the_request.get('config')
                table_type = config["table_type"]
                instruction = config["instruction"]
                table_content = the_request.get('table_content') #二维数组
                header_cell_content = the_request.get('header_cell_content') #字典，序号:内部数据
                # 尚未实现每个trial分别管理，赋予id，以及记忆每行修改的情况，分别修改的功能，即每次更新都是全表全更新，而没有
                # 生成trial_ids（改进逻辑，假设第一列是trial名称）
                trial_ids = []
                if table_content:
                    # 跳过表头行，假设第一行是表头
                    for row in table_content[1:]:
                        if row and row[0]:
                            trial_ids.append(f"{table_rootId}_trial_{len(trial_ids)}")
                        else:
                            trial_ids.append(f"{table_rootId}_trial_{len(trial_ids)}")
                the_request["trial_ids"] = trial_ids

                #print(f"{instruction}\n{name_of_exp}\n{table_rootId}\n{two_d_array}\n{row_id_table}")

                # 根据 instruction 调用相应的处理方法
                print("request: ",the_request)
                print(table_type, instruction)
                processor =this_interface.get_processor(str(table_type), str(instruction))
                print("table content and header contents",table_content, header_cell_content)
                result = processor(name_of_exp, table_rootId, table_content, header_cell_content, the_request)
                print(this_interface.id_exp_name)
                print(f"\nmethod_segregator_result: result:{result}")
                return jsonify(result)
            except Exception as e:
                print (f"method_segregator found: {str(e)}")
                return jsonify({"error": str(e)}), 500
        return render_template('index.html')


@app.route('/create_exp', methods=['POST'])
def create_exp_route():
    data = request.get_json()
    exp_name = data.get('exp_name')
    exp_id = data.get('exp_id')
    if exp_name and exp_id:
        config = this_interface.create_exp(exp_name, exp_id)
        return jsonify(config)
    return jsonify({"error": "缺少必要参数"}), 400

if __name__ == '__main__':
    app.run(debug=True)