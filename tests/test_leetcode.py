from pathlib import Path
from cltd.datasets.leetcode import iter_leetcode_records


def test_iter_leetcode_records(tmp_path: Path):
    # 1. 构造测试目录结构
    md_file = tmp_path / "0001-1000.md"
    cpp_dir = tmp_path / "C++"
    py_dir = tmp_path / "Python"
    
    cpp_dir.mkdir(parents=True, exist_ok=True)
    py_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. 写入模拟的代码文件
    cpp_file = cpp_dir / "two-sum.cpp"
    cpp_file.write_text("int main() { return 0; }", encoding="utf-8")
    
    py_file = py_dir / "two-sum.py"
    py_file.write_text("def main(): pass", encoding="utf-8")
    
    # 3. 写入 Markdown 表格数据
    md_content = """# Solutions
|  #  | Title           |  Solution       |  Time           | Space           | Difficulty    | Tag          | Note| 
|-----|---------------- | --------------- | --------------- | --------------- | ------------- |--------------|-----|
| 0001 | [Two Sum](https://leetcode.com/problems/two-sum/) | [C++](./C++/two-sum.cpp) [Python](./Python/two-sum.py) | _O(n)_ | _O(n)_ | Easy |||
0002 | [Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) | [C++](./C++/add-two-numbers.cpp) | _O(n)_ | _O(1)_ | Medium |||
"""
    md_file.write_text(md_content, encoding="utf-8")
    
    # 4. 运行解析器
    language_map = {"C++": "cpp", "Python": "python"}
    records = iter_leetcode_records(tmp_path, language_map)
    
    # 5. 断言验证
    # add-two-numbers.cpp 虽在表格中，但文件在 C++/ 下不存在，解析器应跳过它。
    # 故只应解析出 two-sum.cpp 和 two-sum.py
    assert len(records) == 2
    
    # 核对内容
    python_records = [r for r in records if r.language == "python"]
    cpp_records = [r for r in records if r.language == "cpp"]
    
    assert len(python_records) == 1
    assert len(cpp_records) == 1
    
    py_rec = python_records[0]
    cpp_rec = cpp_records[0]
    
    assert py_rec.task_id == "0001"
    assert py_rec.task_name == "Two Sum"
    assert py_rec.task_category == "Easy"
    assert py_rec.code_raw == "def main(): pass"
    assert py_rec.equivalence_group_id == "leetcode:0001"
    
    assert cpp_rec.task_id == "0001"
    assert cpp_rec.task_name == "Two Sum"
    assert cpp_rec.task_category == "Easy"
    assert cpp_rec.code_raw == "int main() { return 0; }"
