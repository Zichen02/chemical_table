class EditableCell {
    constructor(initialContent = null, extraInfo = {}, id=null, mutable = true) {
        // 创建一个td元素作为单元格
        this.cellElement = document.createElement('td');
        // 设置初始内容
        this.cellElement.textContent = initialContent;
        // 保存初始内容到data属性中，方便后续恢复
        this.cellElement.dataset.initialContent = initialContent;
        this.cellElement.dataset.PreviousContent = null;
        // 创建一个字典用于存储其他信息，初始化为空对象
        this.extraInfo = extraInfo || {};
        // 添加事件监听器
        if(id){this.cellElement.id = id;}
        else(this.cellElement.id = EditableCell.gen_random_id());
        this.cellElement.user_changed = false;
        // 存储事件处理函数的引用，用于后续移除
        this.eventHandlers = {
            click: null,
            blur: null,
        };
        
        // 初始化this.mutable和this.hasEventListeners
        this.mutable = mutable;
        this.hasEventListeners = false;
        
        // 根据mutable状态决定是否添加事件监听器
        if (this.mutable) {
            this.addEventListeners();
        }
    }

    static gen_random_id(ini = null){
        return 'cell-' + Math.random().toString(36).substring(2, 9);
    }

    addEventListeners() {
        // 使用箭头函数保存引用，确保可以正确移除
        this.eventHandlers.click = () => {
            if (this.mutable) {
                this.cellElement.setAttribute('contenteditable', 'true');
                this.cellElement.focus();
                this.cellElement.dataset.PreviousContent = this.cellElement.textContent;
            }
        };
        
        this.eventHandlers.blur = () => {
            if (this.mutable) {
                this.cellElement.removeAttribute('contenteditable');
                const extractedContent = this.cellElement.textContent;
                this.cellElement.dataset.PreviousContent = extractedContent;
                this.triggerContentChanged();
                if(this.cellElement.textContent.toString() == this.cellElement.dataset.PreviousContent.toString()){
                    this.cellElement.user_changed = true;
                }
            }
        };
        
        // 添加事件监听器
        this.cellElement.addEventListener('click', this.eventHandlers.click);
        this.cellElement.addEventListener('blur', this.eventHandlers.blur);
        
        // 标记已添加监听器
        this.hasEventListeners = true;
    }

    setmutable(stat) {
        this.mutable = stat;
        
        if (stat) {
            // 如果设置为可编辑但还没有添加事件监听器，则添加
            if (!this.hasEventListeners) {
                this.addEventListeners();
            }
        } else {
            // 如果设置为不可编辑，移除contenteditable属性和事件监听器
            this.cellElement.removeAttribute('contenteditable');
            
            if (this.hasEventListeners) {
                this.cellElement.removeEventListener('click', this.eventHandlers.click);
                this.cellElement.removeEventListener('blur', this.eventHandlers.blur);
                
                // 重置事件处理函数引用
                this.eventHandlers = {
                    click: null,
                    blur: null,
                    keydown: null
                };
                
                this.hasEventListeners = false;
            }
        }
    }

    // 用于设置额外信息的方法，接收键和值作为参数
    setExtraInfo(key, value) {
        this.extraInfo[key] = value;
    }

    setcellcontent(new_content){
        this.cellElement.dataset.PreviousContent = this.cellElement.textContent;
        this.cellElement.textContent = new_content;
        if(this.cellElement.textContent.toString() == this.cellElement.dataset.PreviousContent.toString()){
            this.cellElement.user_changed = true;
            }
    }

    // 用于获取额外信息的方法，根据键获取对应的值，如果键不存在则返回 undefined
    getExtraInfo(key) {
        return this.extraInfo[key];
    }

    // 获取单元格元素的方法，方便外部使用时添加到表格等结构中
    getElement() {
        return this.cellElement;
    }

    getCurrentContent() {
        return this.cellElement.textContent;
    }
    
    // 触发内容变更的方法，需要在父类中实现
    triggerContentChanged() {
        // 这个方法可以在子类中实现，用于通知外部内容已变更
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////

//横向坐标在前，纵向坐标在后，0开始
class EditableTable {
    //wtable 对wunit_element的扩写：
    //extrainfo{"wtable_id":[html中第几个表格，横坐标，纵坐标]}
    //单元格信息通过cells.路由访问
    //列的信息
    //row_change_recorder 会被设为1，后端判断为1则需要修改，判断为0则不需要。本类中没有对这个值进行重置为0要用的话需要外面发送时重置
    constructor(rows, cols, rootid = null) {
        this.rows = rows;
        this.cols = cols;
        this.table = document.createElement('table');
        this.cells = [];
        this.cells_id = [];
        this.createTable(rootid);
        if(rootid){this.table.id = rootid}
        else{this.table.id = EditableTable.gen_random_id();}
        this.addPasteListener();
    }

    static gen_random_id(){
        return 'table-' + Math.random().toString(36).substring(2, 9);
    }

    static findContentCoordinates(arr, content) {
        const rowIndex = arr.findIndex(row => row.includes(content));
        if (rowIndex!== -1) {
            const colIndex = arr[rowIndex].findIndex(item => item === content);
            return [rowIndex, colIndex];
        }
        return null;
    }

    createTable(table_cell_ids) {
        for (let i = 0; i < this.rows; i++) {
            const row = document.createElement('tr');
            row.id = `${table_cell_ids}_row_${i}`;
            row.dataset.row_num = i

            this.cells.push([]);
            this.cells_id.push([]);
            for (let j = 0; j < this.cols; j++) {
                const editableCell = new EditableCell(null,{row_index: i,col_index: j},`${table_cell_ids}_${String(i)}_${String(j)}_EditableCell`);
                const cell = editableCell.getElement();
                this.cells[i].push(editableCell);
                this.cells_id[i].push(editableCell.cellElement.id);
                row.appendChild(cell);
            }
            this.table.appendChild(row);
        }
    }

    // 获取表格元素，方便外部添加到页面等结构中
    getTableElement() {
        return this.table;
    }

    // 添加一行
    addRow(initialContent_row = null, extrainfo_row = null, idini_row=null) {
        let initialContent_List = Array.isArray(initialContent_row)? initialContent_row : new Array(this.cols).fill(initialContent_row);
        let extrainfo_List = Array.isArray(extrainfo_row)? extrainfo_row : new Array(this.cols).fill(extrainfo_row);
        let idini_List = Array.isArray(idini_row)? idini_row : new Array(this.cols).fill(idini_row);
        const row = document.createElement('tr');
        row.id = `${idini_List[0]}_row_${this.rows}`
        
        this.cells.push([]);
        this.cells_id.push([]);
        for (let j = 0; j < this.cols; j++) {
            const editableCell = new EditableCell(initialContent_List[j],{
                ...extrainfo_List[j], // 保留原有信息
                row_index: this.rows, // 行索引为当前行数（从0开始）
                col_index: j // 列索引为当前循环变量
            },
            `${idini_List[j]}_${String(this.rows)}_${String(j)}_EditableCell`,);
            const cell = editableCell.getElement();

            this.cells[this.cells.length - 1].push(editableCell);
            this.cells_id[this.cells.length - 1].push(editableCell.cellElement.id);
            row.appendChild(cell);
        }
        this.table.appendChild(row);
        this.rows++;
    }

    // 删除一行（最后一行）
    removeRow() {
        if (this.rows > 0) {
            this.table.removeChild(this.table.lastChild);
            this.cells.pop();
            this.cells_id.pop();
            this.rows--;
        }
    }

    // 添加一列
    addColumn(initialContent_row = null, extrainfo_row = null, idini_row = null) {
        let initialContent_List = Array.isArray(initialContent_row)? initialContent_row : new Array(this.cols).fill(initialContent_row);
        let extrainfo_List = Array.isArray(extrainfo_row)? extrainfo_row : new Array(this.cols).fill(extrainfo_row);
        let idini_List = Array.isArray(idini_row)? idini_row : new Array(this.cols).fill(idini_row);
        for (let i = 0; i < this.rows; i++) {
            const editableCell = new EditableCell(initialContent_List[i], {
                ...extrainfo_List[i], // 保留原有信息
                row_index: i, // 行索引为当前行数（从0开始）
                col_index: this.cols} // 列索引为当前循环变量
            , `${idini_List[i]}_${String(i)}_${String(this.cols)}_EditableCell`,);
            const cell = editableCell.getElement();
            this.cells[i].push(editableCell);
            this.cells_id[i].push(editableCell.cellElement.id);
            this.table.rows[i].appendChild(cell);
        }
        this.cols++;
    }

    // 删除一列（最后一列）
    removeColumn(){
        if (this.cols > 0) {
            for (let i = 0; i < this.rows; i++) {
                this.table.rows[i].removeChild(this.table.rows[i].lastChild);
                this.cells[i].pop();
                this.cells_id[i].pop();
            }
            this.cols--;
        }
    }

    //编辑指定单元格（这里简单实现一个示例，比如传入行和列索引来修改单元格内容，可根据实际需求完善）
    editCell(rowIndex, colIndex, newContent) {
        if (rowIndex >= 0 && rowIndex < this.rows && colIndex >= 0 && colIndex < this.cols) {
            const currentCell = this.cells[rowIndex][colIndex];
            currentCell.setcellcontent(newContent);
            // 这里可根据需求添加更多对额外信息的更新逻辑
        }
    }

    // 提取所有EditableCell中的内容并形成二维数组
    extractContents() {
        const contents = [];
        for (let i = 0; i < this.rows; i++) {
            const rowContents = [];
            for (let j = 0; j < this.cols; j++) {
                const currentCell = this.cells[i][j];
                rowContents.push(currentCell.getCurrentContent());
            }
            contents.push(rowContents);
        }
        return contents;
    }

    extractids(){
        const contents = [];
        for (let i = 0; i < this.rows; i++) {
            const rowContents = [];
            for (let j = 0; j < this.cols; j++) {
                rowContents.push(this.cells_id[i][j]);
            }
            contents.push(rowContents);
        }
        return contents;
    }


/**
const jsonData = {
    table_content: [
        ['数据1', '数据2', '数据3'],
        ['数据4', '数据5', '数据6'],
        ['数据7', '数据8', '数据9']
    ],
    mutable: [
        [true, false, true],
        [false, true, false],
        [true, false, true]
    ],
    important: [
        [true, false, false],
        [false, true, false],
        [false, false, true]
    ]
}; 
*/

    static from2DArray(array2D, table = null, starting_index = [0, 0]) {
        if (!array2D || array2D.length === 0) return table; // 空数据直接返回
        
        const rows = array2D.length;
        const cols = array2D[0].length;
        const [startRow, startCol] = starting_index;
        
        // 初始化表格：若不存在则创建新实例（使用 rootId 或默认配置）
        if (!table) {
            // 建议传入 rootId，若未传则生成随机 ID
            const rootId = EditableTable.gen_random_id();
            table = new EditableTable(0, 0, rootId); // 初始 0 行 0 列，动态扩展
        }
        
        // 扩展表格至足够容纳数据的尺寸
        while (table.rows < startRow + rows) table.addRow(); // 自动添加行
        while (table.cols < startCol + cols) table.addColumn(); // 自动添加列
        
        // 填充数据（使用 editCell 确保触发可能的更新逻辑）
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const targetRow = startRow + i;
                const targetCol = startCol + j;
                if (targetRow < table.rows && targetCol < table.cols) {
                    table.editCell(targetRow, targetCol, array2D[i][j]);
                } else {
                    console.warn(`警告：坐标 [${targetRow}, ${targetCol}] 超出表格范围，数据未填充`);
                }
            }
        }
        
        return table;
    }

    static fromJSON(jsonData, starting_index = [0, 0], table = null) {
        const {table_content, mutable, ...properties} = jsonData;
        if (!table_content || table_content.length === 0) return table;

        const rows = table_content.length;
        const cols = table_content[0].length;
        const [startRow, startCol] = starting_index;
        let mutableArray = mutable;
        if (!mutableArray) {
            // 生成全true的二维数组
            mutableArray = Array(rows).fill().map(() => Array(cols).fill(true));
        }

        // 初始化表格：若不存在则创建新实例（使用 rootId 或默认配置）
        if (!table) {
            const rootId = EditableTable.gen_random_id();
            table = new EditableTable(0, 0, rootId); // 初始 0 行 0 列，动态扩展
        }

        // 扩展表格至足够容纳数据的尺寸
        while (table.rows < startRow + rows) table.addRow(); // 自动添加行
        while (table.cols < startCol + cols) table.addColumn(); // 自动添加列

        // 填充数据
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const targetRow = startRow + i;
                const targetCol = startCol + j;
                if (targetRow < table.rows && targetCol < table.cols) {
                    table.editCell(targetRow, targetCol, table_content[i][j]);
                } else {
                    console.warn(`警告：坐标 [${targetRow}, ${targetCol}] 超出表格范围，数据未填充`);
                }
            }
        }

        // 设置 mutable 特性
        table.modifyCellsByBooleanArray(mutableArray, 'mutable');

        // 设置其他属性
        for (const [propertyName, propertyArray] of Object.entries(properties)) {
            if (Array.isArray(propertyArray) && propertyArray.length > rows && propertyArray[0].length > cols) {
                table.modifyCellsByBooleanArray(propertyArray, propertyName);
            }
        }

        return table;
    }

    // 新方法：根据布尔值二维阵列和词条改变单元格特性
    modifyCellsByBooleanArray(booleanArray, property) {
        if (booleanArray.length!== this.rows || booleanArray.some(row => row.length!== this.cols)) {
            console.error('布尔值二维阵列的大小与表格大小不匹配');
            return;
        }

        for (let i = 0; i < this.rows; i++) {
            for (let j = 0; j < this.cols; j++) {
                const cell = this.cells[i][j];
                const value = booleanArray[i][j];

                if (property === 'mutable') {
                    cell.setmutable(value);
                }
                else if (property === 'user_changed') {
                    cell.cellElement.user_changed = value;
                } else {
                    cell.cellElement.setAttribute(property, value);
                }
            }
        }
    }

    insertPastedData(rows, startRow = 0, startCol = 0) {
        // 直接调用 from2DArray 处理粘贴数据
        EditableTable.from2DArray(
            rows, // 粘贴的二维数据
            this, // 当前表格实例
            [startRow, startCol] // 起始坐标
        );
    }

    addPasteListener() {
        const self = this;
        this.table.addEventListener('paste', function (e) {
            e.preventDefault();
            const target = document.activeElement;
            if (target.tagName === 'TD') {
                const pasteData = (e.clipboardData || window.clipboardData).getData('text/plain');
                // 将粘贴内容转换为二维数组（行×列）
                const rows = pasteData
                   .replace(/\r/g, '')
                   .split('\n')
                   .map(row => row.split('\t')); // 按制表符分割列
                
                // 获取焦点单元格的行列索引
                const startRow = target.parentNode.rowIndex; // 行索引
                const startCol = target.cellIndex; // 列索引
                
                self.insertPastedData(rows, startRow, startCol); // 调用重构后的方法
            } else {
                console.error('请先聚焦到单元格再粘贴');
            }
        });
    }


    // 移动表格内容的方法
    moveTableContent(startRow, startCol, rowShift, colShift) {
        // 扩展表格以容纳移动后的内容
        while (this.rows < this.rows + Math.max(0, startRow + rowShift)) {
            this.addRow();
        }
        while (this.cols < this.cols + Math.max(0, startCol + colShift)) {
            this.addColumn();
        }

        // 创建一个临时数组来存储移动前的内容
        const tempContents = this.extractContents();

        // 根据移动方向决定遍历顺序
        const rowStart = rowShift >= 0 ? tempContents.length - 1 : startRow;
        const rowEnd = rowShift >= 0 ? startRow - 1 : tempContents.length;
        const rowStep = rowShift >= 0 ? -1 : 1;
        
        const colStart = colShift >= 0 ? tempContents[0].length - 1 : startCol;
        const colEnd = colShift >= 0 ? startCol - 1 : tempContents[0].length;
        const colStep = colShift >= 0 ? -1 : 1;

        // 移动内容
        for (let i = rowStart; i !== rowEnd; i += rowStep) {
            for (let j = colStart; j !== colEnd; j += colStep) {
                if (i >= startRow && j >= startCol) {
                    const newRow = i + rowShift;
                    const newCol = j + colShift;
                    if (newRow >= 0 && newRow < this.rows && newCol >= 0 && newCol < this.cols) {
                        this.editCell(newRow, newCol, tempContents[i][j]);
                    }
                }
            }
        }

        // 清空原位置的内容
        for (let i = startRow; i < tempContents.length; i++) {
            for (let j = startCol; j < tempContents[i].length; j++) {
                this.editCell(i, j, '');
            }
        }
    }
}
////////////////////////////////////////////////////////////////////////////////////////////////

