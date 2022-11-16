# queryncbi

## Usage

```shell
usage: search_pubmed [-h] -q QUERY [-o OUTPUT] [-y YEAR] [-f FROM_DATE] [-t TO_DATE] [-r RETMAX] [--log LOG] [--threads THREADS] [-j JOURNAL] [-m MESH]

QueryNCBI: A Python module for the NCBI API Author: https://github.com/liqiming-whu

optional arguments:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        input keywords (default: None)
  -o OUTPUT, --output OUTPUT
                        Output file (default: None)
  -y YEAR, --year YEAR  year (default: None)
  -f FROM_DATE, --from_date FROM_DATE
                        from_date (default: None)
  -t TO_DATE, --to_date TO_DATE
                        to_date (default: today)
  -r RETMAX, --retmax RETMAX
                        retmax (default: 1000)
  --log LOG             log file (default: None)
  --threads THREADS     threads (default: 20)
  -j JOURNAL, --journal JOURNAL
                        journal (default: None)
  -m MESH, --mesh_topic MESH
                        mesh topic (default: None)


usage: search_geo [-h] -q QUERY [-o OUTPUT] [-y YEAR] [-f FROM_DATE] [-t TO_DATE] [-r RETMAX] [--log LOG] [--threads THREADS] [--filter-species FILTER_SPECIES [FILTER_SPECIES ...]] [--filter-pmids]

QueryNCBI: A Python module for the NCBI API Author: https://github.com/liqiming-whu

optional arguments:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        input keywords (default: None)
  -o OUTPUT, --output OUTPUT
                        Output file (default: None)
  -y YEAR, --year YEAR  year (default: None)
  -f FROM_DATE, --from_date FROM_DATE
                        from_date (default: None)
  -t TO_DATE, --to_date TO_DATE
                        to_date (default: today)
  -r RETMAX, --retmax RETMAX
                        retmax (default: 1000)
  --log LOG             log file (default: None)
  --threads THREADS     threads (default: 20)
  --filter-species FILTER_SPECIES [FILTER_SPECIES ...]
                        filter species (default: None)
  --filter-pmids        filter pmids (default: False)
```