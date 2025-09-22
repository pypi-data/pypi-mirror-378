# 设备控制API实现总结

## 新增功能

本次更新为 LiveGBS Python SDK 添加了完整的设备控制功能，包括云台控制、焦点光圈控制、预置位控制和看守位控制四大核心功能。

### 📋 功能详情

#### 1. 云台控制 API
- **接口**: `POST /api/v1/control/ptz`
- **方法**: `client.ptz_control()`
- **功能**: 控制摄像头云台的方向转动和变焦操作

#### 2. 焦点光圈控制 API
- **接口**: `POST /api/v1/control/fi`
- **方法**: `client.fi_control()`
- **功能**: 控制摄像头的焦点远近和光圈大小

#### 3. 预置位控制 API
- **接口**: `POST /api/v1/control/preset`
- **方法**: `client.preset_control()`
- **功能**: 管理摄像头预置位，包括设置、跳转和删除

#### 4. 看守位控制 API
- **接口**: `POST /api/v1/control/homeposition`
- **方法**: `client.home_position_control()`
- **功能**: 配置摄像头自动归位功能

## 🔧 技术实现

### 新增响应类

#### PTZControlResponse
云台控制响应数据类，特点：
- ✅ **统一处理**: 支持JSON和纯文本响应格式
- 📝 **状态反馈**: 返回操作成功状态和详细消息

#### FIControlResponse
焦点光圈控制响应数据类，特点：
- ✅ **格式兼容**: 处理各种响应格式
- 📝 **操作确认**: 提供清晰的操作结果反馈

#### PresetControlResponse
预置位控制响应数据类，特点：
- ✅ **操作验证**: 确认预置位操作是否成功
- 📝 **结果通知**: 返回详细的操作结果信息

#### HomePositionControlResponse
看守位控制响应数据类，特点：
- ✅ **配置确认**: 确认看守位配置是否生效
- 📝 **状态反馈**: 提供配置结果和状态信息

### 通用响应处理

#### _handle_control_response()
专用的设备控制响应处理方法：
- 🔄 **统一处理**: 所有设备控制API使用相同的响应处理逻辑
- 🛡️ **错误处理**: 统一的错误处理和异常管理
- 📊 **格式兼容**: 智能处理JSON和纯文本响应

## 🎮 API方法详解

### 1. 云台控制 (ptz_control)
```python
def ptz_control(
    serial: str,                      # 设备编号 (必须)
    command: str,                     # 控制指令 (必须)
    channel: Optional[int] = None,    # 通道序号，默认1
    code: Optional[str] = None,       # 通道编号（与channel二选一）
    speed: int = 129,                 # 速度(0~255)，默认129
) -> PTZControlResponse
```

**支持的控制指令**：
- `left` - 向左转
- `right` - 向右转  
- `up` - 向上转
- `down` - 向下转
- `upleft` - 左上转
- `upright` - 右上转
- `downleft` - 左下转
- `downright` - 右下转
- `zoomin` - 放大
- `zoomout` - 缩小
- `stop` - 停止

### 2. 焦点光圈控制 (fi_control)
```python
def fi_control(
    serial: str,                      # 设备编号 (必须)
    command: str,                     # 控制指令 (必须)
    channel: Optional[int] = None,    # 通道序号，默认1
    code: Optional[str] = None,       # 通道编号（与channel二选一）
    speed: int = 129,                 # 速度(0~255)，默认129
) -> FIControlResponse
```

**支持的控制指令**：
- `focusnear` - 焦点拉近
- `focusfar` - 焦点拉远
- `irisin` - 光圈收小
- `irisout` - 光圈放大
- `stop` - 停止

### 3. 预置位控制 (preset_control)
```python
def preset_control(
    serial: str,                      # 设备编号 (必须)
    command: str,                     # 控制指令 (必须)
    preset: int,                      # 预置位编号(1~255) (必须)
    channel: Optional[int] = None,    # 通道序号，默认1
    code: Optional[str] = None,       # 通道编号（与channel二选一）
    name: Optional[str] = None,       # 预置位名称（set时有效）
) -> PresetControlResponse
```

**支持的控制指令**：
- `set` - 设置预置位
- `goto` - 跳转到预置位
- `remove` - 删除预置位

