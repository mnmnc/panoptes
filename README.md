panoptes
========

Panoptes (Ancient Greek: Πανόπτης; English translation: "the all-seeing")

### What it it?
Operating system integrity checks made easy.

### How does it work?
This is a python script that parses 

### Capabilities:
```
usage: panoptes.py [-h] [-v] [-d] [-o]
                   [-p [additional_paths [additional_paths ...]]]

panoptes.py [-v | --verbose | -s | --silent | -p | --paths ]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Show output for files that passed the integrity check.
  -d, --details         Show detailed output for files that failed integrity
                        check.
  -o, --override        This forces the creation of new database if some files
                        will generate new hash values.
  -p [additional_paths [additional_paths ...]], --path [additional_paths [additional_paths ...]]
                        Include additional paths.
```

### TODO
  - multi-threading support
  - logo
  - stats per path
  - oop
