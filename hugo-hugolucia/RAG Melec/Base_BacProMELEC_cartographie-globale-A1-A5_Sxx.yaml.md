
cartographie_globale_MELEC:
reference_officiel:
sources:
- "Référentiel Bac Pro MELEC (compétences et tâches, Eduscol / BO)."
- "Activités A1 à A5 : préparation, réalisation, mise en service, maintenance, communication."
principes_de_rattachement:
- "Chaque situation Sxx est reliée à au moins une activité du référentiel (A1 à A5)."
- "Les codes A1–A5 sont utilisés dans la base pour la RAG, mais pas affichés tels quels aux apprenants."
- "La RAG peut être utilisée en appui de préparation à l’évaluation (CCF, certification) en ciblant les activités travaillées."

carte_activites_A1-A5_vers_situations:
A1_preparation:
description: "Préparation des opérations de réalisation, de mise en service et de maintenance."
situations:
- S01
- S02
- S03
- S04
- S05
- S06
A2_realisation:
description: "Réalisation et installation des équipements électriques."
situations:
- S07
- S08
- S09
- S10
- S11
- S12
- S13
- S14
A3_mise_en_service_controle:
description: "Contrôle, essais et mise en service des installations."
situations:
- S15
- S16
- S17
- S18
- S19
- S20
A4_maintenance_diagnostic:
description: "Maintenance préventive et corrective des installations et équipements."
situations:
- S21
- S22
- S23
- S24
- S25
- S26
A5_communication_organisation:
description: "Communication, compte rendu, organisation au sein de l’entreprise et avec les clients."
situations:
- S27
- S28
- S29
- S30

usage_par_moment_AFEST:
ante_action:
objectifs:
- "Aider l’apprenant à se projeter dans l’action à venir (intention, préparation, risques)."
- "Relier la situation à venir à une activité A1–A5 et à une ou deux situations Sxx proches."
fichiers_a_privilegier:
- "cartographie_globale_MELEC (cette carte) pour situer l’activité (A1–A5)."
- "Base_BacProMELEC_profils-RAG_par-bloc.yaml (profils_RAG_par_bloc)."
- "Base_BacProMELEC_index-difficultes-transversales.yaml (pour cibler une difficulté à observer)."
- "Base_BacProMELEC_meta-usage_situations_S01-a-S30.yaml (meta_usage_situations) pour choisir 1 Sxx."
consignes_Hugo:
- "Identifier d’abord l’activité dominante (A1…A5) à partir du contexte décrit."
- "Sélectionner au maximum 2 situations Sxx de référence pour la préparation."
- "Formuler avec l’apprenant : 'Aujourd’hui, on va surtout travailler ce qui ressemble à Sxx, qui relève de A…'."
pendant_action:
objectifs:
- "Rester focalisé sur la sécurité et l’observation, pas sur l’explication théorique."
- "Repérer en direct 1 ou 2 points observables à reprendre en séquence réflexive."
fichiers_a_privilegier:
- "Base_BacProMELEC_profils-RAG_par-bloc.yaml (repères sur ce qu’il est pertinent d’observer)."
- "Base_BacProMELEC_index-difficultes-transversales.yaml (définir la difficulté à regarder)."
consignes_Hugo:
- "Ne pas surcharger l’apprenant de contenu pendant l’action."
- "Utiliser éventuellement la RAG pour se rappeler 1 ou 2 savoir_faire_observables clés de la situation Sxx ciblée."
- "Noter mentalement ou brièvement les points à reprendre en post‑action (liés à l’activité A1–A5 concernée)."
post_action:
objectifs:
- "Analyser la situation vécue en lien avec l’activité du référentiel et les compétences visées."
- "Faire émerger ce que l’apprenant a compris, réussi, raté, et ce qu’il veut retravailler."
fichiers_a_privilegier:
- "Fiches situations Sxx (Base_BacProMELEC_Sxx.yaml)."
- "Base_BacProMELEC_meta-usage_situations_S01-a-S30.yaml."
- "Base_BacProMELEC_index-difficultes-transversales.yaml."
- "Bloc questions_reflexives (intégré dans la base)."
consignes_Hugo:
- "Repartir de la situation réelle, puis choisir 1 fiche Sxx proche (même activité A1–A5, même type de difficulté)."
- "Travailler au maximum 2 à 3 champs de la fiche (par ex. erreurs_frequentes + indices_de_fragilite + questions_hugo_possibles)."
- "Faire le lien explicite avec l’activité du référentiel : 'Ce que tu viens de vivre touche surtout à A… (préparation / réalisation / mise en service / maintenance / communication)'."
- "Conclure par 1 ou 2 points concrets : 'pour la prochaine situation A…, je ferai différemment…'"

legende_fichiers_RAG_Hugo:
Base_BacProMELEC_Sxx.yaml:
contenu: "Ensemble des fiches situations détaillées S01 à S30."
usage_principal:
- "Support d’analyse post‑action : aider l’apprenant à nommer et analyser ce qu’il a vécu."
- "Préparation ciblée d’une nouvelle situation proche (ante‑action)."
precautions:
- "Ne pas lire intégralement la fiche à l’apprenant."
- "Ne pas utiliser comme 'cours complet', mais comme support de questionnement."
Base_BacProMELEC_meta-usage_situations_S01-a-S30.yaml:
contenu: "Meta_usage_situations : tags, moments d’utilisation, objectifs, signaux pour chaque Sxx."
usage_principal:
- "Aider Hugo à choisir rapidement la fiche Sxx la plus pertinente à partir de ce que dit l’apprenant."
- "Relier parole de l’apprenant (signaux) à une intention pédagogique claire (objectifs_possibles)."
precautions:
- "Ne pas multiplier les fiches : 1 situation Sxx principale par séquence réflexive."
Base_BacProMELEC_profils-RAG_par-bloc.yaml:
contenu: "Profils RAG par bloc (préparation, réalisation, mise_en_service, maintenance, communication)."
usage_principal:
- "Filtrer les types de contenus proposés selon le bloc d’activité concerné."
- "Orienter Hugo sur quels champs de fiches privilégier en fonction du moment AFEST."
precautions:
- "Toujours commencer par identifier le bloc (préparation / réalisation / mise_en_service / maintenance / communication) dominant de la situation."
Base_BacProMELEC_index-difficultes-transversales.yaml:
contenu: "Index des grandes difficultés transversales (sécurité, diagnostic, repérage, écrits, etc.) vers les situations Sxx."
usage_principal:
- "Varier les situations Sxx pour travailler une même difficulté."
- "Programmer des séquences réflexives successives sur un même axe (ex : diagnostic) avec plusieurs contextes."
precautions:
- "Éviter de traiter plusieurs difficultés majeures à la fois dans une même séquence."
cartographie_globale_MELEC.yaml:
contenu: "Présent fichier : liens avec référentiel officiel (A1–A5), usage par moment AFEST, légende des fichiers."
usage_principal:
- "Point d’ancrage pour garder la cohérence avec le référentiel Bac Pro MELEC et la certification."
- "Support de paramétrage de la RAG (routing) plutôt que de dialogue direct avec l’apprenant."
precautions:
- "Ne pas afficher les codes A1–A5 à l’apprenant, mais les utiliser pour structurer la sélection des situations et des questions."

