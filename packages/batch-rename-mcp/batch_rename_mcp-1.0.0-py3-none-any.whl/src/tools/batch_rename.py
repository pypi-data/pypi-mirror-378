"""
批量重命名MCP工具

提供批量重命名文件的功能
"""

from typing import Dict, Any
import logging

from ..core.renamer import Renamer
from ..core.operation_log import OperationLog
from ..core.pattern_parser import PatternParser

logger = logging.getLogger(__name__)


class BatchRenameHandler:
    """批量重命名处理器"""
    
    def __init__(self, config: Dict[str, Any], operation_log: OperationLog):
        self.config = config
        self.operation_log = operation_log
        self.renamer = Renamer(config, operation_log)
    
    async def handle(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理批量重命名请求
        
        Args:
            arguments: MCP工具参数
            
        Returns:
            操作结果
        """
        try:
            # 提取参数
            target = arguments.get("target")
            pattern = arguments.get("pattern")
            options = arguments.get("options", {})
            
            # 验证必需参数
            if not target:
                return {
                    "success": False,
                    "message": "缺少必需参数: target",
                    "error_type": "ValidationError"
                }
            
            if not pattern:
                return {
                    "success": False,
                    "message": "缺少必需参数: pattern",
                    "error_type": "ValidationError"
                }
            
            logger.info(f"开始批量重命名: target={target}, pattern={pattern}")
            
            # 添加pattern到options中，供日志使用
            options["pattern"] = pattern
            
            # 执行批量重命名
            result = self.renamer.batch_rename(target, pattern, options)
            
            # 如果是预览模式，添加额外信息
            if options.get("dry_run", False):
                result["help"] = self._get_pattern_help()
                result["examples"] = PatternParser.get_pattern_examples()
            
            logger.info(f"批量重命名完成: success={result.get('success')}")
            
            return result
            
        except Exception as e:
            logger.error(f"批量重命名处理失败: {e}")
            return {
                "success": False,
                "message": f"处理失败: {str(e)}",
                "error_type": type(e).__name__
            }
    
    def _get_pattern_help(self) -> Dict[str, Any]:
        """获取模式帮助信息"""
        return {
            "description": "重命名模式语法说明",
            "template_variables": PatternParser.get_available_variables(),
            "special_patterns": {
                "regex:pattern:replacement": "正则表达式替换",
                "upper:{name}": "转换为大写",
                "lower:{name}": "转换为小写",
                "title:{name}": "转换为标题格式"
            },
            "conflict_resolution": {
                "auto_number": "自动添加序号避免冲突（默认）",
                "skip": "跳过冲突的文件",
                "overwrite": "覆盖已存在的文件"
            }
        }
