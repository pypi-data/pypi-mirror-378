import pytest
from xl_docx.compiler.processors.paragraph import ParagraphProcessor


class TestParagraphProcessor:
    """测试ParagraphProcessor类的功能"""

    def test_decompile_with_empty_space(self):
        xml = '''
        <w:p>
            <w:r>
                <w:t xml:space="preserve">  邮编：201700</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-p><xl-span>  邮编：201700</xl-span></xl-p>' in result

    def test_decompile_with_color(self):
        xml = '''
        <w:p>
            <w:r>
                <w:rPr>
                    <w:color w:val="D7D7D7"/>
                </w:rPr>
                <w:t>content</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'color:D7D7D7' in result

    def test_compile_with_color(self):
        xml = '''
        <xl-p style="font-size:12px;color:D7D7D7">content</xl-p>
        '''
        result = ParagraphProcessor.compile(xml)
        assert '<w:color w:val="D7D7D7"/>' in result
        xml = '''
        <xl-p style="color:D7D7D7;font-size:12px;">content</xl-p>
        '''
        result = ParagraphProcessor.compile(xml)
        assert '<w:color w:val="D7D7D7"/>' in result

    def test_decompile_margin(self):
        xml = '''
        <w:p>
            <w:pPr>
                <w:ind w:start="21pt"/>
            </w:pPr>
            <w:r>
                <w:t>This is a paragraph with left indentation of 21pt.</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'margin-left:21pt' in result
        xml = '''
        <w:p>
            <w:pPr>
                <w:ind w:end="21pt"/>
            </w:pPr>
            <w:r>
                <w:t>This is a paragraph with right indentation of 21pt.</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'margin-right:21pt' in result
        xml = '''
        <w:p>
            <w:pPr>
                <w:ind w:start="21pt" w:end="22pt"/>
            </w:pPr>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'margin-left:21pt' in result
        assert 'margin-right:22pt' in result

    def test_compile_margin(self):
        xml = '<xl-p style="margin-left:21pt">This is a paragraph with left indentation of 21pt.</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:ind w:start="21pt"/>' in result
        xml = '<xl-p style="margin-right:21pt">This is a paragraph with right indentation of 21pt.</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:ind w:end="21pt"/>' in result
        xml = '<xl-p style="margin-left:21pt;margin-right:22pt">This is a paragraph with left and right indentation of 21pt and 22pt.</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:ind w:start="21pt" w:end="22pt"/>' in result
    
    def test_compile_simple_paragraph(self):
        """测试编译简单段落"""
        xml = '<xl-p style="align:center;english:SimSun;chinese:SimSun">检件名称</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:p>' in result
        assert '<w:r>' in result
        assert '<w:t' in result
        assert '检件名称' in result
    
    def test_compile_paragraph_with_style(self):
        """测试编译带样式的段落"""
        xml = '<xl-p style="align:center;margin-top:10px;line-height:14pt;font-size:14px">content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:jc w:val="center"/>' in result
        assert 'w:before="10px"' in result
        assert 'w:line="14pt"' in result
        assert 'w:val="14px"' in result
    
    def test_compile_paragraph_with_fonts(self): 
        """测试编译带字体的段落"""
        xml = '<xl-p style="english:Arial;chinese:SimSun;font-size:12px">content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert 'w:ascii="Arial"' in result
        assert 'w:cs="SimSun"' in result
        assert 'w:val="12px"' in result
    
    def test_compile_paragraph_with_bold(self):
        """测试编译粗体段落"""
        xml = '<xl-p style="font-weight:bold">content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:b/>' in result
    
    def test_compile_paragraph_with_span(self):
        """测试编译包含span的段落"""
        xml = '<xl-p>text<xl-span style="underline:single;font-size:16px">span content</xl-span>more text</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:u w:val="single"/>' in result
        assert 'w:val="16px"' in result
        assert 'span content' in result
    
    def test_compile_paragraph_complex_style(self):
        """测试编译复杂样式的段落"""
        xml = '''<xl-p style="align:right;margin-top:20px;margin-bottom:10px;english:Times New Roman;chinese:宋体;font-size:16px;font-weight:bold">content</xl-p>'''
        result = ParagraphProcessor.compile(xml)
        assert '<w:jc w:val="right"/>' in result
        assert 'w:before="20px"' in result
        assert 'w:after="10px"' in result
        assert 'w:ascii="Times New Roman"' in result
        assert 'w:cs="宋体"' in result
        assert 'w:val="16px"' in result
        assert '<w:b/>' in result
    
    def test_compile_paragraph_no_style(self):
        """测试编译无样式的段落"""
        xml = '<xl-p>content</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:p>' in result
        assert '<w:r>' in result
        assert '<w:t' in result
        assert 'content' in result
    
    def test_compile_paragraph_empty_content(self):
        """测试编译空内容的段落"""
        xml = '<xl-p></xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert '<w:p>' in result
        assert '<w:r>' in result
        assert '<w:t' in result
    
    def test_compile_paragraph_with_nested_spans(self):
        """测试编译包含嵌套span的段落"""
        xml = '''<xl-p><xl-span style="underline:double">span1</xl-span><xl-span style="font-weight:bold">span2</xl-span><xl-span>more text</xl-span></xl-p>'''
        result = ParagraphProcessor.compile(xml)
        assert '<w:u w:val="double"/>' in result
        assert '<w:b/>' in result
        assert 'span1' in result
        assert 'span2' in result
    
    def test_decompile_simple_paragraph(self):
        """测试反编译简单段落"""
        xml = '''<w:p><w:r><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-p>' in result
        assert 'content' in result
    
    def test_decompile_paragraph_with_alignment(self):
        """测试反编译带对齐的段落"""
        xml = '''<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'align:center' in result
    
    def test_decompile_paragraph_with_spacing(self):
        """测试反编译带间距的段落"""
        xml = '''<w:p><w:pPr><w:spacing w:before="20px" w:after="10px"/></w:pPr><w:r><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'margin-top:20px' in result
        assert 'margin-bottom:10px' in result
        xml = '''
        <w:p>
            <w:pPr>
                <w:spacing w:before="240" w:line="18pt" w:lineRule="auto"/>
            </w:pPr>
            <w:r>
                <w:t>This is a paragraph with 12pt spacing above.</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert 'line-height:18pt' in result

    def test_decompile_r_with_spacing(self):
        xml = '''
        <w:p>
            <w:r>
                <w:rPr>
                    <w:spacing w:val="45"/>
                </w:rPr>
                <w:t>器具名称</w:t>
            </w:r>
        </w:p>
        '''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-span style="spacing:45">器具名称</xl-span>' in result

    def test_compile_r_with_spacing(self):
        xml = '''<xl-p><xl-span style="spacing:45">器具名称</xl-span></xl-p>'''
        result = ParagraphProcessor.compile(xml)
        assert '<w:spacing w:val="45"/>' in result

    def test_compile_paragraph_with_spacing(self):
        xml = '<xl-p style="spacing:240">This is a paragraph with 12pt spacing above.</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert 'w:spacing w:val="240"' in result
    
    def test_decompile_paragraph_with_fonts(self):
        """测试反编译带字体的段落"""
        xml = '''<w:p><w:r><w:rPr><w:rFonts w:ascii="Arial" w:cs="SimSun"/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'english:Arial' in result
        assert 'chinese:SimSun' in result
    
    def test_decompile_paragraph_with_font_size(self):
        """测试反编译带字体大小的段落"""
        xml = '''<w:p><w:r><w:rPr><w:sz w:val="16px"/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'font-size:16px' in result
    
    def test_decompile_paragraph_with_bold(self):
        """测试反编译粗体段落"""
        xml = '''<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'font-weight:bold' in result
    
    def test_decompile_paragraph_with_underline(self):
        """测试反编译带下划线的段落"""
        xml = '''<w:p><w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'underline:single' in result
    
    def test_decompile_paragraph_with_span(self):
        """测试反编译包含span的段落"""
        xml = '''<w:p><w:r><w:t>text</w:t></w:r><w:r><w:rPr><w:u w:val="double"/></w:rPr><w:t>span content</w:t></w:r><w:r><w:t>more text</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-span' in result
        assert 'underline:double' in result
        assert 'span content' in result
    
    def test_decompile_paragraph_complex(self):
        """测试反编译复杂段落"""
        xml = '''<w:p><w:pPr><w:jc w:val="right"/><w:spacing w:before="20px" w:after="10px"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" w:cs="SimSun"/><w:sz w:val="16px"/><w:b/></w:rPr><w:t>content</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'align:right' in result
        assert 'margin-top:20px' in result
        assert 'margin-bottom:10px' in result
        assert 'english:Arial' in result
        assert 'chinese:SimSun' in result
        assert 'font-size:16px' in result
        assert 'font-weight:bold' in result
    
    def test_decompile_paragraph_no_runs(self):
        """测试反编译没有运行标签的段落"""
        xml = '''<w:p><w:pPr><w:jc w:val="center"/></w:pPr></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-p style="align:center"></xl-p>' in result  # 应该转换为xl-p格式
    
    def test_decompile_paragraph_with_empty_runs(self):
        """测试反编译包含空运行的段落"""
        xml = '''<w:p><w:r><w:t></w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert '<xl-p><xl-span></xl-span></xl-p>' in result
    
    def test_decompile_paragraph_with_multiple_runs(self):
        """测试反编译包含多个运行的段落"""
        xml = '''<w:p><w:r><w:t>part1</w:t></w:r><w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>part2</w:t></w:r><w:r><w:t>part3</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'part1' in result
        assert 'part2' in result
        assert 'part3' in result
        assert '<xl-span' in result
        assert 'underline:single' in result
    
    def test_decompile_paragraph_with_nested_spans(self):
        """测试反编译包含嵌套span的段落"""
        xml = '''<w:p><w:r><w:t>text</w:t></w:r><w:r><w:rPr><w:u w:val="double"/></w:rPr><w:t>span1</w:t></w:r><w:r><w:rPr><w:u w:val="double"/><w:b/></w:rPr><w:t>span2</w:t></w:r><w:r><w:rPr><w:u w:val="double"/></w:rPr><w:t>span3</w:t></w:r><w:r><w:t>more text</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'text' in result
        assert 'span1' in result
        assert 'span2' in result
        assert 'span3' in result
        assert 'more text' in result
        assert '<xl-span' in result
        assert 'underline:double' in result
        assert 'font-weight:bold' in result
    
    def test_compile_paragraph_with_whitespace(self):
        """测试编译包含空白字符的段落"""
        xml = '<xl-p>  content with spaces  </xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert 'content with spaces' in result
    
    def test_decompile_paragraph_with_whitespace(self):
        """测试反编译包含空白字符的段落"""
        xml = '''<w:p><w:r><w:t xml:space="preserve">  content with spaces  </w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'content with spaces' in result
    
    def test_compile_paragraph_with_special_characters(self):
        """测试编译包含特殊字符的段落"""
        xml = '<xl-p>content with &lt;tags&gt; and "quotes"</xl-p>'
        result = ParagraphProcessor.compile(xml)
        assert 'content with &lt;tags&gt; and "quotes"' in result
    
    def test_decompile_paragraph_with_special_characters(self):
        """测试反编译包含特殊字符的段落"""
        xml = '''<w:p><w:r><w:t>content with &lt;tags&gt; and "quotes"</w:t></w:r></w:p>'''
        result = ParagraphProcessor.decompile(xml)
        assert 'content with &lt;tags&gt; and "quotes"' in result

    def test_process_block_with_variable(self):
        """测试处理使用变量的xl-block标签"""
        xml = '<xl-block text="{{content}}" style="align:center"></xl-block>'
        result = ParagraphProcessor.process_block(xml)
        assert '($ with $)' in result
        assert '($ set paragraphs={{content}}.split(\'\\n\') $)' in result
        assert '($ for paragraph in paragraphs $)' in result
        assert '<xl-p style="align:center">' in result
        assert '<xl-span>((paragraph))</xl-span>' in result
        assert '($ endfor $)' in result
        assert '($ endwith $)' in result
        assert 'xl-block' not in result
        xml = '''
        <xl-p style="align:left;english:Calibri;chinese:SimSun"/>
        <xl-block text="data.get('purpose','')" style="align:left;english:Calibri;chinese:SimSun"/>
        <xl-p style="align:left;english:Calibri;chinese:SimSun"/>
        '''
        result = ParagraphProcessor.process_block(xml)
        assert 'xl-block' not in result

    def test_process_block_with_variable_and_style(self):
        """测试处理使用变量和样式的xl-block标签"""
        xml = '<xl-block text="{{text_content}}" style="align:center;font-size:14px"></xl-block>'
        result = ParagraphProcessor.process_block(xml)
        assert '($ with $)' in result
        assert '($ set paragraphs={{text_content}}.split(\'\\n\') $)' in result
        assert '($ for paragraph in paragraphs $)' in result
        assert '<xl-p style="align:center;font-size:14px">' in result
        assert '<xl-span>((paragraph))</xl-span>' in result
        assert '($ endfor $)' in result
        assert '($ endwith $)' in result

    def test_compile_xl_image_in_span(self):
        """测试xl-image标签在xl-span中的编译"""
        xml = '''<xl-p>
    <xl-span>
        <xl-image rid="rId1" width="200" height="150"></xl-image>
    </xl-span>
</xl-p>'''
        
        result = ParagraphProcessor.compile(xml)
        
        # 检查是否包含段落结构
        assert '<w:p>' in result
        assert '<w:pPr>' in result
        assert '</w:pPr>' in result
        
        # 检查是否包含图片结构
        assert '<w:r>' in result
        assert '<w:pict>' in result
        assert '<v:shape' in result
        assert 'r:id="rId1"' in result
        assert 'width:200px' in result
        assert 'height:150px' in result
        
        # 检查图片是否在span结构中
        assert '<v:imagedata' in result
        assert '<o:lock' in result

    def test_compile_xl_image_in_span_with_style(self):
        """测试带样式的xl-span中包含xl-image标签的编译"""
        xml = '''<xl-p>
    <xl-span style="color:red;font-size:14px">
        <xl-image rid="rId2" width="300" height="200"></xl-image>
    </xl-span>
</xl-p>'''
        
        result = ParagraphProcessor.compile(xml)
        
        # 检查段落结构
        assert '<w:p>' in result
        assert '<w:pPr>' in result
        
        # 检查span样式
        assert '<w:rPr>' in result
        assert '<w:color w:val="red"/>' in result
        assert '<w:sz w:val="14px"/>' in result
        
        # 检查图片结构
        assert '<w:r>' in result
        assert '<w:pict>' in result
        assert 'r:id="rId2"' in result
        assert 'width:300px' in result
        assert 'height:200px' in result

    def test_compile_xl_image_in_span_with_template_variables(self):
        """测试xl-span中包含带模板变量的xl-image标签的编译"""
        xml = '''<xl-p>
    <xl-span>
        <xl-image rid="{{image_id}}" width="{{img_width}}" height="{{img_height}}"></xl-image>
    </xl-span>
</xl-p>'''
        
        result = ParagraphProcessor.compile(xml)
        
        # 检查段落结构
        assert '<w:p>' in result
        assert '<w:pPr>' in result
        
        # 检查图片结构中的模板变量
        assert '<w:r>' in result
        assert '<w:pict>' in result
        assert 'r:id="{{image_id}}"' in result
        assert 'width:{{img_width}}px' in result
        assert 'height:{{img_height}}px' in result

    def test_compile_multiple_xl_images_in_spans(self):
        """测试多个xl-span中包含xl-image标签的编译"""
        xml = '''<xl-p>
    <xl-span>图片1: <xl-image rid="rId1" width="100" height="80"></xl-image></xl-span>
    <xl-span>图片2: <xl-image rid="rId2" width="200" height="150"></xl-image></xl-span>
</xl-p>'''
        
        result = ParagraphProcessor.compile(xml)
        
        # 检查段落结构
        assert '<w:p>' in result
        assert '<w:pPr>' in result
        
        # 检查两个图片都被编译
        assert result.count('<w:r>') == 2
        assert result.count('<w:pict>') == 2
        assert result.count('<v:imagedata') == 2
        
        # 检查具体的图片ID
        assert 'r:id="rId1"' in result
        assert 'r:id="rId2"' in result
        assert 'width:100px' in result
        assert 'width:200px' in result
        
        # 检查文本内容
        assert '图片1:' in result
        assert '图片2:' in result

    def test_compile_xl_image_in_nested_spans(self):
        """测试嵌套xl-span中包含xl-image标签的编译"""
        xml = '''<xl-p>
    <xl-span style="color:blue">
        外层span
        <xl-span style="font-weight:bold">
            内层span: <xl-image rid="rId3" width="150" height="120"></xl-image>
        </xl-span>
    </xl-span>
</xl-p>'''
        
        result = ParagraphProcessor.compile(xml)
        
        # 检查段落结构
        assert '<w:p>' in result
        assert '<w:pPr>' in result
        
        # 检查图片结构
        assert '<w:r>' in result
        assert '<w:pict>' in result
        assert 'r:id="rId3"' in result
        assert 'width:150px' in result
        assert 'height:120px' in result
        
        # 检查文本内容
        assert '外层span' in result
        assert '内层span:' in result