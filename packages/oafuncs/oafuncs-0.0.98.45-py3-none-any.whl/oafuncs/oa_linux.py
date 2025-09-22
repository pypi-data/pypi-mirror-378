from rich import print


__all__ = ["os_command", "get_queue_node"]


# 负责执行命令并返回输出
def os_command(cmd):
    import subprocess
    print(f'🔍 执行命令: {cmd}')
    result = subprocess.run(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    # 打印错误信息（若有，方便排查问题）
    if result.stderr:
        print(f'❌ 错误输出: {result.stderr.strip()}')
    # 检查命令是否执行成功（非0为失败）
    if result.returncode != 0:
        print(f'❌ 命令执行失败，退出码: {result.returncode}')
        return None
    return result.stdout

# 返回“队列名:节点数”的字典
def get_queue_node():
    import re
    # 执行 sinfo | grep "idle" 获取空闲队列数据
    cmd = 'sinfo | grep "idle"'
    output = os_command(cmd)
    if not output:  # 命令执行失败或无输出，返回空字典
        return {}
    
    # 初始化结果字典：键=队列名，值=节点数
    queue_node_dict = {}
    # 按行解析命令输出
    for line in output.strip().split('\n'):
        line = line.strip()
        if not line:  # 跳过空行
            continue
        
        # 正则匹配：仅捕获“队列名”（第1组）和“节点数”（第2组）
        # 末尾用 .* 忽略节点列表，不影响匹配
        pattern = r"^(\S+)\s+\S+\s+\S+\s+(\d+)\s+idle\s+.*$"
        match = re.match(pattern, line)
        
        if match:
            queue_name = match.group(1)    # 提取队列名作为字典的键
            node_count = int(match.group(2))# 提取节点数作为字典的值（转为整数）
            queue_node_dict[queue_name] = node_count  # 存入字典
    
    return queue_node_dict

if __name__ == "__main__":
    pass