/*
received data: 
{
expName: "实验数据表格",
rootId: "backend_table_1",
config: {
buttons:{
addRow: true,
removeRow: true,
addColumn: false,
removeColumn: false,
addRowAndColumn: false,
submit: true,
cancel: true,
floatingWindow: true,
exp_table: false,
conc_table: true,
substance_table: true,
}
headerContents: ['实验ID', '温度', '压力', '湿度'],
headerMutables: [false, true, true, true],
headerLabels: ['ID: ', '温度: ', '压力: ', '湿度: '],
table_type: 'conc',
tableArray: [
['EXP001', '25.5', '101.3', '60'],
['EXP002', '26.0', '101.2', '58'],
['EXP003', '24.8', '101.5', '62']
]
}
}

名字、表格实例、表头单元格用rootId保存于experiments中
this.experiments[rootId] = {expName, table, headers};
this.tableContainers[rootId] = tableContainer;

返回数据：
{
  "table_type": "conc",
  "exp_name": "常规表格 1",
  "rootId": "normal_table_1",
  "config": {table_type: "(received)config.table_type["conc","exp","substance"]", instruction: "update"["exp_table","conc_table","substance_table"]},
  "front_table_content": [
    [
      "数据1",
      "数据2",
      "数据3"
    ],
    [
      "数据4",
      "数据5",
      "数据6"
    ],
    [
      "数据7",
      "数据8",
      "数据9"
    ]
  ],
  "header_cells": {
    "编号: ": "实验编号",
    "负责人: ": "负责人",
    "日期: ": "日期"
  }
}

*/

