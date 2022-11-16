#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
QueryNCBI: A Python module for the NCBI API
Author: https://github.com/liqiming-whu
'''
import re
import argparse
import logging
import pandas as pd
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from Bio import Entrez, Medline

Entrez.email = "liqiming1914658215@gmail.com"                                      
Entrez.api_key = "c80ce212c7179f0bbfbd88495a91dd356708"


class QueryNCBI:
    __slots__ = ['keywords', 'mesh_topic', 'journal', 'year', 'from_date', 'to_date', 'retmax', 'db', 'count', 'idlist', 'threads']
    def __init__(self, keywords=None, mesh_topic=None, journal=None, year=None, from_date=None, to_date=date.today().strftime("%Y/%m/%d"), retmax=1000, db="pubmed", log=None, threads=20):
        self.keywords = keywords
        self.mesh_topic = mesh_topic
        self.journal = journal
        self.year = year
        self.from_date = from_date
        self.to_date = to_date
        assert any(getattr(self, i) for i in self.__slots__[:5]), "At least one parameter is required."
        self.retmax = retmax
        self.db = db
        self.count = self.get_count()
        self.idlist = self.search()
        self.threads = threads
        logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", datefmt='%Y-%m-%d %A %H:%M:%S', level=logging.INFO, filename=log)
        logging.info(str(self))

    def __repr__(self):
        return f"Search '{self.query}', get {self.count} results."

    __str__ = __repr__

    @property
    def query(self):
        query_list = []
        if self.keywords:
            query_list.append(self.keywords)
        if self.mesh_topic:
            query_list.append(f"{self.mesh_topic}[MeSH Major Topic]")
        if self.journal:
            query_list.append(f"{self.journal}[ta]")
        if self.from_date:
            assert re.compile("\d{4}\/\d{2}\/\d{2}").match(self.from_date), "Date error, fromat: YYYY/MM/DD"
            assert re.compile("\d{4}\/\d{2}\/\d{2}").match(self.to_date), "Date error, fromat: YYYY/MM/DD"
            self.year = None
            query_list.append(f"{self.from_date}: {self.to_date}[dp]")
        if self.year:
            query_list.append(f"{self.year}[dp]")
        
        return " AND ".join(query_list)

    def get_count(self):
        handle = Entrez.egquery(term=self.query)
        record = Entrez.read(handle)
        for row in record["eGQueryResult"]:
            if row["DbName"] == self.db:
                count = row["Count"]
        return count
        
    def search(self):                                                           
       handle = Entrez.esearch(db=self.db, term=self.query, retmax=self.retmax)
       record = Entrez.read(handle)                                            
       return record["IdList"]
    
    @classmethod
    def get_pubmed_detail(cls, idlist, threads=20):
        def fetch_task(id, i, count):
            logging.info(f"Fetching {i*10000}-{i*10000+len(id)}/{count}...")
            try:
                handle = Entrez.efetch(db="pubmed", id=id, rettype="medline", retmode="text")
                record = Medline.read(handle)
            except Exception as e:
                logging.warning(f"{i*10000}-{i*10000+len(id)}/{count} Expection: {e}")
                record = None
            return record
        
        id_count = len(idlist)
        idlists = [idlist[i:i+10000] for i in range(0,id_count, 10000)] if id_count > 10000 else [idlist]
        workers = min(threads, len(idlists))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            task_quene = [executor.submit(fetch_task, ids, i, id_count) for i, ids in enumerate(idlists)]
            i = 0
            for task in as_completed(task_quene):
                records = task.result()
                if records is None:
                    continue
                for record in records:
                    i += 1
                    pmid = record.get("PMID", "?")
                    logging.info(f"Download {pmid} {i}/{id_count}")
                    title = record.get("TI", "?")
                    abstract = record.get("AB", "?")
                    authors = ", ".join(record.get("AU", "?"))
                    journal = record.get("TA", "?")
                    pub_date = record.get("DP", "?")
                    source = record.get("SO", "?")
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
                    yield pmid, title, abstract, authors, journal, pub_date, source, url
    
    @classmethod
    def download_pubmed_detail(cls, idlist, path, threads=20):
        data = []
        for record in cls.get_pubmed_detail(idlist, threads):
            pmid, title, abstract, au, jour, date, source, url = record
            data.append({
                "PubMed_ID": pmid,
                "Title": title,
                "Abstract": abstract,
                "Authors": au,
                "Journal": jour,
                "Pub_date": date,
                "Source": source,
                "HTTP_Link": url
            })
        df = pd.DataFrame(data)
   
        if path.endswith(".tsv"):
            df.to_csv(path, sep="\t")
        elif path.endswith(".xlsx") or path.endswith(".xls"):
            df.to_excel(path)
        else:
            df.to_csv(path)
        logging.info(f"save {df.shape[0]} records to {path}.")

    def download_pubmed_results(self, path):
        self.download_pubmed_detail(self.idlist, path, self.threads)

    @classmethod
    def get_geo_summaries(cls, idlist, threads=20):
        def fetch_task(id, i, count):
            logging.info(f"Download {id} {i}/{count}")
            try:
                handle = Entrez.esummary(db="gds", id=id)
                record = Entrez.read(handle)[0]
            except Exception as e:
                logging.warning(f"{id} Exception: {e}")
                record = None
            return record
        count = len(idlist)
        with ThreadPoolExecutor(max_workers=threads) as executor:
            task_quene = [executor.submit(fetch_task, id, i+1, count) for i, id in enumerate(idlist)]
            def iter_resluts():
                ite = as_completed(task_quene, timeout=60)
                i = 0
                while True:
                    i += 1
                    try:
                        yield next(ite).result()
                    except TimeoutError:
                        logging.warning(f"{idlist[i-1]} timeout.")
                        continue
                    except StopIteration:
                        break
            for record in iter_resluts():
                if record is None:
                    continue
                gse = record.get("Accession", "?")
                title = record.get("title", "?")
                summary = record.get("summary", "?")
                species = record.get("taxon", "?")
                date = record.get("PDAT", "?")
                samples = ",".join(i['Accession'] for i in record.get("Samples", []))
                pmids = ",".join(str(int(i)) for i in record.get("PubMedIds", []))
                url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse}"
                yield gse, title, summary, species, date, samples, pmids, url

    @classmethod
    def download_geo_summaries(cls, idlist, path, filter_specise=None, filter_pmids=False, threads=20):
        data = []
        if filter_specise is not None:
            filter_specise = re.compile("|".join(filter_specise))
        for record in cls.get_geo_summaries(idlist, threads):
            gse, title, summary, species, date, samples, pmids, url = record
            if filter_specise is not None and not filter_specise.search(species):
                logging.info(f"{gse} {species} not in {filter_specise.pattern}, skip")
                continue
            if filter_pmids and not pmids:
                logging.info(f"{gse} no pmids, skip")
                continue
            data.append({
                "GSE": gse,
                "Title": title,
                "Summary": summary,
                "Species": species,
                "Date": date,
                "Samples": samples,
                "PMIDS": pmids,
                "HTTP_Link": url
            })
        df = pd.DataFrame(data)
        if path.endswith(".tsv"):
            df.to_csv(path, sep="\t")
        elif path.endswith(".xlsx") or path.endswith(".xls"):
            df.to_excel(path)
        else:
            df.to_csv(path)
        logging.info(f"save {df.shape[0]} records to {path}.")

    def download_geo_results(self, path, filter_specise=None, filter_pmids=False):
        self.download_geo_summaries(self.idlist, path, filter_specise=filter_specise, filter_pmids=filter_pmids, threads=self.threads)
        

def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-q", "--query", dest="query",
                        type=str, required=True, help="input keywords")
    parser.add_argument("-o", "--output", dest="output", type=str, default=None,
                        help="Output file")
    parser.add_argument("-y", "--year", dest="year", type=str, default=None,
                        help="year")
    parser.add_argument("-f", "--from_date", dest="from_date", type=str, default=None,
                        help="from_date")
    parser.add_argument("-t", "--to_date", dest="to_date", type=str, default=date.today().strftime("%Y/%m/%d"),
                        help="to_date")
    parser.add_argument("-r", "--retmax", dest="retmax", type=int, default=1000,
                        help="retmax")
    parser.add_argument("--log", dest="log", type=str, default=None, help="log file")
    parser.add_argument("--threads", dest="threads", type=int, default=20, help="threads")
    return parser


def run_pubmed():
    parser = parse_args()
    parser.add_argument("-j", "--journal", dest="journal", type=str, default=None,
                        help="journal")
    parser.add_argument("-m", "--mesh_topic", dest="mesh", type=str, default=None,
                        help="mesh topic")
    args = parser.parse_args()
    query = QueryNCBI(
        keywords=args.query,
        mesh_topic=args.mesh,
        journal=args.journal,
        year=args.year,
        from_date=args.from_date,
        to_date=args.to_date,
        retmax=args.retmax,
        log=args.log,
        threads=args.threads
        )
    if args.output:
        query.download_pubmed_results(args.output)


def run_geo():
    parser = parse_args()
    parser.add_argument("--filter-species", dest="filter_species", nargs="+", type=str, default=None, help="filter species")
    parser.add_argument("--filter-pmids", dest="filter_pmids", action="store_true", default=False, help="filter pmids")
    args = parser.parse_args()
    query = QueryNCBI(
        keywords=args.query,
        year=args.year,
        from_date=args.from_date,
        to_date=args.to_date,
        retmax=args.retmax,
        db="gds",
        log=args.log,
        threads=args.threads
        )
    if args.output:
        query.download_geo_results(args.output, args.filter_species, args.filter_pmids)


if __name__ == "__main__":
    run_pubmed()