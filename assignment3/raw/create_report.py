"""Generate the Exercise 3.1 report from measured CSV files only.

From the repository root:
  python assignment3/raw/create_report.py
Dependencies: matplotlib, reportlab, pymupdf (PDF preview only).
"""
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.tools' / 'report-python'))
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'tmp' / 'pdfs' / 'mpl'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
)
from reportlab.lib.pagesizes import A4
from xml.sax.saxutils import escape

OUT = ROOT / 'output' / 'pdf'
FIG = OUT / 'figures'
FIG.mkdir(parents=True, exist_ok=True)
OLD = ROOT / 'assignment2/final/gpu15_ex2/pcie_results.csv'
CURRENT = ROOT / 'assignment3/data/template/results/pcie_results.csv'


def load(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row['bytes'] = int(row['bytes'])
        for key in ('gbps', 'time_ms'):
            row[key] = float(row[key])
        expected = row['bytes'] / (row['time_ms'] / 1000) / 1e9
        assert abs(expected - row['gbps']) / row['gbps'] < 0.0001
    assert len({(r['bytes'], r['memory'], r['direction']) for r in rows}) == len(rows)
    return rows


old, current = load(OLD), load(CURRENT)
assert len(current) == 44
assert not any(r['direction'] == 'D2D' for r in current)
series = [('pageable', 'H2D'), ('pageable', 'D2H'), ('pinned', 'H2D'), ('pinned', 'D2H')]
palette = ['#61829a', '#a4b4c0', '#007d83', '#dd8d25']
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False,
                     'axes.spines.right': False, 'font.family': 'DejaVu Sans'})

fig, ax = plt.subplots(figsize=(9, 3.6), layout='constrained')
for (memory, direction), color in zip(series, palette):
    points = sorted((r for r in current if (r['memory'], r['direction']) == (memory, direction)), key=lambda r: r['bytes'])
    ax.plot([r['bytes'] for r in points], [r['gbps'] for r in points],
            marker='o', ms=4, lw=2, color=color, label=f'{direction} {memory}')
ax.set_xscale('log', base=4)
ax.set_xticks([1024, 16384, 262144, 4194304, 67108864, 1073741824],
              ['1 KiB', '16 KiB', '256 KiB', '4 MiB', '64 MiB', '1 GiB'])
ax.set(xlabel='Dimensione del trasferimento', ylabel='Banda effettiva [GB/s]', ylim=(0, 15))
ax.grid(alpha=.2)
ax.legend(ncol=2, loc='upper left', frameon=False)
fig.savefig(FIG / 'banda_output.png', dpi=220)
fig.savefig(FIG / 'banda_output.svg')
plt.close(fig)


def endpoint(rows, key):
    return next(r['gbps'] for r in rows if r['bytes'] == 1073741824 and (r['memory'], r['direction']) == key)


before = [endpoint(old, key) for key in series]
after = [endpoint(current, key) for key in series]
fig, ax = plt.subplots(figsize=(9, 3), layout='constrained')
x = list(range(4))
bars1 = ax.bar([v - .18 for v in x], before, width=.36, color='#a4b4c0', label='Output esercizio 2.3')
bars2 = ax.bar([v + .18 for v in x], after, width=.36, color='#007d83', label='Output disponibile in assignment3')
ax.bar_label(bars1, fmt='%.2f', fontsize=9, padding=3)
ax.bar_label(bars2, fmt='%.2f', fontsize=9, padding=3)
ax.set_xticks(x, ['H2D pageable', 'D2H pageable', 'H2D pinned', 'D2H pinned'])
ax.set(ylabel='Banda effettiva a 1 GiB [GB/s]', ylim=(0, 16))
ax.legend(loc='upper left', ncol=2, frameon=False, fontsize=9)
ax.grid(axis='y', alpha=.2)
ax.set_axisbelow(True)
fig.savefig(FIG / 'confronto_precedente.png', dpi=220)
fig.savefig(FIG / 'confronto_precedente.svg')
plt.close(fig)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle', fontName='Helvetica-Bold', fontSize=21,
                         leading=25, textColor=colors.HexColor('#17394b'), spaceAfter=9))
