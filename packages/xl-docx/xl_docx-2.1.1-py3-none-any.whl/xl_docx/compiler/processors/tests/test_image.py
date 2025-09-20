import pytest
from xl_docx.compiler.processors.paragraph.image import ImageProcessor


class TestImageProcessor:
    """测试ImageProcessor的功能"""
    
    def test_compile_xl_image_basic(self):
        """测试基本的xl-image标签编译"""
        processor = ImageProcessor()
        xml = '<xl-image rid="{{rid}}" width="{{width}}" height="{{height}}"></xl-image>'
        
        result = processor.compile(xml)
        
        expected = '''<w:r>
    <w:pict>
        <v:shape coordsize="21600,21600" filled="f" id="_x0000_s1026" o:spid="_x0000_s1026" o:spt="75" style="width:{{width}}px;height:{{height}}px" type="#_x0000_t75">
            <v:path/>
            <v:fill focussize="0,0" on="f"/>
            <v:stroke/>
            <v:imagedata o:title="" r:id="{{rid}}"/>
            <o:lock v:ext="edit"/>
            <w10:wrap type="none"/>
            <w10:anchorlock/>
        </v:shape>
    </w:pict>
</w:r>'''
        
        assert result == expected
    
    def test_compile_xl_image_with_content(self):
        """测试包含内容的xl-image标签编译"""
        processor = ImageProcessor()
        xml = '<xl-image rid="rId1" width="200" height="150">Some content</xl-image>'
        
        result = processor.compile(xml)
        
        expected = '''<w:r>
    <w:pict>
        <v:shape coordsize="21600,21600" filled="f" id="_x0000_s1026" o:spid="_x0000_s1026" o:spt="75" style="width:200px;height:150px" type="#_x0000_t75">
            <v:path/>
            <v:fill focussize="0,0" on="f"/>
            <v:stroke/>
            <v:imagedata o:title="" r:id="rId1"/>
            <o:lock v:ext="edit"/>
            <w10:wrap type="none"/>
            <w10:anchorlock/>
        </v:shape>
    </w:pict>
</w:r>'''
        
        assert result == expected
    
    def test_compile_xl_image_in_span(self):
        """测试xl-image标签在xl-span中的使用"""
        processor = ImageProcessor()
        xml = '''<xl-span>
    <xl-image rid="{{rid}}" width="{{width}}" height="{{height}}"></xl-image>
</xl-span>'''
        
        result = processor.compile(xml)
        
        expected = '''<xl-span>
    <w:r>
    <w:pict>
        <v:shape coordsize="21600,21600" filled="f" id="_x0000_s1026" o:spid="_x0000_s1026" o:spt="75" style="width:{{width}}px;height:{{height}}px" type="#_x0000_t75">
            <v:path/>
            <v:fill focussize="0,0" on="f"/>
            <v:stroke/>
            <v:imagedata o:title="" r:id="{{rid}}"/>
            <o:lock v:ext="edit"/>
            <w10:wrap type="none"/>
            <w10:anchorlock/>
        </v:shape>
    </w:pict>
</w:r>
</xl-span>'''
        
        assert result == expected
    
    def test_compile_multiple_xl_images(self):
        """测试多个xl-image标签的编译"""
        processor = ImageProcessor()
        xml = '''<div>
    <xl-image rid="rId1" width="100" height="80"></xl-image>
    <xl-image rid="rId2" width="200" height="150"></xl-image>
</div>'''
        
        result = processor.compile(xml)
        
        # 检查是否包含两个编译后的图片
        assert result.count('<w:r>') == 2
        assert result.count('<v:imagedata') == 2
        assert 'r:id="rId1"' in result
        assert 'r:id="rId2"' in result
        assert 'width:100px' in result
        assert 'width:200px' in result
    
    def test_compile_xl_image_no_match(self):
        """测试没有xl-image标签时的处理"""
        processor = ImageProcessor()
        xml = '<div>No image here</div>'
        
        result = processor.compile(xml)
        
        assert result == xml
    
    def test_compile_xl_image_missing_attributes(self):
        """测试缺少属性的xl-image标签"""
        processor = ImageProcessor()
        xml = '<xl-image rid="rId1"></xl-image>'
        
        result = processor.compile(xml)
        
        # 即使缺少width和height属性，也应该能编译
        assert '<w:r>' in result
        assert 'r:id="rId1"' in result
        assert 'width:Nonepx' in result
        assert 'height:Nonepx' in result
    
    def test_compile_xl_image_with_template_variables(self):
        """测试包含模板变量的xl-image标签"""
        processor = ImageProcessor()
        xml = '<xl-image rid="{{image_id}}" width="{{img_width}}" height="{{img_height}}"></xl-image>'
        
        result = processor.compile(xml)
        
        expected = '''<w:r>
    <w:pict>
        <v:shape coordsize="21600,21600" filled="f" id="_x0000_s1026" o:spid="_x0000_s1026" o:spt="75" style="width:{{img_width}}px;height:{{img_height}}px" type="#_x0000_t75">
            <v:path/>
            <v:fill focussize="0,0" on="f"/>
            <v:stroke/>
            <v:imagedata o:title="" r:id="{{image_id}}"/>
            <o:lock v:ext="edit"/>
            <w10:wrap type="none"/>
            <w10:anchorlock/>
        </v:shape>
    </w:pict>
</w:r>'''
        
        assert result == expected
