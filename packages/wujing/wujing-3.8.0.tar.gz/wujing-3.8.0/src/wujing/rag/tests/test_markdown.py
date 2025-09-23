import pytest
import tempfile
import os
from wujing.rag.markdown import MarkdownProcessor, create_default_processor


class TestMarkdownProcessor:
    """MarkdownProcessor 类的测试用例"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.processor = MarkdownProcessor()
        self.sample_markdown = """
# 主标题

这是主要内容。

## 子标题

这是子标题下的内容。

### 三级标题

- 列表项1
- 列表项2

```python
def hello():
    print("Hello World!")
```

这是代码块后的内容。
"""

    def test_init_default_parameters(self):
        """测试默认参数初始化"""
        processor = MarkdownProcessor()
        assert processor.parser is not None

    def test_init_custom_parameters(self):
        """测试自定义参数初始化"""
        processor = MarkdownProcessor(include_metadata=False, include_prev_next_rel=False)
        assert processor.parser is not None

    def test_parse_markdown_text(self):
        """测试解析 Markdown 文本"""
        nodes = self.processor.parse_markdown_text(self.sample_markdown)
        
        assert isinstance(nodes, list)
        assert len(nodes) > 0
        
        # 检查节点内容
        for node in nodes:
            assert hasattr(node, 'get_content')
            assert hasattr(node, 'metadata')
            content = node.get_content()
            assert isinstance(content, str)
            assert len(content) > 0

    def test_parse_empty_markdown_text(self):
        """测试解析空 Markdown 文本"""
        nodes = self.processor.parse_markdown_text("")
        assert isinstance(nodes, list)

    def test_parse_markdown_file(self):
        """测试解析 Markdown 文件"""
        # 创建临时 Markdown 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.sample_markdown)
            temp_file_path = f.name

        try:
            nodes = self.processor.parse_markdown_file(temp_file_path)
            
            assert isinstance(nodes, list)
            assert len(nodes) > 0
            
            # 验证内容与直接解析文本的结果一致
            text_nodes = self.processor.parse_markdown_text(self.sample_markdown)
            assert len(nodes) == len(text_nodes)
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)

    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        with pytest.raises(FileNotFoundError):
            self.processor.parse_markdown_file("/nonexistent/path/file.md")

    def test_get_node_summaries(self):
        """测试获取节点摘要"""
        nodes = self.processor.parse_markdown_text(self.sample_markdown)
        summaries = self.processor.get_node_summaries(nodes)
        
        assert isinstance(summaries, list)
        assert len(summaries) == len(nodes)
        
        for i, summary in enumerate(summaries):
            assert isinstance(summary, dict)
            assert 'index' in summary
            assert 'content_preview' in summary
            assert 'content_length' in summary
            assert 'metadata' in summary
            assert summary['index'] == i + 1
            assert isinstance(summary['content_length'], int)
            assert summary['content_length'] >= 0

    def test_get_node_summaries_with_max_length(self):
        """测试带长度限制的节点摘要"""
        nodes = self.processor.parse_markdown_text(self.sample_markdown)
        max_length = 50
        summaries = self.processor.get_node_summaries(nodes, max_content_length=max_length)
        
        for summary in summaries:
            if summary['content_length'] > max_length:
                # 如果原内容长度超过限制，预览应该以"..."结尾
                assert summary['content_preview'].endswith("...")
                # 预览长度应该是 max_length + 3 (for "...")
                assert len(summary['content_preview']) == max_length + 3
            else:
                # 如果原内容长度不超过限制，预览应该等于原内容
                assert not summary['content_preview'].endswith("...")

    def test_print_node_summaries(self, capsys):
        """测试打印节点摘要"""
        nodes = self.processor.parse_markdown_text(self.sample_markdown)
        self.processor.print_node_summaries(nodes, max_content_length=50)
        
        captured = capsys.readouterr()
        assert "--- NODE" in captured.out
        assert "Text:" in captured.out
        assert "Content Length:" in captured.out
        assert "Metadata:" in captured.out


class TestCreateDefaultProcessor:
    """测试默认处理器创建函数"""

    def test_create_default_processor(self):
        """测试创建默认处理器"""
        processor = create_default_processor()
        
        assert isinstance(processor, MarkdownProcessor)
        assert processor.parser is not None


class TestMarkdownProcessorIntegration:
    """MarkdownProcessor 集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        markdown_content = """
# 测试文档

这是一个测试文档。

## 第一章

第一章的内容。

### 1.1 小节

小节内容。

## 第二章

第二章的内容。

```python
print("Hello World!")
```

结束。
"""
        
        # 创建处理器
        processor = create_default_processor()
        
        # 解析内容
        nodes = processor.parse_markdown_text(markdown_content)
        
        # 获取摘要
        summaries = processor.get_node_summaries(nodes)
        
        # 验证结果
        assert len(nodes) > 0
        assert len(summaries) == len(nodes)
        assert all(summary['content_length'] > 0 for summary in summaries)
        
        # 验证包含标题信息
        content_texts = [node.get_content() for node in nodes]
        full_content = "\n".join(content_texts)
        assert "测试文档" in full_content or any("测试文档" in text for text in content_texts)

    def test_chinese_content_handling(self):
        """测试中文内容处理"""
        chinese_markdown = """
# 中文标题

这是中文内容，包含一些特殊字符：你好世界！

## 子标题

- 第一项
- 第二项
- 第三项

### 代码示例

```python
# 中文注释
def 问候(名字):
    print(f"你好，{名字}！")
```

这是结束部分。
"""
        
        processor = create_default_processor()
        nodes = processor.parse_markdown_text(chinese_markdown)
        summaries = processor.get_node_summaries(nodes)
        
        assert len(nodes) > 0
        assert len(summaries) == len(nodes)
        
        # 验证中文内容正确处理
        for summary in summaries:
            assert summary['content_length'] > 0
            assert isinstance(summary['content_preview'], str)


if __name__ == "__main__":
    pytest.main([__file__])