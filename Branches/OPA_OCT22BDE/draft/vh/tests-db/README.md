# Comparaison écriture / lecture — SQL — NoSQL — TimeSeries

## SQL avec une seule grande table
En pratique, test effectué avec SQLite sur une table avec 350 * 256 000 lignes.
- en écriture : environ 20 minutes pour écrire les lignes
- en lecture : environ 40 secondes pour récupérer une ligne ou compter les lignes

## SQL avec plusieurs tables de tailles raisonnables
En pratique, test effectué avec SQLite sur 1000 tables de 86400 lignes chacunes.
- en écriture : environ 20 minutes pour écrire les 1000 tables
- en lecture : immédiat pour récupérer une ligne ou compter les lignes d'une table.

NB : il faut que le programme accédant à la base en connaisse la structure "hachée" pour faire des requêtes simplifiées

## NoSQL classique
En pratique, test effectué avec MongoDB sur une collection avec 350 * 256 000 documents.
- en écriture : environ 70 à 80 minutes pour écrire les documents
- en lecture : environ 3 à 4 minutes pour récupérer un intervalle de temps de 1000 documents

## NoSQL avec TimeSeries
En pratique, test effectué avec MongoDB sur une collection en mode TimeSerie avec 350 * 256 000 documents.
- en écriture : environ 80 minutes pour écrire les documents
- en lecture : immédiat pour récupérer un intervalle de temps de 1000 documents

NB : en mode TimeSerie, il faut faire attention à ce qu'on stocke en tant que metafield car c'est le seul moyen d'accès aux documents si on souhaite les modifier ou les supprimer. Sinon, on peut supprimer la collection complète...