class Chem_Operator {
    // 存储实验rootId和对应的所有tableid
    experiments = {};

    // 存储表格特性配置
    tableFeatures = {};

    // 存储表格主容器（包含所有相关元素）
    tableContainers = {};

    //存储id字符串：{表格实例，headers字典}以取消和提交时使用，用来绑定对应的experiments{}
    table_map = {};

    created_table = 0;

    constructor() {
        // 初始化操作
    }

    add_table_count(){
        this.created_table++;
        return `table#${this.created_table}`
    }

    // 根据后端的 JSON 数据构建表格，先检索已有表格，有则更新，无则创建
    buildTableFromConfig(expName, rootId, config, targetDivId) {
        const targetDiv = document.getElementById(targetDivId);
        if (!targetDiv) {
            throw new Error(`Target div with id '${targetDivId}' not found.`);
        }

        // 检查是否已有该rootId对应的表格
        if (this.experiments[rootId]) {
            // 获取该实验下所有表格ID
            const tableIds = this.experiments[rootId];
            
            // 查找与当前配置匹配的表格（假设配置中可能有表格类型等标识）
            const matchingTableId = tableIds.find(tableId => {
                const tableConfig = this.tableFeatures[tableId];
                // 这里需要根据实际情况判断表格是否匹配
                // 例如，检查配置中的table_type或其他唯一标识
                return tableConfig && tableConfig.table_type === config.table_type;
            });
            
            if (matchingTableId) {
                // 找到匹配的表格，更新它。额，这里改表格原则上需要全更新，但是咱懒了，直接不加按钮了
                const exp = this.table_map[matchingTableId];
                if (exp) {
                    const table = exp.table;
                    const headers = exp.headers;
                    
                    // 更新表格特性配置
                    this.tableFeatures[matchingTableId] = config;

                    // 更新表头
                    const { headerContents = [], headerMutables = [], headerLabels = [] } = config;
                    for (let i = 0; i < headerContents.length; i++) {
                        const content = headerContents[i];
                        const mutable = headerMutables[i] || false;
                        const label = headerLabels[i] || '';
                        const headerCell = headers[label];
                        if (headerCell) {
                            headerCell.setcellcontent(content);
                            headerCell.setmutable(mutable);
                        }
                    }

                    // 更新表格内容
                    if (config.tableArray && Array.isArray(config.tableArray)) {
                        EditableTable.from2DArray(config.tableArray, table);
                    }  

                    return table;
                }
            }
        }

        // 如果没有找到对应的表格，则创建新表格
        const this_table_id = this.add_table_count();
        
        // 更新实验到表格的映射
        if (!this.experiments[rootId]) {
            this.experiments[rootId] = [this_table_id];
        } else {
            this.experiments[rootId].push(this_table_id);
        }
        console.log(this.experiments);

        // 存储表格特性配置
        this.tableFeatures[this_table_id] = config;

        // 创建表格主容器
        const tableContainer = document.createElement('div');
        tableContainer.id = `${this_table_id}_container`;
        tableContainer.className = 'chem-table-container';

        // 创建表头区域
        const headerContainer = document.createElement('div');
        headerContainer.className = 'table-header-container';
        const headers = {};

        const { headerContents = [], headerMutables = [], headerLabels = [] } = config;
        console.log(`headerconfig: ${headerContents}, ${headerMutables}, ${headerLabels}`);
        
        for (let i = 0; i < headerContents.length; i++) {
            const content = headerContents[i];
            const mutable = headerMutables[i] || false;
            const label = headerLabels[i] || '';

            // 创建标签元素
            const labelElement = document.createElement('span');
            labelElement.textContent = label;
            headerContainer.appendChild(labelElement);

            // 创建表头单元格
            const headerCell = new EditableCell(content, null, `${this_table_id}_header_${i}`, mutable);
            headers[label] = headerCell;
            headerContainer.appendChild(headerCell.getElement());
        }

        // 创建表格内容区域
        const contentContainer = document.createElement('div');
        contentContainer.className = 'table-content-container';
        contentContainer.id = `${this_table_id}_content`;

        // 创建按钮区域
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'table-button-container';

        // 创建并添加按钮
        const buttonMap = this.createTableButtons(this_table_id, config, buttonContainer);

        // 创建表格实例
        const table = new EditableTable(0, 0, `${this_table_id}_table`);

        // 根据表格数组生成表格内容
        if (config.tableArray && Array.isArray(config.tableArray)) {
            EditableTable.from2DArray(config.tableArray, table);
        }

        contentContainer.appendChild(table.getTableElement());

        // 组装所有元素到主容器
        tableContainer.appendChild(headerContainer);
        tableContainer.appendChild(contentContainer);
        tableContainer.appendChild(buttonContainer);
        
        console.log("config:", config);
        
        // 将主容器添加到目标DOM
        if (config.buttons.floatingWindow) {
            // 创建悬浮窗
            const floatingWindow = this.createFloatingWindow(this_table_id, tableContainer);
            targetDiv.appendChild(floatingWindow);
        } else {
            targetDiv.appendChild(tableContainer);
        }

        // 保存表格引用
        this.table_map[this_table_id] = { expName, table, headers };
        this.tableContainers[this_table_id] = tableContainer;

        const sending_config = { table_type: config.table_type };

        // 添加事件监听器
        this.addEventListeners(rootId, buttonMap, sending_config, targetDivId, this_table_id);

        return table;
    }

