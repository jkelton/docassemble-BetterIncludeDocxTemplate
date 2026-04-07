
## What it is

A docassemble extension to improve the include_docx_template() function by letting it pass booleans to the subdocument.

This allows for generic sub-documents which change based on where the context in which they are referenced.

Hopefully this helps someone.

## Example
The following example is adapted from the [Docassemble documentation by Jonathan Pyle](https://docassemble.org/docs/functions.html#include_docx_template), licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).

### Input
#### Variables
```yaml
planet.name.text: Wheurbunker
---
father.name.first: "Bohemius"
son.name.first: "Archibald"
strong_father_son_bond: True
present_one: "shiny slinky"
---
mother.name.first: "Jemimia"
daughter.name.first: "Marietta"
strong_mother_daughter_bond: False
present_one: "equally shiny slinky"

```
#### Super-document (`main_docx_params.docx`)

The main document contains the following jinja:
```
Once upon a time, on {{ planet }}, there were two transactions.

{{p include_docx_template('sub_doc_params.docx', grantor=father, grantee=son, thing=present_one, good_ending=strong_father_son_bond }}

{{p include_docx_template('sub_doc_params.docx', grantor=mother, grantee=daughter, thing=present_two, good_ending=strong_mother_daughter_bond }}
```
Note that `good ending` is set to `strong_father_son_bond` / `strong_mother_daughter_bond`, which are booleans.

#### Sub-document (`sub_doc_params.docx`)

The referenced subdocument contains the following jinja:
```
There was a transaction.
{{ grantor.name.first }} gave a(n) {{ thing}} to {{ grantee.name.first }}.
{% if good_ending %}
They all lived happily ever after on planet {{ planet }}.
{% else %}
They all lived miserably for the rest of their lives on planet {{ planet }}.
{% endif %}
```

### Output
The output document will contain the following text:

```
Once upon a time, on Wheurbunker, there were two transactions.

There was a transaction.
Bohemius gave a(n) shiny slinky to Archibald.
They all lived happily ever after on planet Wheurbunker.

There was a transaction
Jemimia game a(n) equally shiny slinky to Marietta.
They all lived miserably for the rest of their lives on planet Wheurbunker.
```
## What's the Point?

If you wanted to achieve the same result without this package, you might do something along these lines:

 - Define `father_son_bond` and `mother_daughter_bond` as `"good"` and `"bad"`, respectively.
 - In `main_docx_params.docx`, set `ending` to `father_son_bond` for the first transaction and to `mother_daughter_bond` for the second transaction.
 - In `sub_doc_params.docx`, change the conditional to:
	 ```
	 {% if ending == "good" %}
	 text
	 {% elif ending == "bad" %}
	 text
	 {% endif %}
	 ```
However, I believe that the example shown at the top of the document works better for this application, along with others that I (and maybe you) encounter.

## How it Works
This is the chunk of code inside `include_docx_template()` that lets you pass kwargs to the subdocument as DAObjects & strings:
```python
for key, val in kwargs.items():
    if hasattr(val, 'instanceName'):
        the_repr = val.instanceName
    else:
        the_repr = '_codecs.decode(_array.array("b", "' + re.sub(r'\n', '', codecs.encode(bytearray(val, encoding='utf-8'), 'base64').decode()) + '".encode()), "base64").decode()'
    first_paragraph.insert_paragraph_before(str("{%%p set %s = %s %%}" % (key, the_repr)))
```
The only change this module makes to the code is adding two lines to the if statement:
```python
elif isinstance(val, bool):
    the_repr = val
```
