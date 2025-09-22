class KeepAlivedConfigError(Exception):
    """Base exception class for KeepAlivedConfig errors"""
    def __init__(self, message, context=None):
        super().__init__(message)
        self.context = context
        
    def __str__(self):
        if self.context:
            return f"{super().__str__()} (Context: {self.context})"
        return super().__str__()


class KeepAlivedConfigParseError(KeepAlivedConfigError):
    """Exception raised when parsing keepalived configuration fails"""
    def __init__(self, message, line_number=None, file_path=None):
        context = {}
        if line_number:
            context['line'] = line_number
        if file_path:
            context['file'] = file_path
        super().__init__(message, context)


class KeepAlivedConfigValidationError(KeepAlivedConfigError):
    """Exception raised when configuration validation fails"""
    def __init__(self, message, param_path=None):
        context = {}
        if param_path:
            context['path'] = param_path
        super().__init__(message, context)


class KeepAlivedConfigTemplateError(KeepAlivedConfigError):
    """Exception raised when template operations fail"""
    def __init__(self, message, template_name=None):
        context = {}
        if template_name:
            context['template'] = template_name
        super().__init__(message, context)