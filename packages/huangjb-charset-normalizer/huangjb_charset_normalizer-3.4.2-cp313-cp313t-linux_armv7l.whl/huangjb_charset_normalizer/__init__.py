
import sys
import os
import importlib.util

package_dir = os.path.dirname(__file__)
lib_build_path = os.path.join(package_dir, "_lib_build")

# 添加库构建路径到Python路径
if lib_build_path not in sys.path:
    sys.path.insert(0, lib_build_path)

try:
    # 方法1: 使用importlib直接从_lib_build/charset_normalizer导入
    lib_path = os.path.join(lib_build_path, "charset_normalizer")
    if os.path.exists(os.path.join(lib_path, "__init__.py")):
        spec = importlib.util.spec_from_file_location("charset_normalizer", os.path.join(lib_path, "__init__.py"))
        lib_module = importlib.util.module_from_spec(spec)
        sys.modules["charset_normalizer"] = lib_module
        spec.loader.exec_module(lib_module)
        
        # 替换当前模块为库模块
        sys.modules[__name__] = lib_module
        globals().update(lib_module.__dict__)
    else:
        # 如果库没有__init__.py，尝试其他导入方式
        sys.path.insert(0, lib_path)
        import charset_normalizer as lib_module
        sys.modules[__name__] = lib_module
        globals().update(lib_module.__dict__)
        
except ImportError as e:
    # 方法2: 备用方案 - 尝试标准导入
    try:
        import charset_normalizer
        sys.modules[__name__] = charset_normalizer
        globals().update(charset_normalizer.__dict__)
    except ImportError:
        error_msg = f"Failed to import charset_normalizer from custom package. Build path: {lib_build_path} Error: {e}"
        raise ImportError(error_msg) from e

print("huangjb_charset_normalizer loaded successfully")
