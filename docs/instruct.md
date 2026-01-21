## 1
"Toggle Changed Edges"): "切换变动边",
修改为
Toggle Highlighted Edges : 切换高亮边显示

("*", "Toggle display of changed edges for this step"): "切换此步骤的变动边显示",
修改为
Toggle display of highlighted edges for this step"): "切换此步骤的高亮边显示",

## 2
From Active 似乎与系统的重叠了
recorder.py中的改为From Selected
translation.py中的对应更改
("*", "From Active"): "从活动步骤",
更改为 From Selected Step : 从选择的步骤开始

## 3
("*", "From Range"): "从范围",
修改为:
("*", "By Range"): "指定范围",

## 4

bl_label = "Reset Camera" 这部分翻译没有，加进去，中文为 重设摄像机位置

## 5

("*", "Reset the camera for this step to its recorded state"): "将此步骤的摄影机重置为其录制状态",
修改为
"Reset the camera transform for this step"): "重新设定当前步骤的摄像机位置",

## 6
("*", "Confirm and save the current camera for this step"): "确认并保存此步骤的当前摄影机",
修改为
"Confirm and save the current camera transform for this step"): "确认并保存此步骤的摄影机位置",

## 7

("*", "Play/record from active step"): "从活动步骤播放/录制",
修改为
Play/record from selected step : 从选择的步骤开始播放/录制
