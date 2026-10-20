# Riassunti ampliati e precisazioni integrate

I due riassunti sono stati ampliati consultando i paper completi in `../data/`.
La versione attuale è stata sintetizzata a due pagine per ciascun paper,
mantenendo il carattere a 11 punti e le condizioni tecniche essenziali.
Il riassunto GPU approfondisce la transizione grafica--HPC--deep learning,
l'ecosistema software, i Tensor Cores, la scalabilità, A100 e i limiti di memoria.
Il riassunto BSP approfondisce i parametri del modello, slackness, hashing,
accessi concorrenti, algoritmi diretti e implementazioni di rete.
Sono mantenuti il paragrafo introduttivo GPU in italiano e il resto in inglese.

Le sei precisazioni riportate sotto rimangono un registro delle correzioni
già integrate nella versione precedente, ora ulteriormente sviluppate.
I dati e gli sviluppi futuri del paper GPU sono riferiti al suo contesto del 2021.

Compilazione standard, dalla cartella che contiene i sorgenti:

```sh
pdflatex evolution_gpu_summary.tex
pdflatex valiant_1990_summary.tex
```

Non servono immagini esterne, file bibliografici o comandi shell abilitati.
I PDF aggiornati vengono compilati con Tectonic in `../final/` e verificati
visivamente. Le eventuali copie in `../../output/pdf/` appartengono a versioni
precedenti.

## Evolution of the GPU

### 1. Acceleratori precedenti alla GeForce 256

La frase «The first GPUs only performed calculations on fragments» confonde
gli acceleratori precedenti con la GPU integrata descritta dal paper. Inoltre,
la conversione completa da modello 3D a immagine 2D comprende anche il lavoro
sui frammenti già svolto dagli acceleratori: attribuirla tutta alla CPU è troppo ampio.

Sostituzione proposta per i primi due paragrafi di “Origin”:

> Early 3D graphics accelerators handled fragment operations such as rasterization,
> texture mapping, Z-buffering, and shading. Vertex transformation, clipping,
> and lighting remained on the CPU. Introduced in 1999, GeForce 256 integrated
> vertex transformation and lighting with fragment processing on the same chip,
> offloading these vertex computations from the CPU.

Riscontro: `../data/Evolution_GPU.pdf`, p. 43 (seconda pagina del file).

### 2. Huang's law non sostituisce Moore's law

Il paper descrive una crescita delle prestazioni di inferenza maggiore di quella
spiegabile dal solo scaling dei transistor; non un cambiamento o una sostituzione
della legge di Moore. Anche il contrasto tra HPC e deep learning è troppo assoluto.

Sostituzione proposta delle frasi su precisione e leggi di crescita:

> Many HPC applications require high numerical precision, whereas many deep
> learning operations, especially inference, benefit from lower precision and
> higher throughput. In the period discussed by the paper, GPU inference
> performance grew faster than transistor scaling alone would predict.
> This trend, termed Huang's law, was largely enabled by data types and
> instructions specialized for deep learning.

Riscontro: `../data/Evolution_GPU.pdf`, pp. 45-46. La precisazione temporale evita
di trasformare i risultati storici del paper in una previsione generale.

### 3. Tensor Cores e scalabilità orizzontale

“Massive blocks” è poco preciso e l'ultima sezione enuncia un bisogno senza
spiegare come venga soddisfatto. Sono sufficienti due brevi sostituzioni:

> Tensor Cores accelerate matrix multiply-and-accumulate operations, amortizing
> instruction overhead over many arithmetic operations.

> Increasing model complexity requires scaling computation across multiple GPUs.
> NVLink and NVSwitch provide high-bandwidth communication among GPUs within
> a node, while InfiniBand connects nodes into larger training clusters.

Riscontro: `../data/Evolution_GPU.pdf`, pp. 45-46. La versione ampliata sviluppa
anche i formati numerici, la sparsità strutturata e l'architettura A100.

## Valiant (1990)

### 4. Superstep, L e parametro g

La frase sui superstep omette gli invii e può far pensare che si lavori su dati
appena ricevuti nello stesso superstep. Il paper usa dati locali disponibili
prima dell'inizio del superstep. Inoltre, senza `g` resta incompleta la parte
necessaria a comprendere le condizioni di efficienza.

Sostituzione proposta per il paragrafo sui superstep, con una sola aggiunta:

> A computation consists of supersteps combining local computation and message
> transmission and arrival. Local operations use data available before the start
> of the current superstep. In the original formulation, completion is checked
> every L time units, and the next superstep begins only when all participating
> components have completed the current one. The bandwidth parameter g measures
> the communication cost relative to local computation: an h-relation, in which
> each component sends and receives at most h messages, costs gh time units for
> sufficiently large h.

Riscontro: `../data/Val90.pdf`, pp. 105-106 (terza e quarta pagina del file).
Non propongo di aggiungere formule di costo prese da formulazioni successive.

### 5. Hashing: bilanciamento del carico

L'obiettivo non è semplicemente minimizzare le collisioni tra indirizzi:
è evitare che gli accessi si concentrino su poche unità di memoria.
Slackness e periodicità consentono di assorbire lo sbilanciamento residuo.

Sostituzione proposta dell'ultima frase del punto sull'hashing:

> Hashing spreads memory accesses across memory components. Sufficient parallel
> slackness and a suitable periodicity L allow residual load imbalance to be
> absorbed efficiently.

Riscontro: `../data/Val90.pdf`, pp. 106-107.

### 6. Accessi CRCW e condizioni della simulazione

La sigla manoscritta è trascritta come **CRCW**. L'abbreviazione finale
«prob. functions», inizialmente conservata senza espanderla, è stata sostituita
con la spiegazione dei metodi descritti nel paper. Replicazione, ordinamento e metodi probabilistici
non vanno però presentati come alternative equivalenti: il paper descrive una simulazione generale basata
sull'ordinamento di interi, una soluzione più semplice con replicazione sotto
condizioni ulteriori, con un'analisi probabilistica del bilanciamento del carico.

Sostituzione proposta dell'intero punto “Simultaneous accesses”:

> Concurrent reads and writes (CRCW PRAM) can be simulated efficiently on BSP
> under suitable conditions. With constant g, L at least log p, and
> v = p^(1+epsilon) virtual processors for fixed epsilon > 0, the paper gives
> an optimal simulation using parallel integer sorting. Simpler replication
> schemes suffice when contention is bounded and enough slack is available.
> Replication and combining are performed and charged as operations at the
> components; they are not free capabilities of the router.

Nel `.tex`, le condizioni si scrivono `$g=O(1)$`, `$L\geq\log p$` e
`$v=p^{1+\varepsilon}$`, con `$\varepsilon>0$` fissato. L'esempio
`$v=p\log p$` del paragrafo sulla parallel slackness rimane valido come esempio
generale, ma non basta da solo a esprimere le condizioni di questa simulazione CRCW.

Riscontro: `../data/Val90.pdf`, p. 107 (quinta pagina del file).