    // 创建表格按钮
    createTableButtons(rootId, config, container) {
        const buttonMap = {};
        const buttonDefinitions = [
            { id: 'addRow', text: '添加一行', enabled: config.buttons.addRow },
            { id: 'removeRow', text: '删除一行', enabled: config.buttons.removeRow },
            { id: 'addColumn', text: '添加一列', enabled: config.buttons.addColumn },
            { id: 'removeColumn', text: '删除一列', enabled: config.buttons.removeColumn },
            { id: 'addRowAndColumn', text: '添加行列', enabled: config.buttons.addRowAndColumn },
            { id: 'removeRowAndColumn', text: '删除行列', enabled: config.buttons.removeRowAndColumn },
            { id: 'submit', text: '提交', enabled: config.buttons.submit },
            { id: 'cancel', text: '取消', enabled: config.buttons.cancel },
            { id: 'exp_table', text: '生成实验表格', enabled: config.buttons.exp_table },
            { id: 'conc_table', text: '浓度表格', enabled: config.buttons.conc_table },
            { id: 'substance_table', text: '物质表格', enabled: config.buttons.substance_table },
        ];

        buttonDefinitions.forEach(({ id, text, enabled }) => {
            if (enabled) {
                const button = document.createElement('button');
                button.id = `${rootId}_${id}`;
                button.textContent = text;
                button.className = 'table-action-button';
                container.appendChild(button);
                buttonMap[id] = button;
            }
        });

        return buttonMap;
    }

