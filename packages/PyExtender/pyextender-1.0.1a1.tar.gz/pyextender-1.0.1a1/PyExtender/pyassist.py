from .peError import *

class create_list:
    @staticmethod
    def functions(function_name:list = None, file:str = None):
        n = len(function_name)
        if file is None:
            raise MissingFilePathError("Please provide a file path.")
        
        if function_name is None:
            raise MissingFunctionNameError("Please provide a function" + "'s" + 'name.')
        
        if not isinstance(file,str):
            raise InvalidArgumentTypeError('The file path is not string.')
        
        if not isinstance(function_name,list):
            raise InvalidArgumentTypeError('The \"function'+ "'s" + 'name\" is not a list.')
        
        try:
            for i in range(n):
                with open(file, 'a', encoding='utf-8') as f:
                    f.write('\ndef ' + function_name[i] + '():\n    pass\n')
        except PermissionError as e:
            PermissionError(f"Permission denied: cannot write to '{file}'.")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"The directory for '{file}' does not exist.")
        except OSError as e:
            raise OSError(f"Failed to write to file '{file}': {e}.")
        except Exception as e:
            print(f'Unknown Error:{e}')

    @staticmethod
    def list(list_name:list = None, list_element:list = None, file:str = None):
        """Hint: The elements of the list_element list parameter are themselves also lists."""
        n = len(list_name)
        if file is None:
            raise MissingFilePathError("Please provide a file path.")
        
        if list_name is None:
            raise MissingListNameError("Please provide a function" + "'s" + 'name.')
        
        if not isinstance(file,str):
            raise InvalidArgumentTypeError('The file path is not string.')
        
        if not isinstance(list_name,list):
            raise InvalidArgumentTypeError('The \"list'+ "'s" + 'name\" is not a list.')
        
        try:
            for i in range(n):
                with open(file, 'a', encoding='utf-8') as f:
                    if list_element is None:
                        f.write(f"\n{list_name[i]}=[]")
                    if list_element is not None:    
                        s = str(list_element[i])
                        if s.startswith("[") and s.endswith("]"):
                            f.write(f"\n{list_name[i]}={list_element[i]}")
        except PermissionError as e:
            PermissionError(f"Permission denied: cannot write to '{file}'.")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"The directory for '{file}' does not exist.")
        except OSError as e:
            raise OSError(f"Failed to write to file '{file}': {e}.")
        except Exception as e:
            print(f'Unknown Error:{e}')


    @staticmethod
    def variable(variable_name:list = None, variable_value:list = None, file:str = None):
        n = len(variable_name)
        if file is None:
            raise MissingFilePathError("Please provide a file path.")
        
        if variable_name is None:
            raise MissingVaribleNameError("Please provide a varible" + "'s" + 'name.')
        
        if variable_value is None:
            raise MissingVaribleValueError("Please provide a varible" + "'s" + 'value.')
        
        if not isinstance(file,str):
            raise InvalidArgumentTypeError('The file path is not string.')
        if not isinstance(variable_name,list):
            raise InvalidArgumentTypeError('The \"varible'+ "'s" + 'name\" must be a list.')
        if not isinstance(variable_value,list):
            raise InvalidArgumentTypeError('The \"varible'+ "'s" + 'value\" must be a list.')
        
        try:
            for i in range(n):
                with open(file, 'a', encoding='utf-8') as f: 
                    s = variable_value[i]
                    if isinstance(s, str):
                        f.write(f"\n{variable_name[i]}=\"{variable_value[i]}\"")
                    else:
                        f.write(f"\n{variable_name[i]}={variable_value[i]}")
        except PermissionError as e:
            PermissionError(f"Permission denied: cannot write to '{file}'.")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"The directory for '{file}' does not exist.")
        except OSError as e:
            raise OSError(f"Failed to write to file '{file}': {e}.")
        except Exception as e:
            print(f'Unknown Error:{e}')
"""
    @staticmethod
    def set():
        print("This Function = None")

    @staticmethod
    def tuple():
        print("This Function = None")

    @staticmethod
    def dictionary():
        print("This Function = None")

    @staticmethod
    def classes():
        print("This Function = None")
        """
