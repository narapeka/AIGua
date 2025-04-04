"""File utilities for handling long paths and safe file operations."""
import os
import platform
import traceback
from typing import List, Optional, Dict, Any

# 添加长路径支持函数
def get_long_path(path):
    """
    将普通路径转换为支持长路径的格式
    在Windows上添加\\?\前缀，其他平台直接返回原路径
    """
    if platform.system() == 'Windows' and not path.startswith('\\\\?\\'):
        # 确保路径是绝对路径
        abs_path = os.path.abspath(path)
        # 添加长路径前缀
        return '\\\\?\\' + abs_path
    return path

# 添加重命名/移动文件的辅助函数
def safe_rename(src, dst):
    """
    安全地重命名/移动文件，支持长路径
    """
    long_src = get_long_path(src)
    long_dst = get_long_path(dst)
    
    print(f"尝试重命名文件 (使用长路径支持): \n  源: {long_src} \n  目标: {long_dst}")
    
    # 如果源文件和目标相同，直接返回成功
    if os.path.normpath(long_src) == os.path.normpath(long_dst):
        print("源文件和目标文件路径相同，无需重命名")
        return True
    
    # 确保源文件存在
    if not os.path.exists(long_src):
        print(f"源文件不存在: {src}")
        return False
    
    # 执行重命名操作
    try:
        os.rename(long_src, long_dst)
        print(f"文件重命名成功")
        return True
    except Exception as e:
        print(f"文件重命名失败: {str(e)}")
        print(f"错误类型: {type(e)}")
        print(f"错误堆栈: {traceback.format_exc()}")
        return False

# 安全创建目录的辅助函数
def safe_makedirs(path, exist_ok=True):
    """
    安全地创建目录，支持长路径
    """
    long_path = get_long_path(path)
    os.makedirs(long_path, exist_ok=exist_ok)
    return long_path

# 安全检查路径是否存在的辅助函数
def safe_path_exists(path):
    """
    安全地检查路径是否存在，支持长路径
    """
    long_path = get_long_path(path)
    return os.path.exists(long_path)

# 安全删除文件的辅助函数
def safe_remove_file(path, log_to=None, should_remove_empty_dir=True):
    """
    安全地删除文件，支持长路径
    
    Args:
        path: 要删除的文件路径
        log_to: 可选的记录日志的列表，用于保存操作结果
        should_remove_empty_dir: 是否在删除文件后检查并删除空目录
        
    Returns:
        bool: 删除操作是否成功
    """
    long_path = get_long_path(path)
    try:
        if os.path.exists(long_path) and os.path.isfile(long_path):
            file_size = os.path.getsize(long_path)
            parent_dir = os.path.dirname(long_path)
            os.remove(long_path)
            removal_log = f"文件已成功删除: {path} (大小: {file_size} 字节)"
            print(removal_log)
            
            # 如果提供了日志列表，记录操作
            if log_to is not None and isinstance(log_to, list):
                log_to.append({
                    "file": path,
                    "status": "success",
                    "message": removal_log,
                    "operation": "delete",
                    "file_size": file_size
                })
            
            # 检查目录是否为空，如果为空则删除目录
            if should_remove_empty_dir and parent_dir:
                safe_remove_empty_dir(parent_dir, log_to)
            
            return True
        else:
            not_found_log = f"文件不存在或不是文件: {path}"
            print(not_found_log)
            
            # 如果提供了日志列表，记录操作
            if log_to is not None and isinstance(log_to, list):
                log_to.append({
                    "file": path,
                    "status": "not_found",
                    "message": not_found_log,
                    "operation": "delete"
                })
            
            return False
    except Exception as e:
        error_log = f"删除文件失败: {path}, 错误: {str(e)}"
        print(error_log)
        print(f"错误类型: {type(e)}")
        print(f"错误堆栈: {traceback.format_exc()}")
        
        # 如果提供了日志列表，记录操作
        if log_to is not None and isinstance(log_to, list):
            log_to.append({
                "file": path,
                "status": "error",
                "message": error_log,
                "operation": "delete",
                "error": str(e)
            })
        
        return False

# 安全删除空目录的辅助函数
def safe_remove_empty_dir(path, log_to=None):
    """
    安全地删除空目录，支持长路径
    
    Args:
        path: 要删除的目录路径
        log_to: 可选的记录日志的列表，用于保存操作结果
        
    Returns:
        bool: 删除操作是否成功
    """
    long_path = get_long_path(path)
    try:
        if os.path.exists(long_path) and os.path.isdir(long_path):
            # 检查目录是否为空
            if not os.listdir(long_path):
                os.rmdir(long_path)
                removal_log = f"空目录已成功删除: {path}"
                print(removal_log)
                
                # 如果提供了日志列表，记录操作
                if log_to is not None and isinstance(log_to, list):
                    log_to.append({
                        "directory": path,
                        "status": "success",
                        "message": removal_log,
                        "operation": "delete_empty_dir"
                    })
                
                # 递归检查父目录是否为空
                parent_dir = os.path.dirname(long_path)
                if parent_dir:
                    safe_remove_empty_dir(parent_dir, log_to)
                
                return True
            else:
                not_empty_log = f"目录不为空，无法删除: {path}"
                print(not_empty_log)
                
                # 如果提供了日志列表，记录操作
                if log_to is not None and isinstance(log_to, list):
                    log_to.append({
                        "directory": path,
                        "status": "not_empty",
                        "message": not_empty_log,
                        "operation": "delete_empty_dir"
                    })
                
                return False
        else:
            not_found_log = f"目录不存在或不是目录: {path}"
            print(not_found_log)
            
            # 如果提供了日志列表，记录操作
            if log_to is not None and isinstance(log_to, list):
                log_to.append({
                    "directory": path,
                    "status": "not_found",
                    "message": not_found_log,
                    "operation": "delete_empty_dir"
                })
            
            return False
    except Exception as e:
        error_log = f"删除目录失败: {path}, 错误: {str(e)}"
        print(error_log)
        print(f"错误类型: {type(e)}")
        print(f"错误堆栈: {traceback.format_exc()}")
        
        # 如果提供了日志列表，记录操作
        if log_to is not None and isinstance(log_to, list):
            log_to.append({
                "directory": path,
                "status": "error",
                "message": error_log,
                "operation": "delete_empty_dir",
                "error": str(e)
            })
        
        return False

# 安全获取文件大小的辅助函数
def safe_get_file_size(path):
    """
    安全地获取文件大小，支持长路径
    
    Args:
        path: 文件路径
        
    Returns:
        int: 文件大小（字节），如果文件不存在则返回0
    """
    long_path = get_long_path(path)
    try:
        if os.path.exists(long_path) and os.path.isfile(long_path):
            return os.path.getsize(long_path)
        return 0
    except Exception as e:
        print(f"获取文件大小失败: {path}, 错误: {str(e)}")
        return 0 