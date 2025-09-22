import os
import shutil
import tempfile
from threading import Lock
from typing import Optional
from ..i18n import translate
from ..typing import *


__all__ = [
    "guarantee_file_exist",
    "assert_file_exist",
    "append_to_file",
    "get_temp_file_path",
    "delete_file",
    "copy_file",
    "clear_file",
    "get_files",
    "get_lines",
]


def guarantee_file_exist(
    file_path: str,
    is_directory: bool = False,
):
    
    """
    确保给定文件或目录存在，如果不存在则创建它。

    参数:
    file (str): 要检查或创建的文件或目录路径。
    is_directory (bool): 如果为 True，则创建目录而不是文件。
    """
    
    if is_directory:
        os.makedirs(file_path, exist_ok=True)
        
    else:
        
        parent = os.path.dirname(file_path)
        
        if parent:
            os.makedirs(parent, exist_ok=True)
            
        if not os.path.exists(file_path):
            
            with open(
                file = file_path, 
                mode = 'w', 
                encoding = 'UTF-8'
            ):
                pass
        
 
def assert_file_exist(
    file_path: str, 
    error_message = None,
):
    
    """
    断言给定文件存在
    """
    
    if not os.path.exists(file_path):
        
        if error_message is None:
            
            assert False, translate(
                "程序出错，文件 %s 不存在！" % (file_path) 
            )
            
        else:
            assert False, error_message
        

def append_to_file(
    file_path: str, 
    content: str,
    end: str = "\n",
    encoding: str = "UTF-8",
    immediate_flush: bool = True,
    buffering: Optional[int] = None,
):

    with open(
        file = file_path, 
        mode = "a", 
        encoding = encoding,
        buffering = -1 if buffering is None else buffering, 
    ) as file_pointer:
        
        file_pointer.write(content + end)
        if immediate_flush: file_pointer.flush()
        
        
tempfile_lock = Lock()

def get_temp_file_path(
    suffix: Optional[str] = "",
    prefix: str = "tmp_",
    directory: Optional[str] = None,
) -> str:
    
    """
    在线程安全的环境中生成一个临时文件路径或临时目录。

    本函数会：
      - 如果 suffix 为 None，则创建一个临时目录并返回其路径；
      - 否则，在线程锁保护下生成一个唯一的临时文件路径（不创建文件）。

    Args:
        suffix (str or None): 文件后缀名；若为 None，则表示创建临时目录。
        prefix (str): 文件或目录前缀，默认 "tmp_"。
        directory (str): 保存路径，默认使用临时目录。

    Returns:
        str: 生成的临时文件路径或临时目录路径。
    """

    global tempfile_lock
    
    with tempfile_lock:
        
        if suffix is None:
            
            tmp_dir_path = tempfile.mkdtemp(
                prefix = prefix,
                dir = directory,
            )
            
            return tmp_dir_path
        
        else:
            
            temp_file_path = tempfile.mktemp(
                suffix = suffix,
                prefix = prefix,
                dir = directory,
            )
            
            return temp_file_path
        
        
def delete_file(
    file_path: str
) -> None:
    
    """
    Recursively delete the specified file or directory.

    Under thread lock protection:
      - If it's a file, delete it directly;
      - If it's a directory, recursively delete all its contents and itself;
      - If the path doesn't exist, silently ignore.

    Args:
        file_path (str): Path of the file or directory to be deleted.
    """
    
    global tempfile_lock
    
    with tempfile_lock:
        
        try:
            
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                
            elif os.path.isfile(file_path):
                os.remove(file_path)
                
        except FileNotFoundError:
            pass
        
        except Exception as error:
            print(
                translate("删除失败: %s, 错误: %s") % (file_path, error)
            )
            
            
def copy_file(
    source_file_path: str,
    destination_file_path: str,
) -> None:
    
    """
    Copy file or folder from source_file_path to destination_file_path.

    Automatically determines:
      - If source_file_path is a file, copies it as destination_file_path;
      - If source_file_path is a directory:
          - If destination_file_path doesn't exist, recursively copies the entire directory;
          - If destination_file_path exists, copies directory contents inside destination_file_path.
      - Automatically creates parent directories of destination_file_path (if they don't exist)

    Args:
        source_file_path (str): Source path, can be file or directory.
        destination_file_path (str): Destination path.
    """
    
    if not os.path.exists(source_file_path):
        
        raise FileNotFoundError(
            translate("源路径不存在: %s") % (source_file_path)
        )
    
    # Create parent directories of destination_file_path (whether file or directory target)
    os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)

    if os.path.isfile(source_file_path):
        shutil.copy2(source_file_path, destination_file_path)
        
    elif os.path.isdir(source_file_path):
        
        if not os.path.exists(destination_file_path):
            shutil.copytree(source_file_path, destination_file_path)
            
        else:
            
            for item in os.listdir(source_file_path):
                
                s_item = os.path.join(source_file_path, item)
                d_item = os.path.join(destination_file_path, item)
                
                if os.path.isdir(s_item):
                    shutil.copytree(s_item, d_item, dirs_exist_ok=True)
                    
                else:
                    shutil.copy2(s_item, d_item)
                    
    else:
        
        raise ValueError(
            translate("不支持的源路径类型: %s") % (source_file_path)
        )
        
        
def clear_file(
    file_path: str,
    encoding: str = "UTF-16",
):
    
    """
    清空指定文件的全部内容。
    
    若文件不存在，则调用 guarantee_file_exist 创建空白文件。

    参数:
        file_path (str): 目标文件的路径。
        encoding (str): 编码方式，默认为 UTF-16。
    """
    
    try:
        
        with open(
            file = file_path, 
            mode = "w", 
            encoding = encoding,
        ):
            pass
        
    except FileNotFoundError:
        guarantee_file_exist(file_path)
        
        
def get_files(
    directory: str,
    file_type: Literal["all", "files_only", "dirs_only"] = "all",
    start_with: str = "",
    end_with: str = "",
    behaviour: Literal["return_basenames", "return_full_paths"] = "return_basenames",
)-> List[str]:
    
    """
    获取指定目录下文件的basename列表
    
    Args:
        directory: 目录路径
        file_type: 文件类型筛选选项
            - "all": 返回所有文件和目录
            - "dirs_only": 只返回目录
            - "files_only": 只返回文件（非目录）
    
    Returns:
        文件basename的列表
    """
    
    if not os.path.exists(directory):
        
        raise ValueError(
            translate("目录 %s 不存在")
            % (directory)
        )
    
    if not os.path.isdir(directory):
        
        raise ValueError(
            translate("路径 %s 不是目录")
            % (directory)
        )
    
    result = []
    
    for item in os.listdir(directory):
        
        item_path = os.path.join(directory, item)
        
        if not (item.startswith(start_with) and item.endswith(end_with)):
            continue
        
        if file_type == "all":
            result.append(item)
            
        elif file_type == "dirs_only" and os.path.isdir(item_path):
            result.append(item)
            
        elif file_type == "files_only" and os.path.isfile(item_path):
            result.append(item)
            
    if behaviour == "return_basenames":
        return result
    
    elif behaviour == "return_full_paths":
        return [f"{directory}/{basename}" for basename in result]
    
    else:
        
        raise NotImplementedError


def get_lines(
    file_path: str,
    strip: bool = True,
    encoding: str = "UTF-8",
)-> List[str]:
    
    with open(
        file = file_path,
        mode = "r",
        encoding = encoding,
    ) as file_pointer:
        
        lines = file_pointer.readlines()
        
    if strip:
        lines = [line.strip() for line in lines]
        
    return lines