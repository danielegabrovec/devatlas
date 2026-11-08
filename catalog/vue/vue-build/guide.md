## Build
Installa dal manifest esportato e lancia npm run build. Vite usa il plugin del framework e scrive dist, con asset nominati per hash.

## Controllo
Controlla index.html e i riferimenti ai file JS/CSS. Errori del compilatore non vanno ignorati: un build precedente nella cartella dist non prova che l'ultimo sorgente sia valido. L'app è soltanto client-side, senza endpoint o segreti server.