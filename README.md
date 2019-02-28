# cuc_parse
Acest program parsează documente ce conțin întrebari de ”Ce? Unde? Când?”.

# Instalare
Primul past este executarea scirptului "setup.sh". Acest script creaza dosarele necesare, descară toate documentele de pe http://www.cuc.md/content/blogcategory/163/187/lang,ro/ și le convertește în format text.

```
git clone https://github.com/shervlad/cuc_parse
cd cuc_parse
sh setup.sh
```

# Parser
Implementarea parserului este în _block_parser.py_
Pentru a parsa toate fișierele:
```
python block_parser.py all
```
Pentru a parsa un singur fisier:
```
python block_parser.py <num_fisier>
```
