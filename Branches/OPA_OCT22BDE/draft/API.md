# Proposition d'API pour OPA_OCT22BDE

L'objet de l'API est de mettre à disposition des données cryptos sous différentes forme.

Il y aura différents niveaux d'accès selon la route :
public

## Routes

### Connexion
/login GET #public = {username: str, password: str}

### Les ressources disponibles
/symbols GET #public = liste les pairs disponibles dans l'API

### Données historiques
/historical POST #admin = ajoute un symbol à la base

/historical/{symbol} GET #member = infos sur le symbol = les données disponibles par intervalle : date de début, fin ?

/historical/{symbol}/{interval} GET #member = récupère les données historiques
    {start_time: str ISODate, end_time: str ISODate, include?: "ochlv", exclude?: "ochlv"} (YYYY-MM-DD HH:MM:SS)
    
/historical/{symbol}/{interval} POST #member = ajout de données historique
    {start_time: str ISODate, end_time: str ISODate, include?: "ochlv", exclude?: "ochlv"} (YYYY-MM-DD HH:MM:SS)
    
/historical/{symbol}/{interval} DELETE #member = suppression de données historique
    {start_time: str ISODate, end_time: str ISODate, include?: "ochlv", exclude?: "ochlv"} (YYYY-MM-DD HH:MM:SS)

### Streaming
/stream/{symbol} GET #premium = récupère un stream des données par seconde