### 4. 看守位控制 (home_position_control)
```python
def home_position_control(
    serial: str,                      # 设备编号 (必须)
    resettime: int,                   # 自动归位时间间隔(秒) (必须)
    presetindex: int,                 # 调用预置位编号 (必须)
    channel: Optional[int] = None,    # 通道序号，默认1
    code: Optional[str] = None,       # 通道编号（与channel二选一）
    enabled: bool = False,            # 使能开关，默认false
    timeout: int = 15,                # 超时时间(秒)，默认15
) -> HomePositionControlResponse
```

## 🛡️ 参数验证

### 指令验证
所有控制方法都包含严格的参数验证：
- **云台控制指令**: 验证指令是否在允许的11个指令范围内
- **焦点光圈指令**: 验证指令是否在允许的5个指令范围内
- **预置位指令**: 验证指令是否在允许的3个指令范围内
- **预置位编号**: 验证编号是否在1-255范围内

### 错误处理
- **ValueError**: 参数验证失败时抛出，包含详细的错误信息
- **LiveGBSError**: 网络或API错误时抛出
- **详细信息**: 所有错误都包含清晰的错误描述和解决建议

## 🧪 测试验证

### 测试文件
- `test_control.py` - 完整功能测试，包含所有控制场景
- `example_control.py` - 简单使用示例，演示实际应用

### 测试场景

#### 1. 云台控制测试
```python
# 方向控制
client.ptz_control(serial="xxx", code="xxx", command="left", speed=100)
client.ptz_control(serial="xxx", code="xxx", command="right", speed=100)
client.ptz_control(serial="xxx", code="xxx", command="up", speed=100)
client.ptz_control(serial="xxx", code="xxx", command="stop")

# 变焦控制
client.ptz_control(serial="xxx", code="xxx", command="zoomin", speed=150)
client.ptz_control(serial="xxx", code="xxx", command="zoomout", speed=150)
```

#### 2. 焦点光圈测试
```python
# 焦点控制
client.fi_control(serial="xxx", code="xxx", command="focusnear", speed=80)
client.fi_control(serial="xxx", code="xxx", command="focusfar", speed=80)

# 光圈控制
client.fi_control(serial="xxx", code="xxx", command="irisin", speed=80)
client.fi_control(serial="xxx", code="xxx", command="irisout", speed=80)
```

#### 3. 预置位管理测试
```python
# 设置预置位
client.preset_control(serial="xxx", code="xxx", command="set", preset=1, name="默认位置")

# 跳转预置位
client.preset_control(serial="xxx", code="xxx", command="goto", preset=1)

# 删除预置位
client.preset_control(serial="xxx", code="xxx", command="remove", preset=1)
```

#### 4. 看守位配置测试
```python
# 启用看守位
client.home_position_control(
    serial="xxx", code="xxx", 
    enabled=True, resettime=60, presetindex=1, timeout=20
)

# 禁用看守位
client.home_position_control(
    serial="xxx", code="xxx", 
    enabled=False, resettime=60, presetindex=1
)
```

### 测试结果
✅ **云台控制**: 所有11种控制指令测试通过  
✅ **焦点光圈**: 所有5种控制指令测试通过  
✅ **预置位管理**: 设置、跳转、删除操作测试通过  
✅ **看守位控制**: 启用、禁用配置测试通过  
✅ **参数验证**: 无效指令和参数正确被拦截  
✅ **错误处理**: 各种异常情况处理正常  

### 实际测试数据
- **服务器**: http://your-livegbs-server:port
- **设备**: 测试设备 (设备序列号)
- **云台类型**: 0 (未知类型，但API调用成功)
- **测试结果**: 所有控制操作均返回"OK"响应

## 🎯 应用场景

### 1. 自动巡检
```python
# 定义巡检路径
patrol_points = [
    (1, "入口监控点"),
    (2, "主要区域"),
    (3, "出口监控点")
]

# 执行巡检
for preset_num, location in patrol_points:
    print(f"巡检: {location}")
    client.preset_control(serial=device_id, code=channel_code, command="goto", preset=preset_num)
    time.sleep(10)  # 停留10秒
```

### 2. 手动控制
```python
# 操作员手动控制
def manual_control(direction, speed=100):
    client.ptz_control(
        serial=device_id,
        code=channel_code,
        command=direction,
        speed=speed
    )
    
# 使用示例
manual_control("left")     # 向左转
time.sleep(2)
manual_control("stop")     # 停止
```

