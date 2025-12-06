"""
FileTool - 文件操作工具

提供文件和目录的读写、创建、删除等功能
"""

import os
import json
import shutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from .base_tool import BaseTool, ToolResult
except ImportError:
    from base_tool import BaseTool, ToolResult


class FileTool(BaseTool):
    """文件操作工具"""

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "file"

    @property
    def description(self) -> str:
        return "文件工具：创建文件、读写文件、保存内容、目录操作"

    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_file",
            "read_file",
            "write_file",
            "append_file",
            "delete_file",
            "create_directory",
            "delete_directory",
            "list_directory",
            "copy_file",
            "move_file",
            "file_exists",
            "get_file_info"
        ]

    @property
    def required_permissions(self) -> List[str]:
        return ["file_access"]

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """验证参数有效性"""
        if action in ["create_file", "read_file", "write_file", "append_file",
                     "delete_file", "file_exists", "get_file_info"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["filepath"],
                optional_params=[]
            )

        elif action in ["create_directory", "delete_directory", "list_directory"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["dirpath"],
                optional_params=[]
            )

        elif action in ["copy_file"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["source", "destination"],
                optional_params=[]
            )

        elif action in ["move_file"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["source", "destination"],
                optional_params=[]
            )

        elif action in ["write_file", "append_file"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["filepath", "content"],
                optional_params=["encoding", "mode"]
            )

        else:
            self.logger.error(f"不支持的动作: {action}")
            return False

    def execute_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """执行具体动作"""
        try:
            if action == "create_file":
                return self._create_file(parameters, context)
            elif action == "read_file":
                return self._read_file(parameters, context)
            elif action == "write_file":
                return self._write_file(parameters, context)
            elif action == "append_file":
                return self._append_file(parameters, context)
            elif action == "delete_file":
                return self._delete_file(parameters, context)
            elif action == "create_directory":
                return self._create_directory(parameters, context)
            elif action == "delete_directory":
                return self._delete_directory(parameters, context)
            elif action == "list_directory":
                return self._list_directory(parameters, context)
            elif action == "copy_file":
                return self._copy_file(parameters, context)
            elif action == "move_file":
                return self._move_file(parameters, context)
            elif action == "file_exists":
                return self._file_exists(parameters, context)
            elif action == "get_file_info":
                return self._get_file_info(parameters, context)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的文件动作: {action}"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"执行文件动作 {action} 失败: {str(e)}"
            )

    def _create_file(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """创建空文件"""
        filepath = parameters["filepath"]

        try:
            # 确保目录存在
            dir_path = os.path.dirname(filepath)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # 创建空文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("")

            return ToolResult(
                success=True,
                message=f"文件创建成功: {filepath}",
                data={"filepath": filepath}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"创建文件失败: {str(e)}"
            )

    def _read_file(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """读取文件内容"""
        filepath = parameters["filepath"]
        encoding = parameters.get("encoding", "utf-8")
        max_size = parameters.get("max_size", 1024 * 1024)  # 默认最大1MB

        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    message=f"文件不存在: {filepath}"
                )

            file_size = os.path.getsize(filepath)
            if file_size > max_size:
                return ToolResult(
                    success=False,
                    message=f"文件过大: {file_size} bytes (最大允许: {max_size} bytes)"
                )

            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()

            return ToolResult(
                success=True,
                message=f"文件读取成功: {filepath}",
                data={
                    "filepath": filepath,
                    "content": content,
                    "size": file_size,
                    "encoding": encoding
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"读取文件失败: {str(e)}"
            )

    def _write_file(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """写入文件内容"""
        filepath = parameters["filepath"]
        content = parameters["content"]
        encoding = parameters.get("encoding", "utf-8")
        backup = parameters.get("backup", False)

        try:
            # 如果启用备份，先备份原文件
            if backup and os.path.exists(filepath):
                backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(filepath, backup_path)

            # 确保目录存在
            dir_path = os.path.dirname(filepath)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # 写入文件
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)

            return ToolResult(
                success=True,
                message=f"文件写入成功: {filepath}",
                data={
                    "filepath": filepath,
                    "content_length": len(content),
                    "encoding": encoding,
                    "backup_created": backup and os.path.exists(filepath)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"写入文件失败: {str(e)}"
            )

    def _append_file(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """追加文件内容"""
        filepath = parameters["filepath"]
        content = parameters["content"]
        encoding = parameters.get("encoding", "utf-8")
        newline = parameters.get("newline", True)

        try:
            # 确保目录存在
            dir_path = os.path.dirname(filepath)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # 追加内容
            with open(filepath, 'a', encoding=encoding) as f:
                if newline and not content.endswith('\n'):
                    content += '\n'
                f.write(content)

            return ToolResult(
                success=True,
                message=f"内容追加成功: {filepath}",
                data={
                    "filepath": filepath,
                    "appended_content": content,
                    "content_length": len(content),
                    "encoding": encoding
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"追加内容失败: {str(e)}"
            )

    def _delete_file(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """删除文件"""
        filepath = parameters["filepath"]
        confirm = parameters.get("confirm", False)

        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    message=f"文件不存在: {filepath}"
                )

            if not confirm:
                return ToolResult(
                    success=False,
                    message="删除文件需要confirm参数设置为True"
                )

            os.remove(filepath)

            return ToolResult(
                success=True,
                message=f"文件删除成功: {filepath}",
                data={"filepath": filepath}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"删除文件失败: {str(e)}"
            )

    def _create_directory(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """创建目录"""
        dirpath = parameters["dirpath"]
        exist_ok = parameters.get("exist_ok", True)

        try:
            os.makedirs(dirpath, exist_ok=exist_ok)

            return ToolResult(
                success=True,
                message=f"目录创建成功: {dirpath}",
                data={"dirpath": dirpath}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"创建目录失败: {str(e)}"
            )

    def _delete_directory(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """删除目录"""
        dirpath = parameters["dirpath"]
        recursive = parameters.get("recursive", False)
        confirm = parameters.get("confirm", False)

        try:
            if not os.path.exists(dirpath):
                return ToolResult(
                    success=False,
                    message=f"目录不存在: {dirpath}"
                )

            if not confirm:
                return ToolResult(
                    success=False,
                    message="删除目录需要confirm参数设置为True"
                )

            if recursive:
                shutil.rmtree(dirpath)
            else:
                os.rmdir(dirpath)

            return ToolResult(
                success=True,
                message=f"目录删除成功: {dirpath}",
                data={"dirpath": dirpath, "recursive": recursive}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"删除目录失败: {str(e)}"
            )

    def _list_directory(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """列出目录内容"""
        dirpath = parameters["dirpath"]
        include_hidden = parameters.get("include_hidden", False)
        recursive = parameters.get("recursive", False)

        try:
            if not os.path.exists(dirpath):
                return ToolResult(
                    success=False,
                    message=f"目录不存在: {dirpath}"
                )

            if not os.path.isdir(dirpath):
                return ToolResult(
                    success=False,
                    message=f"路径不是目录: {dirpath}"
                )

            items = []
            if recursive:
                for root, dirs, files in os.walk(dirpath):
                    for name in dirs + files:
                        if not include_hidden and name.startswith('.'):
                            continue
                        full_path = os.path.join(root, name)
                        rel_path = os.path.relpath(full_path, dirpath)
                        items.append(self._get_item_info(full_path, rel_path))
            else:
                for item in os.listdir(dirpath):
                    if not include_hidden and item.startswith('.'):
                        continue
                    full_path = os.path.join(dirpath, item)
                    items.append(self._get_item_info(full_path, item))

            return ToolResult(
                success=True,
                message=f"目录内容获取成功: {dirpath}",
                data={
                    "dirpath": dirpath,
                    "items": items,
                    "count": len(items),
                    "recursive": recursive
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"列出目录内容失败: {str(e)}"
            )

    def _copy_file(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """复制文件"""
        source = parameters["source"]
        destination = parameters["destination"]
        overwrite = parameters.get("overwrite", False)

        try:
            if not os.path.exists(source):
                return ToolResult(
                    success=False,
                    message=f"源文件不存在: {source}"
                )

            if os.path.exists(destination) and not overwrite:
                return ToolResult(
                    success=False,
                    message=f"目标文件已存在: {destination} (设置overwrite=True覆盖)"
                )

            # 确保目标目录存在
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            shutil.copy2(source, destination)

            return ToolResult(
                success=True,
                message=f"文件复制成功: {source} -> {destination}",
                data={"source": source, "destination": destination}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"复制文件失败: {str(e)}"
            )

    def _move_file(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """移动文件"""
        source = parameters["source"]
        destination = parameters["destination"]
        overwrite = parameters.get("overwrite", False)

        try:
            if not os.path.exists(source):
                return ToolResult(
                    success=False,
                    message=f"源文件不存在: {source}"
                )

            if os.path.exists(destination) and not overwrite:
                return ToolResult(
                    success=False,
                    message=f"目标文件已存在: {destination} (设置overwrite=True覆盖)"
                )

            # 确保目标目录存在
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            shutil.move(source, destination)

            return ToolResult(
                success=True,
                message=f"文件移动成功: {source} -> {destination}",
                data={"source": source, "destination": destination}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"移动文件失败: {str(e)}"
            )

    def _file_exists(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """检查文件是否存在"""
        filepath = parameters["filepath"]

        try:
            exists = os.path.exists(filepath)
            is_file = os.path.isfile(filepath) if exists else False

            return ToolResult(
                success=True,
                message=f"文件存在性检查: {filepath}",
                data={
                    "filepath": filepath,
                    "exists": exists,
                    "is_file": is_file
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"检查文件存在性失败: {str(e)}"
            )

    def _get_file_info(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """获取文件信息"""
        filepath = parameters["filepath"]

        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    message=f"文件不存在: {filepath}"
                )

            stat = os.stat(filepath)
            info = {
                "filepath": filepath,
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": os.path.isfile(filepath),
                "is_directory": os.path.isdir(filepath),
                "absolute_path": os.path.abspath(filepath)
            }

            return ToolResult(
                success=True,
                message=f"文件信息获取成功: {filepath}",
                data=info
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"获取文件信息失败: {str(e)}"
            )

    def _get_item_info(self, full_path: str, name: str) -> Dict[str, Any]:
        """获取文件/目录项信息"""
        try:
            stat = os.stat(full_path)
            return {
                "name": name,
                "full_path": full_path,
                "type": "directory" if os.path.isdir(full_path) else "file",
                "size": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except:
            return {
                "name": name,
                "full_path": full_path,
                "type": "unknown",
                "size": 0,
                "modified_time": None
            }