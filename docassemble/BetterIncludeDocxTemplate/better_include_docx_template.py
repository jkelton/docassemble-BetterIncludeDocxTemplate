import re
import os
import codecs
import time
import stat
import mimetypes
import tempfile
import string
import shutil
import zipfile
from collections import deque
from copy import deepcopy
from xml.sax.saxutils import escape as html_escape
from docxtpl import InlineImage, RichText
from docx.shared import Mm, Inches, Pt, Cm, Twips
import docx.opc.constants
from docx.oxml.section import CT_SectPr
from docx.oxml.table import CT_Tbl
import docx
from docxcompose.composer import Composer  # For fixing up images, etc when including docx files within templates
import docassemble.base.functions
from docassemble.base.functions import package_template_filename, get_config, roman
from docassemble.base.error import DAError
import docassemble.base.filter
import docassemble.base.pandoc
from docassemble.base.logger import logmessage
from bs4 import BeautifulSoup, NavigableString, Tag
from pikepdf import Pdf
from docassemble.base.file_docx import fix_subdoc, include_docx_template

def include_docx_template(template_file, **kwargs):
    """Include the contents of one docx file inside another docx file."""
    use_jinja = kwargs.pop('_use_jinja2', True)
    if docassemble.base.functions.this_thread.evaluation_context is None:
        return 'ERROR: not in a docx file'
    if template_file.__class__.__name__ in ('DAFile', 'DAFileList', 'DAFileCollection', 'DALocalFile', 'DAStaticFile'):
        template_path = template_file.path()
    else:
        template_path = package_template_filename(template_file, package=docassemble.base.functions.this_thread.current_package)
    sd = docassemble.base.functions.this_thread.misc['docx_template'].new_subdoc()
    sd.subdocx = docx.Document(template_path)
    change_numbering = bool(kwargs.pop('change_numbering', True))
    if '_inline' in kwargs:
        single_paragraph = True
        del kwargs['_inline']
    else:
        single_paragraph = False

    # We need to keep a copy of the subdocs so we can fix up the master template in the end (in parse.py)
    # Given we're half way through processing the template, we can't fix the master template here
    # we have to do it in post
    if 'docx_subdocs' not in docassemble.base.functions.this_thread.misc:
        docassemble.base.functions.this_thread.misc['docx_subdocs'] = []
    docassemble.base.functions.this_thread.misc['docx_subdocs'].append({'subdoc': deepcopy(sd.subdocx), 'change_numbering': change_numbering})

    # Fix the subdocs before they are included in the template
    fix_subdoc(docassemble.base.functions.this_thread.misc['docx_template'], {'subdoc': sd.subdocx, 'change_numbering': change_numbering})

    first_paragraph = sd.subdocx.paragraphs[0]

    if not use_jinja:
        if single_paragraph:
            return re.sub(r'<w:p[^>]*>\s*(.*)</w:p>\s*', r'\1', sanitize_xml(str(first_paragraph._p.xml)), flags=re.DOTALL)
        return sanitize_xml(str(sd))

    for key, val in kwargs.items():
        if hasattr(val, 'instanceName'):
            the_repr = val.instanceName
        elif isinstance(val, bool):
            the_repr = val
        else:
            the_repr = '_codecs.decode(_array.array("b", "' + re.sub(r'\n', '', codecs.encode(bytearray(val, encoding='utf-8'), 'base64').decode()) + '".encode()), "base64").decode()'
        first_paragraph.insert_paragraph_before(str("{%%p set %s = %s %%}" % (key, the_repr)))
    if 'docx_include_count' not in docassemble.base.functions.this_thread.misc:
        docassemble.base.functions.this_thread.misc['docx_include_count'] = 0
    docassemble.base.functions.this_thread.misc['docx_include_count'] += 1
    if single_paragraph:
        return re.sub(r'<w:p[^>]*>\s*(.*)</w:p>\s*', r'\1', str(first_paragraph._p.xml), flags=re.DOTALL)
    return sd
