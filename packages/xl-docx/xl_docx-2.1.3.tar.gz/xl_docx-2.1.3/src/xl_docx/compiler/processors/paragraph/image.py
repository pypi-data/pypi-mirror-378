import re
from xl_docx.compiler.processors.base import BaseProcessor


class ImageProcessor(BaseProcessor):
    """处理图片相关的XML标签"""
    def compile(self, xml: str) -> str:
        def process_image(match):
            attrs = self._extract_attrs(match.group(0), ['rid', 'width', 'height'])
            rid = attrs[0]  # rid
            width = attrs[1]  # width
            height = attrs[2]  # height
            
            return f'''<w:r>
    <w:pict>
        <v:shape coordsize="21600,21600" filled="f" id="_x0000_s1026" o:spid="_x0000_s1026" o:spt="75" style="width:{width}px;height:{height}px" type="#_x0000_t75">
            <v:path/>
            <v:fill focussize="0,0" on="f"/>
            <v:stroke/>
            <v:imagedata o:title="" r:id="{rid}"/>
            <o:lock v:ext="edit"/>
            <w10:wrap type="none"/>
            <w10:anchorlock/>
        </v:shape>
    </w:pict>
</w:r>'''
            
        return self._process_tag(xml, r'<xl-image[^>]*>.*?</xl-image>', process_image, flags=re.DOTALL)