styles.add(ParagraphStyle(name='SectionTitle', fontName='Helvetica-Bold', fontSize=11.5,
                         leading=15, textColor=colors.HexColor('#007d83'), spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name='ReportBody', fontName='Helvetica', fontSize=9.5,
                         leading=13, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='CaptionSmall', fontName='Helvetica', fontSize=8,
                         leading=11, textColor=colors.HexColor('#536875'), spaceAfter=7))

story, markdown = [], []


def text(content, kind='ReportBody'):
    story.append(Paragraph(content, styles[kind]))
    prefix = '# ' if kind == 'ReportTitle' else '## ' if kind == 'SectionTitle' else ''
    markdown.append(prefix + content.replace('<b>', '**').replace('</b>', '**').replace('<br/>', '\n') + '\n')


def chart(name, height, caption):
    story.append(Image(str(FIG / name), width=495, height=height))
    text(caption, 'CaptionSmall')
    markdown.append(f'![{caption}](figures/{name})\n')


text('Esercizio 3.1 | Global Memory', 'ReportTitle')
text('cudaMemcpy: estensione D2D e confronto con i trasferimenti host-device', 'CaptionSmall')
text('Obiettivo e stato dei risultati', 'SectionTitle')
text("L'esercizio estende il benchmark 2.3 aggiungendo copie tra due buffer della stessa GPU. "
     "<b>Il codice aggiornato implementa D2D, ma gli output disponibili non contengono ancora questa misura.</b> "
     "Il CSV in assignment3 include 44 righe: 11 dimensioni e quattro condizioni H2D/D2H. "
     "Il log associato identifica una NVIDIA GeForce RTX 2080 Ti e conferma quattro condizioni per dimensione.")
text('La nuova parte: misura D2D', 'SectionTitle')
text("Il buffer deviceDestination viene allocato con cudaMalloc, oltre al buffer device esistente. "
     "La chiamata cudaMemcpy(deviceDestination, device, N, cudaMemcpyDeviceToDevice) copia N byte "
     "tra due allocazioni sul dispositivo corrente. Il test D2D viene eseguito una sola volta per dimensione, "
     "fuori dai cicli pageable/pinned, poiche' non coinvolge memoria host.")
text("La funzione di misura riceve sorgente e destinazione esplicite, esegue tre copie di warmup, "
     "poi cronometra n copie con steady_clock. Ogni copia e' seguita da cudaDeviceSynchronize: "
     "D2D non garantisce un'attesa lato host al ritorno di cudaMemcpy. La metrica e' "
     "<b>B = N / (t_medio x 10^9) GB/s</b>, con t_medio = T_totale / n. "
     "Il tempo include API e sincronizzazione; allocazione, inizializzazione e warmup sono esclusi.")
text('Dati di output attualmente disponibili', 'SectionTitle')
chart('banda_output.png', 198,
      'Figura 1. CSV presente in assignment3: banda in funzione della dimensione, asse x logaritmico. Nessuna curva D2D e\' disponibile.')
text("Le dimensioni aumentano di un fattore quattro da 1 KiB a 1 GiB. Le ripetizioni misurate "
     "sono 1000, 200, 30, 8 o 4, secondo la dimensione. La banda cresce inizialmente "
     "perche' gli overhead vengono ammortizzati su piu' byte, poi tende a un plateau.")

story.append(PageBreak())
text('Risultati e interpretazione', 'ReportTitle')
text('Richiamo del 2.3 e implicazioni per il nuovo confronto D2D', 'CaptionSmall')
chart('confronto_precedente.png', 165,
      'Figura 2. Confronto a 1 GiB tra output del 2.3 e output disponibile in assignment3. Sono due dataset host-device, non un confronto con D2D.')

text('Risultati host-device', 'SectionTitle')
table_data = [['Condizione', '2.3 [GB/s]', 'CSV assignment3 [GB/s]']]
for i, (memory, direction) in enumerate(series):
    table_data.append([f'{direction} {memory}', f'{before[i]:.2f}', f'{after[i]:.2f}'])
