"""Download the age-of-acquisition norms from the publisher and write data/aoa-{es,en}.tsv (word<TAB>years).

The publisher's file server rejects plain HTTP clients, so the files are fetched through headless Chromium.
Run: uv run --with playwright --with openpyxl python fetch_norms.py
"""
import asyncio, io, os, zipfile
import openpyxl
from playwright.async_api import async_playwright

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ESM = "https://media.springernature.com/original/springer-static/esm/art%3A10.3758%2F{doi}/MediaObjects/{name}"
SPANISH = ESM.format(doi="s13428-014-0454-2", name="13428_2014_454_MOESM1_ESM.zip")  # Alonso et al. 2015
ENGLISH = ESM.format(doi="s13428-013-0348-8", name="13428_2013_348_MOESM1_ESM.xlsx")  # Kuperman et al. 2012, erratum file

async def download(urls):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://link.springer.com/", wait_until="domcontentloaded")
        bodies = []
        for url in urls:
            response = await page.request.get(url)
            if not response.ok:
                raise SystemExit(f"{url}: HTTP {response.status}")
            bodies.append(await response.body())
        await browser.close()
        return bodies

def spanish(blob):
    # SpanishAoA.txt is UTF-16 with columns word, averageAoA, SD, Min, Max, ...; ratings are years, 11 meaning 11 or older.
    text = zipfile.ZipFile(io.BytesIO(blob)).read("SpanishAoA.txt").decode("utf-16")
    rows = [line.split("\t") for line in text.splitlines()[1:]]
    return [(r[0].strip().lower(), float(r[1])) for r in rows if len(r) > 1 and r[1].strip()]

def english(blob):
    # Columns Word, OccurTotal, OccurNum, Freq_pm, Rating.Mean, Rating.SD, Dunno; ratings are years.
    sheet = openpyxl.load_workbook(io.BytesIO(blob), read_only=True).active
    rows = list(sheet.iter_rows(values_only=True))[1:]
    return [(str(r[0]).lower(), float(r[4])) for r in rows if r[0] and isinstance(r[4], (int, float))]

def main():
    es, en = asyncio.run(download([SPANISH, ENGLISH]))
    os.makedirs(DATA, exist_ok=True)
    for lang, pairs in (("es", spanish(es)), ("en", english(en))):
        with open(f"{DATA}/aoa-{lang}.tsv", "w") as f:
            f.writelines(f"{w}\t{a:.2f}\n" for w, a in pairs)
        print(f"aoa-{lang}.tsv: {len(pairs)} words")

if __name__ == "__main__":
    main()
