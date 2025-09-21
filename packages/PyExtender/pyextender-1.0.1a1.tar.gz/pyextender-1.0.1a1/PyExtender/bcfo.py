#This is a basic file operations.
from .peError import *

def output(text:str = None, file:str = None)->bool:
    if file is None:
        raise MissingFilePathError("Please provide a file path.")
    if text is None:
        raise MissingContentError("Please provide some content to output.")
    
    if not isinstance(file,str):
        raise InvalidArgumentTypeError('The file path is not string.')
    
    if not isinstance(text,str):
        raise InvalidArgumentTypeError('The text is not string.')
    
    try:
        with open(file, 'a', encoding='utf-8') as f:
            f.write(text)
        return True
    except PermissionError:
        PermissionError(f"Permission denied: cannot write to '{file}'.")
    except FileNotFoundError:
        raise FileNotFoundError(f"The directory for '{file}' does not exist.")
    except OSError as e:
        raise OSError(f"Failed to write to file '{file}': {e}")
    except Exception as e:
        print(f'Unknown Error{e}')

def create(file:str = None):
    if file is None:
        raise MissingFilePathError("Please provide a file path.")
    
    if not isinstance(file,str):
        raise InvalidArgumentTypeError('The file path is not string.')
    
    try:
        with open(file, 'a', encoding='utf-8') as f:
            f.write()
    except Exception as e:
        print(f'Unknown Error{e}')
