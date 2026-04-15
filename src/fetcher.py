import os
import time
import argparse
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from src.config import DOCS_PATH

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_NS  = "{http://www.w3.org/2005/Atom}"

def search_arxiv(topic: str, max_results: int = 5) -> list:
    params = urllib.parse.urlencode({
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_API}?{params}"
    print(f"Searching arXiv for: '{topic}'")
    with urllib.request.urlopen(url) as r:
        xml_data = r.read()
    return _parse(xml_data)

def fetch_by_ids(arxiv_ids: list) -> list:
    params = urllib.parse.urlencode({
        "id_list": ",".join(arxiv_ids),
        "max_results": len(arxiv_ids),
    })
    url = f"{ARXIV_API}?{params}"
    print(f"Fetching {len(arxiv_ids)} papers by ID")
    with urllib.request.urlopen(url) as r:
        xml_data = r.read()
    return _parse(xml_data)

def _parse(xml_data: bytes) -> list:
    root   = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall(f"{ARXIV_NS}entry"):
        raw_id   = entry.find(f"{ARXIV_NS}id").text.strip()
        arxiv_id = raw_id.split("/abs/")[-1].replace("/", "_")
        title    = entry.find(f"{ARXIV_NS}title").text.strip().replace("\n", " ")
        summary  = entry.find(f"{ARXIV_NS}summary").text.strip().replace("\n", " ")
        authors  = [
            a.find(f"{ARXIV_NS}name").text
            for a in entry.findall(f"{ARXIV_NS}author")
        ]

        pdf_url = None
        for link in entry.findall(f"{ARXIV_NS}link"):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib["href"]
                break
        if not pdf_url:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"

        papers.append({
            "id":      arxiv_id,
            "title":   title,
            "authors": authors,
            "summary": summary,
            "pdf_url": pdf_url,
        })

    print(f"Found {len(papers)} papers")
    return papers

def download_papers(papers: list, save_dir: str = DOCS_PATH) -> list:
    os.makedirs(save_dir, exist_ok=True)
    saved = []

    for paper in papers:
        fname     = _safe_name(paper["title"]) + ".pdf"
        file_path = Path(save_dir) / fname

        if file_path.exists():
            print(f"Already exists, skipping: {fname}")
            saved.append(str(file_path))
            continue

        print(f"Downloading: {paper['title'][:70]}")
        try:
            req = urllib.request.Request(
                paper["pdf_url"],
                headers={"User-Agent": "RAGCopilot/1.0 (portfolio project)"}
            )
            with urllib.request.urlopen(req) as r:
                data = r.read()
            with open(file_path, "wb") as f:
                f.write(data)
            print(f"  Saved to: {file_path}")
            saved.append(str(file_path))
            time.sleep(1.5)
        except Exception as e:
            print(f"  Failed: {e}")

    return saved

def _safe_name(title: str) -> str:
    s = title.lower().replace(" ", "_")
    s = "".join(c for c in s if c.isalnum() or c in "_-")
    return s[:80]


def print_papers(papers: list) -> None:
    print("\n" + "="*60)
    for i, p in enumerate(papers, 1):
        print(f"\n[{i}] {p['title']}")
        print(f"    Authors : {', '.join(p['authors'][:3])}")
        print(f"    Abstract: {p['summary'][:150]}...")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch papers from arXiv")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--topic", type=str,
                       help='e.g. "retrieval augmented generation"')
    group.add_argument("--ids",   type=str, nargs="+",
                       help="arXiv IDs e.g. 1706.03762 1810.04805")
    parser.add_argument("--max",        type=int, default=5)
    parser.add_argument("--list-only",  action="store_true")
    args = parser.parse_args()

    papers = search_arxiv(args.topic, args.max) if args.topic else fetch_by_ids(args.ids)
    print_papers(papers)

    if not args.list_only and papers:
        paths = download_papers(papers)
        print(f"\nDownloaded {len(paths)} PDFs into {DOCS_PATH}")
        print("Next: python -m src.ingest")