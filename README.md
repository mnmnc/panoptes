mpanoptes
========
Multithreaded Panoptes - a version of the script designed for concurrency.

Well this is utter failure since even when executed concurrently those operations will not run faster than in a sequential version of the script. What a shame.
Writing it was fun tho :)

### Usage

```
usage: mpanoptes.py [-h] [-v] [-d] [-o] [-p [path [path ...]]] [-t THREADS]
                    [-w database_file]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Show output for files that passed the integrity check.
  -d, --details         Show detailed output for files that failed integrity
                        check.
  -o, --override        This forces the creation of new database if some files
                        will generate new hash values.
  -p [path [path ...]], --path [path [path ...]]
                        Include additional paths.
  -t THREADS, --threads THREADS
                        Specify number of threads prefered. By default a CPU
                        detection is being used to determine the optimal
                        value.
  -w database_file, --write database_file
                        Specify different database file. If nonexistent it
                        will be created.
```
