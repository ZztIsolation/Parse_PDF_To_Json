"""
测试Ollama连接和模型可用性

使用方法:
    python src/test_ollama_connection.py
"""

import sys

def test_ollama_import():
    """测试ollama库是否安装"""
    print("1️⃣ 测试ollama库...")
    try:
        import ollama
        print("   ✅ ollama库已安装")
        return True
    except ImportError:
        print("   ❌ ollama库未安装")
        print("   请运行: pip install ollama")
        return False


def test_ollama_connection():
    """测试Ollama服务连接"""
    print("\n2️⃣ 测试Ollama服务连接...")
    try:
        import ollama
        # 尝试列出模型
        models = ollama.list()
        print("   ✅ Ollama服务运行正常")
        return True, models
    except Exception as e:
        print(f"   ❌ Ollama服务连接失败: {e}")
        print("   请确保Ollama服务正在运行")
        return False, None


def test_model_availability(models_info):
    """测试qwen2.5:7b模型是否可用"""
    print("\n3️⃣ 检查qwen2.5:7b模型...")
    
    if not models_info:
        print("   ❌ 无法获取模型列表")
        return False
    
    # 检查模型列表
    # Ollama返回的是一个对象，需要访问models属性
    try:
        # 尝试访问models属性（新版本）
        if hasattr(models_info, 'models'):
            models = models_info.models
        # 或者作为字典访问（旧版本）
        elif isinstance(models_info, dict):
            models = models_info.get('models', [])
        else:
            models = []

        # 提取模型名称
        model_names = []
        for model in models:
            if hasattr(model, 'model'):
                model_names.append(model.model)
            elif isinstance(model, dict):
                model_names.append(model.get('name', model.get('model', '')))
            else:
                model_names.append(str(model))

        print(f"   已安装的模型: {len(model_names)} 个")
        for name in model_names:
            print(f"     - {name}")

        # 检查qwen2.5:7b
        target_models = ['qwen2.5:7b', 'qwen2.5:latest']
        found = any(model in model_names for model in target_models)

        if found:
            print("   ✅ qwen2.5:7b模型已安装")
            return True
        else:
            print("   ❌ qwen2.5:7b模型未安装")
            print("   请运行: ollama pull qwen2.5:7b")
            return False
    except Exception as e:
        print(f"   ❌ 解析模型列表失败: {e}")
        return False


def test_model_inference():
    """测试模型推理"""
    print("\n4️⃣ 测试模型推理...")
    try:
        import ollama
        import time
        
        start_time = time.time()
        
        response = ollama.chat(
            model='qwen2.5:7b',
            messages=[
                {'role': 'user', 'content': '你好，请用一句话介绍你自己'}
            ]
        )
        
        elapsed = time.time() - start_time
        
        print("   ✅ 模型推理成功")
        print(f"   ⏱️  推理耗时: {elapsed:.2f}秒")
        print(f"   💬 模型回复: {response['message']['content'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 模型推理失败: {e}")
        return False


def test_chinese_processing():
    """测试中文文本处理能力"""
    print("\n5️⃣ 测试中文文本处理...")
    try:
        import ollama
        
        test_text = """一、 课程目标


《程序设计基础》是计算机类相关专业的一门重要的学科基础课程，它为其它专业课程奠定程


序设计的基础，又是其它专业课程的程序设计工具。

534

课程目标 1 ：系统掌握 C 语言数据类型、常量、变量、运算符、表达式、语句和函数等语义、


语法和使用方法。"""
        
        system_prompt = "你是一个文本清理助手。请删除文本中的页码（如534）和多余的空行，将句子合并成连续段落。只输出清理后的文本。"
        
        response = ollama.chat(
            model='qwen2.5:7b',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"请清理以下文本：\n\n{test_text}"}
            ],
            options={'temperature': 0.3}
        )
        
        result = response['message']['content']
        
        print("   ✅ 中文处理成功")
        print("   📝 清理结果:")
        print("   " + "-"*66)
        for line in result.split('\n')[:5]:
            print(f"   {line}")
        print("   " + "-"*66)
        
        return True
        
    except Exception as e:
        print(f"   ❌ 中文处理失败: {e}")
        return False


def main():
    """主测试流程"""
    print("="*70)
    print("🧪 Ollama环境测试")
    print("="*70)
    
    # 测试1: 库安装
    if not test_ollama_import():
        print("\n❌ 测试终止: 请先安装ollama库")
        sys.exit(1)
    
    # 测试2: 服务连接
    connected, models_info = test_ollama_connection()
    if not connected:
        print("\n❌ 测试终止: 请启动Ollama服务")
        sys.exit(1)
    
    # 测试3: 模型可用性
    if not test_model_availability(models_info):
        print("\n❌ 测试终止: 请安装qwen2.5:7b模型")
        sys.exit(1)
    
    # 测试4: 模型推理
    if not test_model_inference():
        print("\n❌ 测试终止: 模型推理失败")
        sys.exit(1)
    
    # 测试5: 中文处理
    if not test_chinese_processing():
        print("\n⚠️ 警告: 中文处理测试失败，但可以继续")
    
    # 全部通过
    print("\n" + "="*70)
    print("🎉 所有测试通过! 环境配置正确!")
    print("="*70)
    print("\n✅ 你现在可以运行:")
    print("   python src/test_single_file.py      # 测试单个文件")
    print("   python src/process_markdown.py      # 批量处理所有文件")
    print("="*70)


if __name__ == '__main__':
    main()

