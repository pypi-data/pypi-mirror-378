"""Advanced variable substitution engine with support for nested references and functions."""

import re
import os
import logging
from typing import Dict, Any, Optional, List, Set, Callable, Union
from datetime import datetime
import json
import base64
import hashlib
import uuid

from .env_manager import EnvironmentManager


logger = logging.getLogger(__name__)


class VariableSubstitutionError(Exception):
    """Raised when variable substitution fails."""
    pass


class CircularReferenceError(VariableSubstitutionError):
    """Raised when circular reference is detected in variables."""
    pass


class VariableSubstitutionEngine:
    """Advanced variable substitution engine with functions and nested references."""
    
    def __init__(self, env_manager: Optional[EnvironmentManager] = None):
        self.env_manager = env_manager or EnvironmentManager()
        
        # Variable patterns
        self.simple_pattern = re.compile(r'\$\{([^}:]+)(?::([^}]*))?\}')
        self.function_pattern = re.compile(r'\$\{([a-zA-Z_][a-zA-Z0-9_]*)\(([^)]*)\)\}')
        
        # Built-in functions
        self.functions = {
            'now': self._func_now,
            'uuid': self._func_uuid,
            'random': self._func_random,
            'base64': self._func_base64,
            'hash': self._func_hash,
            'env': self._func_env,
            'upper': self._func_upper,
            'lower': self._func_lower,
            'trim': self._func_trim,
            'replace': self._func_replace,
            'substring': self._func_substring,
            'length': self._func_length,
            'default': self._func_default,
            'json_extract': self._func_json_extract,
            'url_encode': self._func_url_encode,
            'url_decode': self._func_url_decode
        }
        
        # Maximum substitution depth to prevent infinite recursion
        self.max_depth = 10
    
    def substitute(self, text: str, environment: str = "default",
                  custom_variables: Optional[Dict[str, str]] = None,
                  context: Optional[Dict[str, Any]] = None) -> str:
        """
        Perform variable substitution with support for nested references and functions.
        
        Args:
            text: Text containing variables to substitute
            environment: Environment name for variable lookup
            custom_variables: Additional variables to use for substitution
            context: Additional context for function evaluation
            
        Returns:
            Text with variables substituted
            
        Raises:
            VariableSubstitutionError: If substitution fails
            CircularReferenceError: If circular reference is detected
        """
        if not text:
            return text
        
        # Load variables
        variables = self._load_variables(environment, custom_variables)
        
        # Track substitution path to detect circular references
        substitution_path = set()
        
        # Perform substitution with recursion tracking
        return self._substitute_recursive(text, variables, context or {}, substitution_path, 0)
    
    def _load_variables(self, environment: str, custom_variables: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Load variables from environment and custom sources."""
        variables = {}
        
        # Load environment variables
        try:
            env_vars = self.env_manager.list_variables(environment, include_values=True)
            variables.update(env_vars.get('variables', {}))
        except Exception as e:
            logger.warning(f"Failed to load environment '{environment}': {e}")
        
        # Add system environment variables with ENV_ prefix
        for key, value in os.environ.items():
            variables[f"ENV_{key}"] = value
        
        # Add custom variables (override environment variables)
        if custom_variables:
            variables.update(custom_variables)
        
        # Add built-in variables
        variables.update({
            'TIMESTAMP': str(int(datetime.now().timestamp())),
            'ISO_TIMESTAMP': datetime.now().isoformat(),
            'DATE': datetime.now().strftime('%Y-%m-%d'),
            'TIME': datetime.now().strftime('%H:%M:%S'),
            'YEAR': str(datetime.now().year),
            'MONTH': str(datetime.now().month),
            'DAY': str(datetime.now().day)
        })
        
        return variables
    
    def _substitute_recursive(self, text: str, variables: Dict[str, str],
                            context: Dict[str, Any], substitution_path: Set[str],
                            depth: int) -> str:
        """Perform recursive substitution with circular reference detection."""
        if depth > self.max_depth:
            raise VariableSubstitutionError(f"Maximum substitution depth ({self.max_depth}) exceeded")
        
        # Track missing variables
        missing_variables = []
        
        # Function to handle variable substitution
        def replace_variable(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.lastindex >= 2 else None
            
            # Check for circular reference
            if var_name in substitution_path:
                raise CircularReferenceError(f"Circular reference detected: {' -> '.join(substitution_path)} -> {var_name}")
            
            if var_name in variables:
                # Add to substitution path
                new_path = substitution_path.copy()
                new_path.add(var_name)
                
                # Recursively substitute the variable value
                value = variables[var_name]
                return self._substitute_recursive(value, variables, context, new_path, depth + 1)
            elif default_value is not None:
                # Use default value and recursively substitute it
                return self._substitute_recursive(default_value, variables, context, substitution_path, depth + 1)
            else:
                missing_variables.append(var_name)
                return match.group(0)  # Return original if not found
        
        # Function to handle function calls
        def replace_function(match):
            func_name = match.group(1)
            func_args = match.group(2)
            
            if func_name not in self.functions:
                raise VariableSubstitutionError(f"Unknown function: {func_name}")
            
            try:
                # Parse function arguments
                args = self._parse_function_args(func_args)
                
                # Substitute variables in arguments
                substituted_args = []
                for arg in args:
                    substituted_arg = self._substitute_recursive(arg, variables, context, substitution_path, depth + 1)
                    substituted_args.append(substituted_arg)
                
                # Call function
                result = self.functions[func_name](substituted_args, context)
                return str(result)
                
            except Exception as e:
                raise VariableSubstitutionError(f"Function '{func_name}' failed: {e}")
        
        # First pass: substitute functions
        result = self.function_pattern.sub(replace_function, text)
        
        # Second pass: substitute simple variables
        result = self.simple_pattern.sub(replace_variable, result)
        
        # Check for missing variables
        if missing_variables and depth == 0:  # Only report at top level
            raise VariableSubstitutionError(
                f"Missing variables: {', '.join(missing_variables)}. "
                f"Available variables: {', '.join(variables.keys()) if variables else 'none'}"
            )
        
        return result
    
    def _parse_function_args(self, args_str: str) -> List[str]:
        """Parse function arguments from string."""
        if not args_str.strip():
            return []
        
        # Simple argument parsing (comma-separated, with basic quote handling)
        args = []
        current_arg = ""
        in_quotes = False
        quote_char = None
        
        for char in args_str:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ',' and not in_quotes:
                args.append(current_arg.strip())
                current_arg = ""
                continue
            
            current_arg += char
        
        if current_arg.strip():
            args.append(current_arg.strip())
        
        # Remove quotes from arguments
        cleaned_args = []
        for arg in args:
            arg = arg.strip()
            if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                arg = arg[1:-1]
            cleaned_args.append(arg)
        
        return cleaned_args
    
    def extract_variables(self, text: str) -> List[str]:
        """
        Extract all variable names from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of variable names found
        """
        if not text:
            return []
        
        variables = set()
        
        # Extract simple variables
        for match in self.simple_pattern.finditer(text):
            variables.add(match.group(1))
        
        # Extract function calls (functions themselves are not variables)
        # But their arguments might contain variables
        for match in self.function_pattern.finditer(text):
            func_args = match.group(2)
            if func_args:
                # Recursively extract variables from function arguments
                arg_variables = self.extract_variables(func_args)
                variables.update(arg_variables)
        
        return sorted(list(variables))
    
    def validate_syntax(self, text: str) -> List[str]:
        """
        Validate variable substitution syntax.
        
        Args:
            text: Text to validate
            
        Returns:
            List of syntax error messages
        """
        errors = []
        
        if not text:
            return errors
        
        # Check for unmatched braces
        brace_count = 0
        for i, char in enumerate(text):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count < 0:
                    errors.append(f"Unmatched closing brace at position {i}")
                    brace_count = 0  # Reset to continue checking
        
        if brace_count > 0:
            errors.append(f"Unmatched opening brace(s): {brace_count}")
        
        # Check function syntax
        for match in self.function_pattern.finditer(text):
            func_name = match.group(1)
            if func_name not in self.functions:
                errors.append(f"Unknown function: {func_name}")
        
        return errors
    
    # Built-in functions
    
    def _func_now(self, args: List[str], context: Dict[str, Any]) -> str:
        """Return current timestamp in specified format."""
        format_str = args[0] if args else '%Y-%m-%d %H:%M:%S'
        try:
            return datetime.now().strftime(format_str)
        except ValueError as e:
            raise VariableSubstitutionError(f"Invalid date format: {e}")
    
    def _func_uuid(self, args: List[str], context: Dict[str, Any]) -> str:
        """Generate a UUID."""
        version = args[0] if args else '4'
        
        if version == '1':
            return str(uuid.uuid1())
        elif version == '4':
            return str(uuid.uuid4())
        else:
            raise VariableSubstitutionError(f"Unsupported UUID version: {version}")
    
    def _func_random(self, args: List[str], context: Dict[str, Any]) -> str:
        """Generate random number or string."""
        import random
        import string
        
        if not args:
            return str(random.randint(1, 1000))
        
        arg_type = args[0].lower()
        
        if arg_type == 'int':
            min_val = int(args[1]) if len(args) > 1 else 1
            max_val = int(args[2]) if len(args) > 2 else 1000
            return str(random.randint(min_val, max_val))
        
        elif arg_type == 'string':
            length = int(args[1]) if len(args) > 1 else 10
            chars = string.ascii_letters + string.digits
            return ''.join(random.choice(chars) for _ in range(length))
        
        else:
            raise VariableSubstitutionError(f"Unknown random type: {arg_type}")
    
    def _func_base64(self, args: List[str], context: Dict[str, Any]) -> str:
        """Base64 encode/decode."""
        if not args:
            raise VariableSubstitutionError("base64 function requires at least one argument")
        
        operation = args[1].lower() if len(args) > 1 else 'encode'
        text = args[0]
        
        try:
            if operation == 'encode':
                return base64.b64encode(text.encode('utf-8')).decode('ascii')
            elif operation == 'decode':
                return base64.b64decode(text.encode('ascii')).decode('utf-8')
            else:
                raise VariableSubstitutionError(f"Unknown base64 operation: {operation}")
        except Exception as e:
            raise VariableSubstitutionError(f"Base64 {operation} failed: {e}")
    
    def _func_hash(self, args: List[str], context: Dict[str, Any]) -> str:
        """Generate hash of input."""
        if not args:
            raise VariableSubstitutionError("hash function requires at least one argument")
        
        text = args[0]
        algorithm = args[1].lower() if len(args) > 1 else 'sha256'
        
        try:
            if algorithm == 'md5':
                return hashlib.md5(text.encode('utf-8')).hexdigest()
            elif algorithm == 'sha1':
                return hashlib.sha1(text.encode('utf-8')).hexdigest()
            elif algorithm == 'sha256':
                return hashlib.sha256(text.encode('utf-8')).hexdigest()
            else:
                raise VariableSubstitutionError(f"Unsupported hash algorithm: {algorithm}")
        except Exception as e:
            raise VariableSubstitutionError(f"Hash generation failed: {e}")
    
    def _func_env(self, args: List[str], context: Dict[str, Any]) -> str:
        """Get system environment variable."""
        if not args:
            raise VariableSubstitutionError("env function requires variable name")
        
        var_name = args[0]
        default_value = args[1] if len(args) > 1 else ""
        
        return os.environ.get(var_name, default_value)
    
    def _func_upper(self, args: List[str], context: Dict[str, Any]) -> str:
        """Convert text to uppercase."""
        if not args:
            raise VariableSubstitutionError("upper function requires text argument")
        
        return args[0].upper()
    
    def _func_lower(self, args: List[str], context: Dict[str, Any]) -> str:
        """Convert text to lowercase."""
        if not args:
            raise VariableSubstitutionError("lower function requires text argument")
        
        return args[0].lower()
    
    def _func_trim(self, args: List[str], context: Dict[str, Any]) -> str:
        """Trim whitespace from text."""
        if not args:
            raise VariableSubstitutionError("trim function requires text argument")
        
        return args[0].strip()
    
    def _func_replace(self, args: List[str], context: Dict[str, Any]) -> str:
        """Replace text in string."""
        if len(args) < 3:
            raise VariableSubstitutionError("replace function requires text, search, and replacement arguments")
        
        text, search, replacement = args[0], args[1], args[2]
        return text.replace(search, replacement)
    
    def _func_substring(self, args: List[str], context: Dict[str, Any]) -> str:
        """Extract substring."""
        if len(args) < 2:
            raise VariableSubstitutionError("substring function requires text and start position")
        
        text = args[0]
        start = int(args[1])
        end = int(args[2]) if len(args) > 2 else len(text)
        
        return text[start:end]
    
    def _func_length(self, args: List[str], context: Dict[str, Any]) -> str:
        """Get length of text."""
        if not args:
            raise VariableSubstitutionError("length function requires text argument")
        
        return str(len(args[0]))
    
    def _func_default(self, args: List[str], context: Dict[str, Any]) -> str:
        """Return first non-empty argument."""
        for arg in args:
            if arg.strip():
                return arg
        return ""
    
    def _func_json_extract(self, args: List[str], context: Dict[str, Any]) -> str:
        """Extract value from JSON string."""
        if len(args) < 2:
            raise VariableSubstitutionError("json_extract function requires JSON string and path")
        
        json_str = args[0]
        path = args[1]
        
        try:
            data = json.loads(json_str)
            
            # Simple path extraction (dot notation)
            keys = path.split('.')
            current = data
            
            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list) and key.isdigit():
                    index = int(key)
                    current = current[index] if 0 <= index < len(current) else None
                else:
                    current = None
                
                if current is None:
                    break
            
            return str(current) if current is not None else ""
            
        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
            raise VariableSubstitutionError(f"JSON extraction failed: {e}")
    
    def _func_url_encode(self, args: List[str], context: Dict[str, Any]) -> str:
        """URL encode text."""
        if not args:
            raise VariableSubstitutionError("url_encode function requires text argument")
        
        from urllib.parse import quote
        return quote(args[0])
    
    def _func_url_decode(self, args: List[str], context: Dict[str, Any]) -> str:
        """URL decode text."""
        if not args:
            raise VariableSubstitutionError("url_decode function requires text argument")
        
        from urllib.parse import unquote
        return unquote(args[0])
    
    def register_function(self, name: str, func: Callable[[List[str], Dict[str, Any]], str]) -> None:
        """
        Register a custom function.
        
        Args:
            name: Function name
            func: Function implementation
        """
        if not name.isidentifier():
            raise ValueError(f"Invalid function name: {name}")
        
        self.functions[name] = func
        logger.debug(f"Registered custom function: {name}")
    
    def list_functions(self) -> List[Dict[str, str]]:
        """
        List all available functions.
        
        Returns:
            List of function information dictionaries
        """
        functions_info = []
        
        function_docs = {
            'now': 'Get current timestamp with optional format',
            'uuid': 'Generate UUID (version 1 or 4)',
            'random': 'Generate random number or string',
            'base64': 'Base64 encode/decode text',
            'hash': 'Generate hash (md5, sha1, sha256)',
            'env': 'Get system environment variable',
            'upper': 'Convert text to uppercase',
            'lower': 'Convert text to lowercase',
            'trim': 'Trim whitespace from text',
            'replace': 'Replace text in string',
            'substring': 'Extract substring',
            'length': 'Get length of text',
            'default': 'Return first non-empty argument',
            'json_extract': 'Extract value from JSON string',
            'url_encode': 'URL encode text',
            'url_decode': 'URL decode text'
        }
        
        for name in sorted(self.functions.keys()):
            functions_info.append({
                'name': name,
                'description': function_docs.get(name, 'Custom function')
            })
        
        return functions_info