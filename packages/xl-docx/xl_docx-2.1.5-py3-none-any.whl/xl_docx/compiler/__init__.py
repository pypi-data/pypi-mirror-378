from jinja2 import Environment, BaseLoader, TemplateNotFound
from typing import Dict, Any
from xl_docx.compiler.processors import StyleProcessor, DirectiveProcessor, \
TableProcessor, ParagraphProcessor, PagerProcessor


class XMLTemplateLoader(BaseLoader):
    def __init__(self, template_str: str):
        self.template_str = template_str

    def get_source(self, environment: Environment, template: str) -> tuple:
        if template == 'root':
            return self.template_str, None, lambda: True
        raise TemplateNotFound(template)

class XMLCompiler:
    """XML编译器主类"""
    def __init__(self):
        self.processors = [
            StyleProcessor(),
            DirectiveProcessor(), 
            TableProcessor(),
            ParagraphProcessor(),
            PagerProcessor()
        ]
        self.env = Environment(
            loader=XMLTemplateLoader(""),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def compile_template(self, template: str) -> str:
        for processor in self.processors:
            if hasattr(processor, 'compile'):
                template = processor.compile(template)
            
        return template
    
    def decompile_template(self, template: str) -> str:
        for processor in self.processors:
            if hasattr(processor, 'decompile'):
                template = processor.decompile(template)
            
        return template
    

    def render_template(self, template: str, data: Dict[str, Any]) -> str:
        processed_template = self.compile_template(template)
        env = Environment(
            loader=XMLTemplateLoader(processed_template),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        template = env.get_template('root')
        result = template.render(**data)
        
        return result
