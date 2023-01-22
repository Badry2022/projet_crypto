# Tests d'écriture sur SQLite et Mongo

L'objet est ici de comparer les temps d'écriture de données de type ticker sur différentes bases (SQLite ou MongoDB) avec différentes méthodes.

## Conclusions
### Impact de la taille des batchs
On a comparé l'écriture pour des lignes/documents par paquets de 1, 10, 100, ...
- SQLite : il y a une diminution sensible du temps d'écriture, environ 200 fois plus rapide entre 1 et 1000. Au delà, le temps est quasi stable.
- MongoDB : même type de conclusion, avec environ 50 fois plus rapide de 1 à 100, et 100 de 1 à 1000, puis à peu près stable

### Impact de la taille des tables / collections
On a répété l'opération après un premier passage, pour voir l'impact du remplissage sur le temps d'écriture.
On n'observe rien de vraiement sensible.

### Autres constats
#### SQLite
L'usage de la méthode sqlalchemy.insert est plus efficace que pandas.DataFrame.to_sql. Cette meilleure efficacité diminue avec l'augmentation des bacths de x 4 à x 1.5. Pour un batch de 1000, on a un facteur 2.

#### Mongo
On n'observe pas de différence sensible entre l'écriture dans une collection standard et l'écriture dans une collection TimeSerie.


## Description des fichiers
### producer.py
Permet de récupérer des batchs dans le format (mode) souhaité :
binance_data(n_batch, mode)

Les formats disponibles sont :
- LIST: le ticker est sous forme de liste :
    [timestamp, open, high, low, close, volume]

- DICT: le ticker est sous forme d'un dict :
    {"timestamp": timestamp, "open": open, "high": high, "low": low, "close": close, "volume": volume}

- DF: le batch est fourni sous forme d'un dataframe pandas, dont les colonnes sont :
    ["timestamp", "open", "high", "low", "close", "volume"]

- TIME_DICT: le ticker est sous forme d'un dict TimeSerie :
    {"timestamp": datetime(timestamp), "metadata": {"symbol": symbol, "interval": interval}, "open": open, "high": high, "low": low, "close": close, "volume": volume}

### sqlite.py
Fournit 2 classes InsertSQLite, PandasSQLite qui ont une méthode write_batch(batch).

- InsertSQLite : pour l'utilisation de la méthode sqlalchemy.insert via un batch en mode DICT
- PandasSQLite : pour l'utilisation de la méthode pandas.DataFrame.to_sql via un batch en mode DF

### mongo.py
Fournit 2 classes MongoBasic, MongoTimeSerie qui ont une méthode write_batch(batch).

- MongoBasic : pour l'utilisation d'une collection standard de Mongo via un batch en mode DICT
- MongoTimeSerie : pour l'utilisation d'une collection TimeSerie de Mongo via un batch en mode TIME_DICT

### write-timings.ipynb
Programme qui fait les mesures. Les résulats s'affichent dans le dataframe stats. Pour chaque type d'écriture, on effectue 2 passages avec la même succesion de batchs, et on affiche la moyenne et le minimum sur une répétition d'essai

On peut régler les différents paramètres :
- engines : les types d'écritures à tester. Instance qui doit avoir une méthode write_batch(batch)
- batch_modes : pour chaque type d'écriture indiquer le format de batch à fournir parmi BatchMode.DICT, BatchMode.DF, BatchMode.DICT, BatchMode.TIME_DICT
- engine_names : le nom du type d'écriture qui se retrouvera dans le dataframe de stats
- batches : liste des nombres par batch
- avg_samples : nombre de répétition pour chaque test




