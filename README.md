# queryncbi

## Usage

```shell
usage: search_pubmed [-h] -q QUERY [-o OUTPUT_FILE] [-y YEAR] [-f FROM_DATE] [-t TO_DATE] [-r RETMAX] [-j JOURNAL] [-m MESH]

QueryNCBI: A Python module for the NCBI API Author: https://github.com/liqiming-whu

options:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        input keywords (default: None)
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Output file (default: None)
  -y YEAR, --year YEAR  year (default: None)
  -f FROM_DATE, --from_date FROM_DATE
                        from_date (default: None)
  -t TO_DATE, --to_date TO_DATE
                        to_date (default: 2022/04/07)
  -r RETMAX, --retmax RETMAX
                        retmax (default: 1000)
  -j JOURNAL, --journal JOURNAL
                        journal (default: None)
  -m MESH, --mesh_topic MESH
                        mesh topic (default: None)


usage: search_geo [-h] -q QUERY [-o OUTPUT_FILE] [-y YEAR] [-f FROM_DATE] [-t TO_DATE] [-r RETMAX]

QueryNCBI: A Python module for the NCBI API Author: https://github.com/liqiming-whu

options:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        input keywords (default: None)
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Output file (default: None)
  -y YEAR, --year YEAR  year (default: None)
  -f FROM_DATE, --from_date FROM_DATE
                        from_date (default: None)
  -t TO_DATE, --to_date TO_DATE
                        to_date (default: 2022/04/07)
  -r RETMAX, --retmax RETMAX
                        retmax (default: 1000)
```