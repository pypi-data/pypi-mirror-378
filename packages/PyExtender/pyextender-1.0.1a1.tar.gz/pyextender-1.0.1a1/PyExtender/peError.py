class InvalidArgumentTypeError(TypeError):
    """当参数类型不正确时抛出此错误"""
    pass

class InvalidFilePathError(ValueError):
    """当文件路径无效时抛出此错误"""
    pass


class MissingFilePathError(ValueError):
    """当没有提供文件路径时抛出此错误"""
    pass

class MissingContentError(ValueError):
    """当没有提供文本内容时抛出此错误"""
    pass

class DirectoryNotFoundError(FileNotFoundError):
    """当目录不存在时抛出此错误"""
    pass
class MissingFunctionNameError(Exception):
    """当没有提供函数名时抛出此错误"""
    pass
class MissingListNameError(Exception):
    """当没有提供列表名时抛出此错误"""
    pass
class MissingVaribleNameError(Exception):
    """当没有提供变量名时抛出此错误"""
    pass
class MissingVaribleValueError(Exception):
    """当没有提供变量值时抛出此错误"""
    pass