### 3. 焦点自动调节
```python
# 自动对焦
def auto_focus():
    # 焦点拉近
    client.fi_control(serial=device_id, code=channel_code, command="focusnear", speed=100)
    time.sleep(1)
    
    # 焦点拉远
    client.fi_control(serial=device_id, code=channel_code, command="focusfar", speed=100)
    time.sleep(1)
    
    # 停止调节
    client.fi_control(serial=device_id, code=channel_code, command="stop")
```

### 4. 看守位自动化
```python
# 设置无人值守自动归位
def setup_auto_return():
    # 设置重要监控位置为预置位
    client.preset_control(
        serial=device_id, 
        code=channel_code, 
        command="set", 
        preset=1, 
        name="重要监控位置"
    )
    
    # 启用看守位，5分钟无操作后自动归位
    client.home_position_control(
        serial=device_id,
        code=channel_code,
        enabled=True,
        resettime=300,  # 5分钟
        presetindex=1
    )
```

## 📈 完整API覆盖

LiveGBS Python SDK现已实现的完整API列表：

### 🔐 认证管理
- ✅ 用户登录 (`login`)
- ✅ 退出登录 (`logout`) 
- ✅ 修改密码 (`modify_password`)

### 📱 设备管理
- ✅ 查询设备列表 (`get_device_list`)
- ✅ 查询单个设备信息 (`get_device_info`)
- ✅ 查询设备通道列表 (`get_device_channel_list`)
- ✅ 查询设备在线统计 (`get_device_online_stats`)

### 🎬 直播流控制
- ✅ 开始直播 (`start_stream`)
- ✅ 停止直播 (`stop_stream`)
- ✅ 视频水印 (`stream_osd`)

### 🎮 设备控制 **[新增]**
- ✅ 云台控制 (`ptz_control`) 
- ✅ 焦点光圈控制 (`fi_control`)
- ✅ 预置位控制 (`preset_control`)
- ✅ 看守位控制 (`home_position_control`)

## 🏗️ 代码结构

```
lsyiot_livegbs_sdk/
├── __init__.py              # 模块入口，导出所有公共API
├── api.py                  # 主API客户端，新增4个设备控制方法
├── responses.py            # 响应数据类，新增4个控制响应类
└── exceptions.py           # 自定义异常类
```

## 🎯 实现亮点

### 1. 完整参数验证
- **指令验证**: 所有控制指令都有严格的白名单验证
- **范围检查**: 预置位编号、速度等参数都有合理的范围限制
- **错误提示**: 详细的错误信息，帮助开发者快速定位问题

### 2. 统一响应处理
- **通用方法**: `_handle_control_response()` 统一处理所有控制API响应
- **格式兼容**: 智能处理JSON和纯文本响应格式
- **错误统一**: 一致的错误处理和异常抛出机制

### 3. 实际验证测试
- **真实设备**: 在实际的GB28181设备上测试验证
- **全面覆盖**: 测试了所有API和参数组合
- **边界测试**: 包含了各种边界条件和错误场景

### 4. 易用性设计
- **默认参数**: 合理的默认参数值，简化常用场景
- **灵活调用**: 支持通道序号和通道编号两种方式
- **清晰命名**: API方法和参数命名清晰易懂

## 💡 使用建议

1. **了解设备能力**: 在使用前先查询设备的云台类型，确认设备支持的控制功能
2. **适当延迟**: 控制指令之间添加适当的延迟，避免指令冲突
3. **及时停止**: 方向和变焦控制后要及时发送停止指令
4. **预置位管理**: 合理规划预置位编号，建议使用有意义的名称
5. **看守位配置**: 看守位时间不宜过短，避免频繁归位影响正常监控

## 🎉 总结

设备控制API的成功实现为LiveGBS Python SDK增加了强大的摄像头控制能力。现在开发者可以通过简单的API调用实现复杂的摄像头控制逻辑，包括实时云台控制、自动巡检、焦点调节、预置位管理和无人值守等功能。

SDK现在已经覆盖了从用户认证、设备管理、直播控制、视频增强到设备控制的完整业务流程，为开发基于GB28181标准的视频监控和流媒体应用提供了全面、专业、易用的开发工具。