table = Table(table_data, colWidths=[165, 130, 200], hAlign='LEFT')
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#17394b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ('TOPPADDING', (0, 0), (-1, -1), 7),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#edf3f5'), colors.white]),
    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
]))
markdown.append('| Condizione | 2.3 [GB/s] | CSV assignment3 [GB/s] |\n|---|---:|---:|\n' + '\n'.join('| ' + ' | '.join(row) + ' |' for row in table_data[1:]) + '\n')
gain_h2d = (after[2] / after[0] - 1) * 100
gain_d2h = (after[3] / after[1] - 1) * 100
text(f"Nel CSV di assignment3, a 1 GiB, la memoria pinned migliora la banda di circa {gain_h2d:.1f}% "
     f"in H2D e {gain_d2h:.1f}% in D2H rispetto alla pageable. Con pageable, H2D e' piu' veloce "
     "di D2H; con pinned, D2H e' leggermente piu' veloce. Le differenze rispetto al vecchio "
     "dataset sono inferiori al 1.5% a questa dimensione; non sono stime di significativita' statistica.")
text("Il vantaggio pinned e' piu' evidente a 1 MiB: circa 12.00 contro 7.15 GB/s in H2D e "
     "12.51 contro 5.77 GB/s in D2H. A 1 KiB, invece, pageable H2D supera pinned H2D "
     "(0.169 contro 0.147 GB/s): gli overhead dominano e pinned non e' sempre piu' veloce.")
text("Definendo il plateau come il primo punto entro il 5% del valore a 1 GiB, le curve pinned "
     "vi entrano a 4 MiB; le pageable a 16 MiB. Da 64 MiB la banda cambia poco. "
     "La memoria pinned facilita i trasferimenti DMA; il diverso percorso di staging e gli overhead "
     "possono contribuire alle differenze, ma i soli tempi non ne isolano la causa.")
text('Come completare il risultato nuovo', 'SectionTitle')
text("Occorre rieseguire il codice aggiornato e ottenere <b>55 righe di dati: 11 dimensioni x 5 condizioni</b>. "
     "Il grafico finale dovra' aggiungere la curva D2D alle quattro host-device della stessa esecuzione. "
     "Si prevede una banda D2D maggiore per trasferimenti grandi, poiche' la copia rimane sulla GPU, "
     "ma non e' ancora una conclusione misurata. La metrica usa N/t; il conteggio logico "
     "letture piu' scritture per D2D sarebbe 2N/t.")
text("Il vecchio codice sincronizza a fine batch, quello aggiornato dopo ogni copia: gli output presenti "
     "non dimostrano l'esecuzione della versione aggiornata. Per il confronto definitivo usare "
     "un unico metodo di timing. Le copie riutilizzano gli stessi buffer e non sono disponibili "
     "barre d'errore o verifiche esplicite del contenuto copiato.")
text('Fonti e riproducibilita\'', 'SectionTitle')
text('Dati: assignment2/final/gpu15_ex2/pcie_results.csv; '
     'assignment3/data/template/results/pcie_results.csv e pcie_output.txt. '
     'Codice nuovo: assignment3/raw/pcie_benchmark.cu. '
     'Riferimenti: NVIDIA CUDA Runtime API, API Synchronization Behavior; '
     'CUDA C++ Best Practices Guide, Pinned Memory. '
     'Grafici generati direttamente dai CSV con create_report.py.', 'CaptionSmall')


def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#ccd8df'))
    canvas.line(50, 39, A4[0] - 50, 39)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#536875'))
    canvas.drawString(50, 26, 'GPU Computing | Esercizio 3.1 | Report sui dati disponibili')
    canvas.drawRightString(A4[0] - 50, 26, str(doc.page))


pdf_path = OUT / 'report_esercizio_3_1.pdf'
doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=50, leftMargin=50,
                        topMargin=35, bottomMargin=50, title='Esercizio 3.1 - cudaMemcpy',
                        author='GPU Computing - gruppo 15')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
(OUT / 'report_esercizio_3_1.md').write_text('\n'.join(markdown), encoding='utf-8')

import pymupdf
preview_dir = ROOT / 'tmp' / 'pdfs'
preview_dir.mkdir(parents=True, exist_ok=True)
with pymupdf.open(pdf_path) as pdf:
    assert len(pdf) == 2, f'Expected 2 pages, got {len(pdf)}'
    for i, page in enumerate(pdf):
        page.get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4)).save(preview_dir / f'report_3_1_page_{i+1}.png')
print(f'Created {pdf_path} (2 pages); CSV values verified against time_ms.')