    // 创建悬浮窗
    createFloatingWindow(this_table_id, content) {
        const floatingWindow = document.createElement('div');
        floatingWindow.id = `${this_table_id}_floating_window`;
        floatingWindow.className = 'floating-window';

        const handle = document.createElement('div');
        handle.id = `${this_table_id}_handle`;
        handle.className = 'floating-handle';
        handle.textContent = '拖动';

        // 添加拖动功能
        let isDragging = false;
        let offsetX, offsetY;

        handle.addEventListener('mousedown', (e) => {
            isDragging = true;
            offsetX = e.clientX - floatingWindow.getBoundingClientRect().left;
            offsetY = e.clientY - floatingWindow.getBoundingClientRect().top;
            floatingWindow.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                floatingWindow.style.left = `${e.clientX - offsetX}px`;
                floatingWindow.style.top = `${e.clientY - offsetY}px`;
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            floatingWindow.style.cursor = 'grab';
        });

        floatingWindow.appendChild(handle);
        floatingWindow.appendChild(content);

        return floatingWindow;
    }

    // 添加事件监听器
    addEventListeners(rootId, buttonMap, sending_config, targetDivId, this_table_id) {
        const table = this.table_map[this_table_id]["table"];
        // 添加行
        if (buttonMap.addRow) {
            buttonMap.addRow.addEventListener('click', () => {
                table.addRow();
            });
        }

        // 删除行
        if (buttonMap.removeRow) {
            buttonMap.removeRow.addEventListener('click', () => {
                table.removeRow();
            });
        }

        // 添加列
        if (buttonMap.addColumn) {
            buttonMap.addColumn.addEventListener('click', () => {
                table.addColumn();
            });
        }

        // 删除列
        if (buttonMap.removeColumn) {
            buttonMap.removeColumn.addEventListener('click', () => {
                table.removeColumn();
            });
        }

        // 添加行列
        if (buttonMap.addRowAndColumn) {
            buttonMap.addRowAndColumn.addEventListener('click', () => {
                table.addRow();
                table.addColumn();
            });
        }

        if (buttonMap.removeRowAndColumn) {
            buttonMap.removeRowAndColumn.addEventListener('click', () => {
                table.removeRow();
                table.removeColumn();
            });
        }

        // 提交
        if (buttonMap.submit) {
            buttonMap.submit.addEventListener('click', () => {
                const { expName } = this.table_map[this_table_id];
                this.sendTableDataToFlask(expName, rootId, { ... sending_config, instruction : "update"}, targetDivId, this_table_id);
            });
        }

        if (buttonMap.exp_table) {
            buttonMap.exp_table.addEventListener('click', () => {
                const { expName } = this.table_map[this_table_id];
                this.sendTableDataToFlask(expName, rootId, { ... sending_config, instruction : "exp_table"}, targetDivId, this_table_id);
            });
        }        
        if (buttonMap.conc_table) {
            buttonMap.conc_table.addEventListener('click', () => {
                const { expName } = this.table_map[this_table_id];
                this.sendTableDataToFlask(expName, rootId, { ... sending_config, instruction : "conc_table"}, targetDivId, this_table_id);
            });
        }
        if (buttonMap.substance_table) {
            buttonMap.substance_table.addEventListener('click', () => {
                const { expName } = this.table_map[this_table_id];
                this.sendTableDataToFlask(expName, rootId, { ... sending_config, instruction : "substance_table"}, targetDivId, this_table_id);
            });
        }        
        // 取消
        if (buttonMap.cancel) {
            buttonMap.cancel.addEventListener('click', () => {
                // 获取主容器
                const container = this.tableContainers[this_table_id];
                if (container && container.parentNode) {
                    container.parentNode.removeChild(container);
                }

                // 如果是悬浮窗，也移除
                const floatingWindow = document.getElementById(`${this_table_id}_floating_window`);
                if (floatingWindow && floatingWindow.parentNode) {
                    floatingWindow.parentNode.removeChild(floatingWindow);
                }

                // 清理内存引用
                delete this.table_map[this_table_id];
                delete this.tableFeatures[this_table_id];
                delete this.tableContainers[this_table_id];
            });
        }
    }

