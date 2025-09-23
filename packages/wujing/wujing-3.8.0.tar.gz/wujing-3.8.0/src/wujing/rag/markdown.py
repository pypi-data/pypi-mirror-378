from typing import List, Optional
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core import Document
from llama_index.core.schema import BaseNode


class MarkdownProcessor:
    """Markdown 文档处理器，用于将 Markdown 文本解析为节点"""
    
    def __init__(
        self,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
        chunk_size: Optional[int] = None,
        chunk_overlap: int = 200
    ):
        """
        初始化 Markdown 处理器
        
        Args:
            include_metadata: 是否包含元数据
            include_prev_next_rel: 是否包含前后节点关系
            chunk_size: 最大块大小（字符数）。如果指定，将使用 SentenceSplitter 进行二次分割
            chunk_overlap: 块重叠大小，默认为 200
        """
        self.include_metadata = include_metadata
        self.include_prev_next_rel = include_prev_next_rel
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 使用 MarkdownNodeParser 作为主解析器
        self.parser = MarkdownNodeParser(
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel
        )
        
        # 如果指定了 chunk_size，创建二级分割器
        self.secondary_parser = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel
        ) if chunk_size is not None else None
    
    def parse_markdown_text(self, markdown_text: str) -> List[BaseNode]:
        """
        解析 Markdown 文本为节点列表
        
        Args:
            markdown_text: Markdown 文本内容
            
        Returns:
            解析后的节点列表
        """
        documents = [Document(text=markdown_text)]
        
        # 先用 MarkdownNodeParser 分割
        markdown_nodes = self.parser.get_nodes_from_documents(documents)
        
        # 如果没有二级分割器，直接返回结果
        if self.secondary_parser is None:
            return markdown_nodes
        
        # 使用二级分割器对超过大小限制的节点进行细分
        final_nodes = []
        for md_node in markdown_nodes:
            # 如果节点内容超过 chunk_size，使用二级分割器
            if len(md_node.get_content()) > self.chunk_size:
                sub_documents = [Document(text=md_node.get_content())]
                sub_nodes = self.secondary_parser.get_nodes_from_documents(sub_documents)
                
                # 保留原始节点的元数据
                for sub_node in sub_nodes:
                    if hasattr(md_node, 'metadata') and md_node.metadata:
                        if not hasattr(sub_node, 'metadata') or sub_node.metadata is None:
                            sub_node.metadata = {}
                        sub_node.metadata.update(md_node.metadata)
                
                final_nodes.extend(sub_nodes)
            else:
                final_nodes.append(md_node)
        
        return final_nodes
    
    def parse_markdown_file(self, file_path: str, encoding: str = "utf-8") -> List[BaseNode]:
        """
        解析 Markdown 文件为节点列表
        
        Args:
            file_path: Markdown 文件路径
            encoding: 文件编码，默认为 utf-8
            
        Returns:
            解析后的节点列表
        """
        with open(file_path, 'r', encoding=encoding) as f:
            markdown_text = f.read()
        return self.parse_markdown_text(markdown_text)
    
    def get_node_summaries(self, nodes: List[BaseNode], max_content_length: int = 100) -> List[dict]:
        """
        获取节点摘要信息
        
        Args:
            nodes: 节点列表
            max_content_length: 内容最大显示长度
            
        Returns:
            包含节点摘要信息的字典列表
        """
        summaries = []
        for i, node in enumerate(nodes):
            content = node.get_content()
            summary = {
                "index": i + 1,
                "content_preview": content[:max_content_length] + "..." if len(content) > max_content_length else content,
                "content_length": len(content),
                "metadata": node.metadata
            }
            summaries.append(summary)
        return summaries
    
    def print_node_summaries(self, nodes: List[BaseNode], max_content_length: int = 100):
        """
        打印节点摘要信息
        
        Args:
            nodes: 节点列表
            max_content_length: 内容最大显示长度
        """
        summaries = self.get_node_summaries(nodes, max_content_length)
        for summary in summaries:
            print(f"--- NODE {summary['index']} ---")
            print(f"Text: {summary['content_preview']}")
            print(f"Content Length: {summary['content_length']}")
            print(f"Metadata: {summary['metadata']}")
            print()


def create_default_processor() -> MarkdownProcessor:
    """创建默认配置的 Markdown 处理器"""
    return MarkdownProcessor(include_metadata=True, include_prev_next_rel=True)


def create_chunked_processor(chunk_size: int = 1024, chunk_overlap: int = 200) -> MarkdownProcessor:
    """
    创建支持分块大小控制的 Markdown 处理器
    
    Args:
        chunk_size: 最大块大小（字符数）
        chunk_overlap: 块重叠大小
    
    Returns:
        配置好的 MarkdownProcessor 实例，先按 Markdown 结构分割，再按大小分割
    """
    return MarkdownProcessor(
        include_metadata=True,
        include_prev_next_rel=True,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )


# 示例使用
if __name__ == "__main__":
    # 示例 Markdown 文本
    sample_markdown = """
# Python 编程入门

Python 是一种高级编程语言，以其简洁明了的语法而闻名。本章介绍基础知识，让读者能够快速上手 Python 编程。Python 的设计哲学强调代码的可读性和简洁性，这使得它成为初学者和专业开发者的首选语言之一。

## 变量和数据类型

在 Python 中，你不需要明确声明变量的类型。Python 会根据赋给变量的值自动推断变量的类型。这种特性被称为动态类型，它让编程变得更加灵活和简单。

- **整数 (int)**: `x = 10` - 用于表示整数值
- **浮点数 (float)**: `y = 3.14` - 用于表示小数值
- **字符串 (str)**: `name = "Alice"` - 用于表示文本数据
- **布尔值 (bool)**: `is_active = True` - 用于表示真假值

```python
# 这是一个代码块示例，展示了如何定义和使用函数
def greet(name):
    \"\"\"这个函数用于问候指定的人\"\"\"
    print(f"Hello, {name}! 欢迎学习 Python 编程！")

# 调用函数
greet("World")
greet("张三")
````

这是 `变量和数据类型` 部分的总结。Python 的数据类型系统非常丰富，除了基本类型外，还有列表、字典、元组等复合数据类型。

# 控制流

使用 `if`, `elif`, `else` 来进行条件判断。这是第二章的内容，涵盖了程序流程控制的基本概念。条件语句让程序能够根据不同的情况执行不同的代码路径，这是编程中非常重要的概念。

## 循环语句

Python 提供了 for 循环和 while 循环两种循环结构。for 循环通常用于遍历序列（如列表、字符串等），while 循环则用于在满足特定条件时重复执行代码块。掌握循环语句对于编写高效的程序至关重要。
"""

    print("=== 示例 1: 默认处理器（按 Markdown 结构分割）===")
    processor1 = create_default_processor()
    nodes1 = processor1.parse_markdown_text(sample_markdown)
    print(f"生成了 {len(nodes1)} 个节点")
    processor1.print_node_summaries(nodes1, max_content_length=80)

    print("\n" + "="*60)
    print("=== 示例 2: 分块处理器（Markdown 结构 + 大小限制）===")
    processor2 = create_chunked_processor(chunk_size=200, chunk_overlap=50)
    nodes2 = processor2.parse_markdown_text(sample_markdown)
    print(f"生成了 {len(nodes2)} 个节点")
    processor2.print_node_summaries(nodes2, max_content_length=80)
