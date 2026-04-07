import os
import sys
from setuptools import setup, find_namespace_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')

def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.BetterIncludeDocxTemplate',
      version='1.0.0',
      description=('A docassemble extension to improve the include_docx_template() function by making it accept booleans as keyword arguments.'),
      long_description='\r\n## What it is\r\n\r\nA docassemble extension to improve the include_docx_template() function by letting it pass booleans to the subdocument.\r\n\r\nThis allows for generic sub-documents which change based on where the context in which they are referenced.\r\n\r\nHopefully this helps someone.\r\n\r\n## Example\r\nThe following example is adapted from the [Docassemble documentation by Jonathan Pyle](https://docassemble.org/docs/functions.html#include_docx_template), licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).\r\n\r\n### Input\r\n#### Variables\r\n```yaml\r\nplanet.name.text: Wheurbunker\r\n---\r\nfather.name.first: "Bohemius"\r\nson.name.first: "Archibald"\r\nstrong_father_son_bond: True\r\npresent_one: "shiny slinky"\r\n---\r\nmother.name.first: "Jemimia"\r\ndaughter.name.first: "Marietta"\r\nstrong_mother_daughter_bond: False\r\npresent_one: "equally shiny slinky"\r\n\r\n```\r\n#### Super-document (`main_docx_params.docx`)\r\n\r\nThe main document contains the following jinja:\r\n```\r\nOnce upon a time, on {{ planet }}, there were two transactions.\r\n\r\n{{p include_docx_template(\'sub_doc_params.docx\', grantor=father, grantee=son, thing=present_one, good_ending=strong_father_son_bond }}\r\n\r\n{{p include_docx_template(\'sub_doc_params.docx\', grantor=mother, grantee=daughter, thing=present_two, good_ending=strong_mother_daughter_bond }}\r\n```\r\nNote that `good ending` is set to `strong_father_son_bond` / `strong_mother_daughter_bond`, which are booleans.\r\n\r\n#### Sub-document (`sub_doc_params.docx`)\r\n\r\nThe referenced subdocument contains the following jinja:\r\n```\r\nThere was a transaction.\r\n{{ grantor.name.first }} gave a(n) {{ thing}} to {{ grantee.name.first }}.\r\n{% if good_ending %}\r\nThey all lived happily ever after on planet {{ planet }}.\r\n{% else %}\r\nThey all lived miserably for the rest of their lives on planet {{ planet }}.\r\n{% endif %}\r\n```\r\n\r\n### Output\r\nThe output document will contain the following text:\r\n\r\n```\r\nOnce upon a time, on Wheurbunker, there were two transactions.\r\n\r\nThere was a transaction.\r\nBohemius gave a(n) shiny slinky to Archibald.\r\nThey all lived happily ever after on planet Wheurbunker.\r\n\r\nThere was a transaction\r\nJemimia game a(n) equally shiny slinky to Marietta.\r\nThey all lived miserably for the rest of their lives on planet Wheurbunker.\r\n```\r\n## What\'s the Point?\r\n\r\nIf you wanted to achieve the same result without this package, you might do something along these lines:\r\n\r\n - Define `father_son_bond` and `mother_daughter_bond` as `"good"` and `"bad"`, respectively.\r\n - In `main_docx_params.docx`, set `ending` to `father_son_bond` for the first transaction and to `mother_daughter_bond` for the second transaction.\r\n - In `sub_doc_params.docx`, change the conditional to:\r\n\t ```\r\n\t {% if ending == "good" %}\r\n\t text\r\n\t {% elif ending == "bad" %}\r\n\t text\r\n\t {% endif %}\r\n\t ```\r\nHowever, I believe that the example shown at the top of the document works better for this application, along with others that I (and maybe you) encounter.\r\n\r\n## How it Works\r\nThis is the chunk of code inside `include_docx_template()` that lets you pass kwargs to the subdocument as DAObjects & strings:\r\n```python\r\nfor key, val in kwargs.items():\r\n    if hasattr(val, \'instanceName\'):\r\n        the_repr = val.instanceName\r\n    else:\r\n        the_repr = \'_codecs.decode(_array.array("b", "\' + re.sub(r\'\\n\', \'\', codecs.encode(bytearray(val, encoding=\'utf-8\'), \'base64\').decode()) + \'".encode()), "base64").decode()\'\r\n    first_paragraph.insert_paragraph_before(str("{%%p set %s = %s %%}" % (key, the_repr)))\r\n```\r\nThe only change this module makes to the code is adding two lines to the if statement:\r\n```python\r\nelif isinstance(val, bool):\r\n    the_repr = val\r\n```\r\n## Changelog\r\n### 1.0.0\r\n- First Release :D',
      long_description_content_type='text/markdown',
      author='J. Kelton',
      author_email='',
      license='MIT',
      url='https://docassemble.org',
      packages=find_namespace_packages(),
      install_requires=[],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/BetterIncludeDocxTemplate/', package='docassemble.BetterIncludeDocxTemplate'),
     )
