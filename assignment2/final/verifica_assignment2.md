# Verifica finale - Assignment 2

Gruppo 15: Michele Arrigoni, Francesco Foresti, Kasra Ghasemipoo, Karol Bonat.
Disponibilita alla presentazione: tutti gli esercizi, 2.1, 2.2 e 2.3.

## Esito

Il materiale necessario e presente. Il PDF unico e `output/pdf/assignment2_report.pdf`.
L'archivio di consegna e `assignment2/final/gpu15_ex2.zip`, con cartella radice `gpu15_ex2/`.
L'archivio contiene sorgenti, dipendenza chTimer.h, Makefile, tre script Slurm, dati originali,
plotter, grafici PNG/SVG, README e un unico report PDF. Non contiene eseguibili o vecchie bozze.

## Dati verificati

- Es2.1, job 279658: confronto base asincrono 5.55 us e sincrono 6.04 us; sorgente aggiornato a 100000 iterazioni.
- Es2.1, job 279659: tutte le 165 combinazioni uniche, 15 valori di griglia e 11 di blocco. Tempi asincroni e sincroni presenti. Grafici aggiornati per usare entrambe le colonne.
- Es2.2, job 279660: 76 punti, da zero a 7500 cicli con passo 100. Baseline 2.681958350 us, soglia 5.363916700 us; 7400 cicli ancora sotto soglia, 7500 sopra. Scrittura condizionale device presente nel sorgente.
- Es2.3, job 279661: 44 combinazioni uniche, 11 dimensioni da 1 KiB a 1 GiB. CSV coerente con il log e con la formula banda=byte/tempo entro gli arrotondamenti. Tabella e grafico generati dallo stesso CSV.
- A 1 GiB: pageable H2D 12.7274194 GB/s; pageable D2H 10.3861598 GB/s; pinned H2D 13.0832865 GB/s; pinned D2H 13.5117672 GB/s.

## Limiti riportati nel report

Il confronto base di es2.1 non effettua warm-up prima del primo batch: non viene confuso con il dato asincrono a regime dello sweep. Il risultato es2.2 e il primo superamento della soglia nella singola esecuzione, non una garanzia statistica di accuratezza. Il link PCIe non e stato verificato indipendentemente e il riferimento 15.8 GB/s e quello della traccia. Versione del compilatore e nodi dei nuovi job non sono inventati.

## Controlli del pacchetto

I tre plotter sono stati eseguiti con i dati consegnati. Il PDF e stato renderizzato per verifica visiva. L'archivio ZIP e stato riaperto e controllato; contiene un solo PDF e tutte le dipendenze della build. I file di testo del pacchetto hanno terminatori LF; gli script hanno permessi Unix eseguibili nell'archivio. Non sono state cambiate le misure originali o la logica dei benchmark CUDA durante questa finalizzazione.

## Aggiornamento LaTeX

Il report finale e stato riscritto in `assignment2/latex/assignment2_report.tex` e compilato con Tectonic. Formule, pedici, potenze e unita sono composti in modalita matematica. Il testo e stato reso piu diretto; i dati sperimentali non sono cambiati. Lo ZIP include il sorgente `report.tex` e il PDF aggiornato.
