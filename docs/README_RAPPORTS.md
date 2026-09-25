# Rapports AutoFlow — livraison académique

Deux versions cohérentes sont prêtes à être importées dans Overleaf. Elles utilisent les mêmes schémas et les mêmes sources, dans `rapport_assets/`.

| Fichier principal | Version | Usage conseillé |
|---|---|---|
| `rapport.tex` | Complète, v1.1 | Version à finaliser avec les informations de stage et à soumettre au jury. |
| `rapport_visuel.tex` | Concise et visuelle | Version de lecture rapide / soutenance, avec davantage de figures, de tableaux et de messages-clés. |
| `rapport_autoflow.tex` | Version 1 d'origine | Conservée sans modification pour comparaison. |

## Importer dans Overleaf

1. Créer un projet vide.
2. Importer le fichier `.tex` choisi et le dossier entier `rapport_assets/`.
3. Dans *Menu > Main document*, choisir le fichier `.tex` concerné.
4. Compiler avec pdfLaTeX.
5. Remplacer les quatre champs indiqués en haut du fichier : auteur, encadrant académique, tuteur entreprise et structure d'accueil.

Les figures `fig_admin_*.png` sont des schémas d'interface et de traçabilité ; elles ne sont pas présentées comme des captures de données réelles. Les résultats d'évaluation sont explicitement limités au jeu fictif contrôlé et aux tests automatisés du dépôt.
