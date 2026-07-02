# Notes de présentation — SMS Scam Detector

## Slide 1 — Titre
Bonjour, nous sommes l’équipe [nom de l’équipe]. Notre projet s’appelle **SMS Scam Detector**. C’est un outil d’IA qui détecte les SMS frauduleux et explique pourquoi un message est risqué. L’objectif est de protéger les élèves, les familles et les utilisatrices de Mobile Money contre les arnaques.

## Slide 2 — Problème
Les arnaques par SMS sont dangereuses parce qu’elles paraissent urgentes et crédibles. Elles peuvent imiter une banque, Orange Money, MTN MoMo ou même un proche. Le message pousse souvent à cliquer, appeler, envoyer un PIN ou agir immédiatement. Notre question est simple: comment aider une personne à savoir rapidement si un SMS est sûr, publicitaire ou frauduleux?

## Slide 3 — Solution
Notre solution est une application simple. L’utilisateur colle un SMS. Le modèle analyse le texte et les signaux suspects. Ensuite, il donne une classe: safe, spam ou smishing. Le plus important: il explique les raisons, par exemple la présence d’un lien, d’un numéro, d’une urgence ou d’une demande de PIN.

## Slide 4 — Démo
Nous montrons trois exemples. Le premier est un SMS normal: il est classé safe. Le deuxième est une promotion: il est classé spam. Le troisième contient un message Mobile Money avec demande de PIN: il est classé smishing. En moins d’une minute, le jury voit la prédiction, la confiance et les explications.

## Slide 5 — Approche technique
Le modèle utilise une approche légère et explicable. Nous nettoyons les SMS sans supprimer les éléments importants comme liens, numéros et ponctuation. Ensuite, nous utilisons TF-IDF pour comprendre les mots et n-grammes. Nous ajoutons aussi des signaux structurels: lien, téléphone, email, argent, OTP/PIN, urgence, menace et récompense. Le modèle est une régression logistique équilibrée.

## Slide 6 — Explicabilité
Nous ne voulons pas seulement dire “scam”. Nous voulons aider l’utilisateur à comprendre. Par exemple, si le message dit que le compte sera suspendu et demande de cliquer sur un lien, l’application affiche les raisons: lien détecté, menace, urgence et contexte financier. Cela transforme l’outil en assistant d’éducation cyber.

## Slide 7 — Pertinence locale
Le projet est adapté au contexte camerounais: Mobile Money, Orange Money, MTN MoMo, français et anglais. Il est aussi aligné avec l’esprit CGIS: science pour les données, technologie pour l’application, engineering pour l’intégration, arts pour le design, mathématiques pour l’évaluation.

## Slide 8 — Résultats et limites
Le prototype fonctionne déjà avec un petit dataset de démonstration. Les métriques actuelles montrent que le système est utilisable pour la démo, mais nous sommes honnêtes: il faut plus de données réelles, anonymisées et locales pour un système robuste. Notre priorité est de réduire les faux négatifs, c’est-à-dire les scams que le modèle pourrait rater.

## Slide 9 — Roadmap
Après le hackathon, nous voulons enrichir les données, améliorer le modèle, créer une version terrain utilisable hors ligne et collaborer avec des clubs scolaires, universités, associations de femmes en STEAM et éventuellement opérateurs télécoms.

## Slide 10 — Conclusion
Notre message final est que la cybersécurité doit être compréhensible par toutes et tous. SMS Scam Detector protège, explique et éduque. Avec plus de données et d’accompagnement, ce projet peut devenir un vrai outil de prévention pour les jeunes filles, les familles et les communautés au Cameroun.
