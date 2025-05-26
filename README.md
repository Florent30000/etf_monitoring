# etf_monitoring
L'Objectif de cette application et des suivre les performances d'une sélection d'ETF avec des indicateurs simples et incontournables, avec le strcite minimum d'information sur un seul visuel.
A cet effet, le portefeuille personnalisé permet de visualiser d'un seul coup d'oeil sur un même graphique tous les ETF de son portefeuille. Le tableau de variation permet d'avoir les performances chiffrés. De plus, le mix équipondéré est calculé automatiquement afin d'en faire la synthèse. 
Le portefeuille Harry Brown représente un exemple type de portefeuille personnalisé.
Le Podium montre le top 3 des ETF les plus performants par durée d'investissement.
Enfin, tous les ETF sont consultables individuellement et catégorisés (capitalisation US, énergie, IA).


Les données sont importées via l'API EOD Historical Data. Un script est automatisé pour exécuter quotidiennement une mise à jour du dernier cours de clôture des ETF vers leur base de donnée historique hébergée sur Google Big Query. Ce script fonctionne grâce à Github Action.
La Data visualisation est générée en python grâce à Streamlit.

Ce système a été pensé pour être totatelement autonome dans le cloud et ne nécessite aucun appareil local connecté pour assurer les fonctionnalités de mise à jour, accessibilité des données et data visualisation : GitHub Action communique avec EOD Historical Data, lui même met à jour les données hébergées dans Google Big Query, qui à son tour partage les données sur streamlit.
