#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
QueryNCBI: A Python module for the NCBI API
Author: https://github.com/liqiming-whu
'''
import re
import argparse
from datetime import date
import pandas as pd
from Bio import Entrez, Medline


Entrez.email = "liqiming1914658215@gmail.com"                                      
Entrez.api_key = "c80ce212c7179f0bbfbd88495a91dd356708"


class QueryNCBI:
    __slots__ = ['keywords', 'mesh_topic', 'journal', 'year', 'from_date', 'to_date', 'retmax', 'db', 'count', 'idlist']
    def __init__(self, keywords=None, mesh_topic=None, journal=None, year=None, from_date=None, to_date=date.today().strftime("%Y/%m/%d"), retmax=1000, db="pubmed"):
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
        print(self)

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
    def get_pubmed_detail(cls, idlist):
        id_count = len(idlist)
        idlists = [idlist[i:i+10000] for i in range(0,id_count, 10000)] if id_count > 10000 else [idlist]
        i = 0
        for ids in idlists:
            handle = Entrez.efetch(db="pubmed", id=ids, rettype="medline", retmode="text")
            records = Medline.parse(handle)
            for record in records:
                i += 1
                pmid = record.get("PMID", "?")
                print(f"Download {pmid} {i}/{id_count}")
                title = record.get("TI", "?")
                abstract = record.get("AB", "?")
                authors = ", ".join(record.get("AU", "?"))
                journal = record.get("TA", "?")
                pub_date = record.get("DP", "?")
                source = record.get("SO", "?")
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
                yield pmid, title, abstract, authors, journal, pub_date, source, url
    
    @classmethod
    def download_pubmed_detail(cls, idlist, path):
        data = []
        for record in cls.get_pubmed_detail(idlist):
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

    def download_pubmed_results(self, path):
        self.download_pubmed_detail(self.idlist, path)

    @classmethod
    def get_geo_summaries(cls, idlist):
        count = len(idlist)
        i = 0
        for id in idlist:
            i += 1
            print(f"Download {id} {i}/{count}")
            try:
                handle = Entrez.esummary(db="gds", id=id)
                record = Entrez.read(handle)[0]
            except Exception:
                print(f"{id} connect error")
                continue
            gse = record.get("Accession", "?")
            title = record.get("title", "?")
            summary = record.get("summary", "?")
            species = record.get("taxon", "?")
            date = record.get("PDAT", "?")
            samples = [i['Accession'] for i in record.get("Samples", [])]
            pmids = [int(i) for i in record.get("PubMedIds", [])]
            url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse}"
            yield id, gse, title, summary, species, date, samples, pmids, url

    @classmethod
    def download_geo_summaries(cls, idlist, path):
        data = []
        for record in cls.get_geo_summaries(idlist):
            id, gse, title, summary, species, date, samples, pmids, url = record
            data.append({
                "ID": id,
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

    def download_geo_results(self, path):
        self.download_geo_summaries(self.idlist, path)
        

def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-q", "--query", dest="query",
                        type=str, required=True, help="input keywords")
    parser.add_argument("-o", "--output", dest="output_file", type=str, default=None,
                        help="Output file")
    parser.add_argument("-y", "--year", dest="year", type=str, default=None,
                        help="year")
    parser.add_argument("-f", "--from_date", dest="from_date", type=str, default=None,
                        help="from_date")
    parser.add_argument("-t", "--to_date", dest="to_date", type=str, default=date.today().strftime("%Y/%m/%d"),
                        help="to_date")
    parser.add_argument("-r", "--retmax", dest="retmax", type=int, default=1000,
                        help="retmax")
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
        retmax=args.retmax
        )
    if args.output:
        query.download_pubmed_results(args.output)


def run_geo():
    parser = parse_args()
    args = parser.parse_args()
    query = QueryNCBI(
        keywords=args.query,
        year=args.year,
        from_date=args.from_date,
        to_date=args.to_date,
        retmax=args.retmax,
        db="gds"
        )
    if args.output:
        query.download_geo_results(args.output)


if __name__ == "__main__":
    run_pubmed()