    // 向 Flask 后端发送表格数据
    async sendTableDataToFlask(expName, rootId, sending_config, targetDivId, this_table_id) {
        const exp = this.table_map[this_table_id];
        if (exp) {
            const table = exp.table;
            const headers = exp.headers;
            const tableData = table.extractContents();
            const tableid = table.extractids();

            // 提取前置单元格数据
            const headerCells = {};
            for (const [label, header] of Object.entries(headers)) {
                const content = header.getCurrentContent();
                headerCells[label] = content;
            }

            console.log(headerCells);

            try {
                const response = await fetch(`/config_acceptor`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        exp_name: expName,
                        rootId: rootId,
                        config : sending_config,
                        table_content: tableData,
                        header_cell_content: headerCells
                    })
                });

                // 检查 HTTP 状态码
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                // 解析响应为 JSON
                const json_response = await response.json();
                console.log(json_response); // 打印解析后的 JSON 数据
                return this.handle_response(json_response, targetDivId); // 传递解析后的 JSON 数据
                
            } catch (error) {
                console.error('向 Flask 后端发送数据时出错：', error);
                return { status: 'error', message: error.message };
            }
        }
    }

    handle_response(json_response, targetDivId) {
        // 检查是否有错误信息
        if (json_response.error) {
            console.error('服务器返回错误:', json_response.error);
            return { status: 'error', message: json_response.error };
        }
        
        // 检查响应状态
        if (json_response.status) {
            console.log('表格更新成功:', json_response.message || '');
            // 可以在这里添加更新成功后的其他操作，如提示用户等
            return { status: 'success', message: json_response.message };
        } 
        
        else if (json_response.expName && json_response.rootId && json_response.config) {
            // 处理表格配置响应
            const { expName, rootId, config } = json_response;
            try {
                // 根据配置构建并渲染表格
                this.buildTableFromConfig(expName, rootId, config, targetDivId);
                console.log('表格渲染成功:', rootId);
                return { status: 'success', message: '表格渲染成功' };
            } catch (error) {
                console.error('表格渲染失败:', error);
                return { status: 'error', message: '表格渲染失败' };
            }
        } 
        
        else {
            console.error('未知响应格式:', json_response);
            return { status: 'error', message: '未知响应格式' };
        }
    }


// 在 Chem_Operator 类中添加 createNewExperiment 方法
    async createNewExperiment(targetDivId) {
        const expName = prompt('请输入实验名称');
        if (expName) {
            const expId = `exp_${Date.now()}`; // 生成唯一的实验 ID
            try {
                const response = await fetch('/create_exp', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        exp_name: expName,
                        exp_id: expId,

                    })
                });
                const json_response = await response.json();
                this.handle_response(json_response, targetDivId); // 假设目标 div 的 ID 为 target-div-id
            } catch (error) {
                console.error('创建实验时出错：', error);
            }
        }
    }
}