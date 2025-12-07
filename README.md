# etf_monitoring
L'Objectif de cette application est de suivre les performances d'une sélection d'ETF avec des indicateurs simples et incontournables, avec le stricte minimum d'information sur un seul visuel.
A cet effet, le portefeuille personnalisé permet de visualiser d'un seul coup d'oeil sur un même graphique tous les ETF de son portefeuille. Le tableau de variation permet d'avoir les performances chiffrés. De plus, le mix équipondéré est calculé automatiquement afin d'en faire la synthèse. 
Le portefeuille Harry Brown représente un exemple type de portefeuille personnalisé.
Le Podium montre le top 3 des ETF les plus performants par durée d'investissement.
Enfin, tous les ETF sont consultables individuellement et catégorisés.

Les données sont importées via l'API EOD Historical Data. Un script est automatisé pour exécuter quotidiennement une mise à jour du dernier cours de clôture des ETF vers leur base de donnée historique hébergée sur GCP Big Query. Ce script fonctionne grâce à Github Action.
La Data visualisation est générée en python grâce à Streamlit.

Ce système a été pensé pour être totatelement autonome dans le cloud et ne nécessite aucun appareil local connecté pour assurer les fonctionnalités de mise à jour, accessibilité des données et data visualisation : GitHub Action communique avec EOD Historical Data, qui importe et met à jour les données hébergées dans GCP Big Query, la data visualisation est assuré par Streamlit cloud.

l'environnement du projet est stocké dans le dossier venv. 3 requirements sont distingués :
 - requirements-dev : le package du développement en local
 - requirements-prod : le package réduit nécessaire à Git Action
 - requirements : le package réduit nécessaire à streamlit cloud (détection automatique du fichier par le nom dans streamlit)

Le workflow est organisé comme ceci :
 - .github / workflows :
    - daily_import.yml
    - weekly_import.yml
Orchestration des imports quotidiens et hebdo des cours de clôture depuis EOD HD vers Big query, deux frèquences pour pallier la contrainte du nombre max d'appel API gratuit sur EOD HD (20 par jour). Ces fichiers yml sont utilisés par Git Actions et ils exécutent selon leur programmation les scripts d'import.

Les clés privés sont stockés dans des variables. Les fichiers sont conservés en local et identifés dans Gitignore pour ne pas les pousser en public dans Github. Il y en a 2 :
 - GCP - big query : stockage des bases de données
 - EOD HD : API qui permet d'importer les cours actualisés d'actifs financiers.

 L'importation des données est exécutée en python (les scripts du dossier "imports"). Les scripts contrôlent la dernière date en base afin d'importer uniquement les cours journaliers postérieurs et de les y ajouter.

 l'application web Streamlit s'exécute par défaut avec le fichier app.py qui paramètre la page d'accueil. Les autres pages sont organisés dans le dossier "pages", avec un 1er niveau grâce à l'indexation par défaut streamlit :
  - 1_portefeuille_Harry_Browne.py
  - 2_Portefeuille_personnalisé.py
  - etc...
Ces scripts affichent simplement les différentes sections de la page et le menu des sous pages concernés. Le contenu interactif (sélection multiple, graphique et tableau) est appelé dans les scripts subordonnés du dossier "sections". Ils permettent :
 - selon un choix de date de début de période valide
 - selon un choix d'ETF
 - de rendre l'évolution des cours des ETF comparable sur un même graphique en leur attribuant une base 100  à la date d'origine, puis en recalculant leur évolution depuis cette base 100.
 - de construire une moyenne equipondéré des ETF de la sélection
 - d'afficher les résultats sur le graphique
 - d'affichier les résultats sur un tableau : en variation brute entre la date de début et la date de fin et en variation annualisé.
 Seules les Pages portefeuille_Harry_Browne et Portefeuille_personnalisé ont les fonctions de comparaisons. Les autres pages et sous pages présentent uniquement l'ETF concerné seul.
Enfin, une page podium fait le top 3 (sur l'évolution du cours) de tous les ETFs présents dans l'application selon les durées de détention : 3 mois et 1 an.