

S07 réalisation Poser une ligne prise de courant encastrée bâtiment Activité de base sur chantier logement, mobilise traçage, perçage, passage de gaines, respect des hauteurs. Traçage imprécis, oubli de réservation, gaines trop courtes, rayons de courbure non respectés.​
S08 réalisation Câbler un circuit d’éclairage simple allumage bâtiment Très fréquent, support pour comprendre phase, neutre, retour lampe, commande et sécurité. Inversion phase/neutre, oublis de repère, mauvaise connexion au luminaire, serrage insuffisant.​
S09 réalisation Réaliser le câblage d’un tableau divisionnaire bâtiment / tertiaire Met en jeu repérage, organisation, cheminement, serrage, esthétique et conformité, souvent confié à l’alternant. Tableau désorganisé, longueurs de fils mal gérées, erreurs de repérage, mélange circuits spécialisés/généraux.​
S10 réalisation Installer un détecteur de mouvement pour éclairage bâtiment / tertiaire Situe l’apprenant à l’interface entre éclairage traditionnel et fonctions automatisées simples. Mauvais réglages de temporisation/lux, mauvais positionnement, confusion schéma 2 fils / 3 fils.​
S11 réalisation Poser un câblage de commande moteur simple industrie légère Introduction concrète à la commande de moteurs (démarrage direct), logique de contacteurs et protections. Erreurs sur contacts NO/NC, bobine mal alimentée, oubli de protection thermique, câblage peu lisible.​
S12 réalisation Tirer et fixer des chemins de câbles tertiaire / industrie Fréquent sur grands plateaux tertiaires et ateliers, développe sens de la trajectoire, supports, dilatation. Mauvaise prise de cotes, fixations inadaptées, non‑respect des distances avec autres réseaux.

IMPORTANT : la sortie NE DOIT CONTENIR QUE le bloc YAML demandé, rien d’autre.

- Pas de rappel du tableau.
- Pas de répétition de la consigne.
- Pas de notes de bas de page.
- Pas de texte en dehors du YAML.

Situations à traiter (ne fais que les utiliser, ne les recopie pas telles quelles dans la sortie) :
[COLLER ICI 5 À 8 LIGNES DU TABLEAU : ID, Bloc, Situation, Contexte, Pourquoi_formateur, Difficultes_typiques, Priorite_Hugo]

Pour chaque situation, produis UNE fiche au format YAML avec exactement les champs suivants :

- situation_id
- titre
- bloc (preparation / realisation / mise_en_service / maintenance / communication)
- contexte_entreprise
- description_courte
- ce_que_l_apprenant_fait
- savoirs_mobilises
- savoir_faire_observables
- connaissances_sous_jacentes
- erreurs_frequentes
- risques_et_vigilances
- indices_de_comprehension
- indices_de_fragilite
- questions_hugo_possibles
- mini_cas_probleme
- mini_cas_situation_interessante
- mini_cas_besoin_aide

Contraintes :

- Français.
- Niveau Bac Pro (pas BTS).
- Détail technique sérieux, cohérent avec les activités Bac Pro MELEC (préparation, réalisation/mise en service, maintenance, communication).
- Pas de codes RNCP, pas de U2/U31, pas de jargon de référentiel dans le texte des fiches.
- Chaque champ liste contient 2 à 6 éléments maximum (sauf les mini_cas, qui sont 1 phrase chacun).
- AUCUNE note de bas de page, AUCUN lien web, AUCUNE citation de type [^1] ou [web:56].

Format de sortie attendu :

- Une liste YAML de fiches commençant par “- situation_id: …”.
- Pas de ```yaml ni ```markdown, pas de texte avant ou après.
- Exemple de structure (à ne pas recopier, juste pour la forme) :
- situation_id: SXX
titre: ...
bloc: preparation
contexte_entreprise:
    - ...
    - ...
description_courte:
    - ...
ce_que_l_apprenant_fait:
    - ...
[...]

Rappelle-toi : la réponse finale doit être STRICTEMENT ce bloc YAML, et rien d’autre.
au début de ta réponse, donne le nom du fichier : Base_BacProMELEC_preparation_S07-a-S013.yaml

- situation_id: S07
titre: Poser une ligne de prises encastrées
bloc: realisation
contexte_entreprise:
    - Maison individuelle en construction
    - Rénovation d’appartement
    - Petit immeuble de logements
description_courte:
    - L’alternant réalise une ligne de prises encastrées dans un mur.
    - Il enchaîne traçage, perçage, passage de gaines et mise en place des boîtes.
ce_que_l_apprenant_fait:
    - Repère sur le mur l’emplacement des prises à partir du plan.
    - Trace les hauteurs et les alignements des boîtes.
    - Perce ou saigne le support selon le type de mur.
    - Passe les gaines et les fixe proprement jusqu’aux boîtes.
savoirs_mobilises:
    - Lecture du plan d’implantation des prises.
    - Règles de hauteur et d’alignement des appareillages.
    - Choix des outils adaptés au type de support.
    - Notions de cheminement des gaines et de rayons de courbure.
savoir_faire_observables:
    - Sait tracer des lignes droites et des hauteurs régulières.
    - Sait utiliser proprement perceuse, scie-cloche ou rainureuse.
    - Sait positionner et fixer des boîtes d’encastrement correctement.
    - Sait passer les gaines sans les pincer ni les abîmer.
connaissances_sous_jacentes:
    - Contraintes de pose encastrée selon les types de murs.
    - Effet des rayons de courbure sur le tirage des conducteurs.
    - Importance de l’alignement et de l’esthétique pour le client.
    - Impacts des réservations manquantes sur la suite du chantier.
erreurs_frequentes:
    - Traçage approximatif donnant des prises non alignées.
    - Oubli de réservation pour certaines boîtes.
    - Gaines trop courtes ou trop tendues.
    - Courbures trop serrées rendant le tirage difficile.
risques_et_vigilances:
    - Détérioration du support (fissures, éclats importants).
    - Difficulté à passer les conducteurs, risque d’âme blessée.
    - Mauvaise tenue mécanique des boîtes dans le temps.
    - Non-respect des hauteurs pouvant gêner l’usage.
indices_de_comprehension:
    - L’alternant prépare son traçage avant de percer.
    - Il adapte ses outils au support rencontré.
    - Il vérifie régulièrement l’alignement et les hauteurs.
    - Il anticipe le passage des câbles lors de la pose des gaines.
indices_de_fragilite:
    - Il commence à percer sans repérage précis.
    - Il coupe les gaines à la dernière minute sans marge.
    - Il ne voit pas l’impact d’un mauvais alignement.
    - Il ne tient pas compte du cheminement futur des conducteurs.
questions_hugo_possibles:
    - Comment t’y prends-tu pour être sûr de tes hauteurs et alignements ?
    - Qu’est-ce qui t’aide à choisir le cheminement des gaines ?
    - À quel moment vérifies-tu que tes gaines ne sont ni trop courtes ni trop tendues ?
    - Qu’as-tu appris la dernière fois où une réservation manquait ?
mini_cas_probleme: "Après avoir posé toutes les boîtes, tu découvres qu’une gaine est trop courte pour atteindre le tableau."
mini_cas_situation_interessante: "En préparant bien ton traçage, tu réalises une ligne de prises parfaitement alignées qui satisfait le client."
mini_cas_besoin_aide: "Tu n’es pas sûr de la hauteur à respecter pour une série de prises dans une cuisine équipée."
- situation_id: S08
titre: Câbler un circuit d’éclairage simple allumage
bloc: realisation
contexte_entreprise:
    - Logement individuel
    - Cage d’escalier d’immeuble
    - Petits locaux techniques
description_courte:
    - L’alternant câble un circuit d’éclairage avec un seul point de commande.
    - Il relie tableau, interrupteur, luminaire et éventuelle boîte de dérivation.
ce_que_l_apprenant_fait:
    - Tire les conducteurs depuis le tableau jusqu’à la zone d’éclairage.
    - Raccorde l’interrupteur en respectant phase et retour lampe.
    - Raccorde le luminaire en respectant phase, neutre et terre.
    - Vérifie la cohérence de son câblage avant la mise sous tension.
savoirs_mobilises:
    - Schéma de principe d’un simple allumage.
    - Distinction phase, neutre, terre et retour lampe.
    - Règles de repérage des conducteurs et des bornes.
    - Utilisation de dominos, Wago ou borniers de manière sûre.
savoir_faire_observables:
    - Sait identifier et utiliser la phase pour alimenter l’interrupteur.
    - Sait repérer et raccorder correctement le retour lampe.
    - Sait réaliser des connexions propres et bien serrées.
    - Sait organiser les conducteurs dans la boîte ou dans le luminaire.
connaissances_sous_jacentes:
    - Rôle de la phase et du neutre dans un circuit d’éclairage.
    - Conséquences d’une inversion phase/neutre.
    - Importance du conducteur de protection pour les luminaires métalliques.
    - Lien entre serrage correct et échauffement des connexions.
erreurs_frequentes:
    - Inversion phase et neutre au niveau de l’interrupteur ou du luminaire.
    - Oubli du repérage du retour lampe.
    - Connexions mal serrées ou mal isolées.
    - Encombrement excessif des boîtes de dérivation.
risques_et_vigilances:
    - Risque de choc électrique en cas d’inversion ou de défaut de protection.
    - Dysfonctionnement du luminaire ou coupure intempestive.
    - Échauffement au niveau des connexions mal serrées.
    - Difficulté de dépannage si le repérage est absent.
indices_de_comprehension:
    - L’alternant explique clairement le trajet de la phase et du retour.
    - Il vérifie ses connexions avant de refermer les boîtes.
    - Il repère les conducteurs de manière lisible.
    - Il fait le lien entre schéma et réalité de câblage.
indices_de_fragilite:
    - Il confond les conducteurs dès qu’ils sont de la même couleur.
    - Il inverse souvent phase et neutre.
    - Il ne voit pas l’importance du repérage pour la suite.
    - Il referme sans vérifier ni tester les connexions.
questions_hugo_possibles:
    - Comment t’assures-tu de ne pas inverser phase et neutre ?
    - Que regardes-tu en priorité quand tu ouvres un luminaire à raccorder ?
    - Comment fais-tu le lien entre le schéma et ce que tu as devant toi ?
    - Qu’est-ce qui t’a déjà posé problème sur un simple allumage ?
mini_cas_probleme: "Après ton câblage, le luminaire ne s’allume pas ou reste sous tension en permanence."
mini_cas_situation_interessante: "En expliquant ton schéma à un collègue, tu repères toi-même une inversion avant la mise sous tension."
mini_cas_besoin_aide: "Tu ne comprends pas bien comment repérer le retour lampe parmi plusieurs conducteurs dans une boîte."
- situation_id: S09
titre: Câbler un tableau divisionnaire
bloc: realisation
contexte_entreprise:
    - Tableau d’étage dans un immeuble
    - Tableau secondaire pour annexe ou garage
    - Petit tableau tertiaire pour bureau ou local technique
description_courte:
    - L’alternant réalise le câblage interne d’un tableau divisionnaire.
    - Il organise les conducteurs, les protections et le repérage des circuits.
ce_que_l_apprenant_fait:
    - Positionne les disjoncteurs, différentiels et accessoires dans le tableau.
    - Pose et raccorde les peignes d’alimentation.
    - Raccorde les départs de circuits en respectant phase, neutre et terre.
    - Met en place un repérage clair des circuits et des rangées.
savoirs_mobilises:
    - Lecture du schéma de tableau et du plan des circuits.
    - Organisation interne d’un tableau (rangées, ordonnancement).
    - Choix du cheminement des conducteurs à l’intérieur du coffret.
    - Techniques de repérage et d’étiquetage.
savoir_faire_observables:
    - Sait organiser les départs de manière logique et lisible.
    - Sait gérer les longueurs de conducteurs sans excès ni tension.
    - Sait utiliser proprement peignes et borniers.
    - Sait réaliser un repérage clair des circuits sur le tableau.
connaissances_sous_jacentes:
    - Règles de base pour la répartition des circuits sur les différentiels.
    - Influence de l’organisation du tableau sur la maintenance future.
    - Effet des longueurs de conducteurs sur l’encombrement et les échauffements.
    - Importance d’un repérage durable pour l’utilisateur et le dépanneur.
erreurs_frequentes:
    - Tableau désorganisé avec conducteurs croisés dans tous les sens.
    - Longueurs de fils mal gérées (trop longs ou trop tendus).
    - Repérage incomplet ou absent.
    - Mélange de circuits spécialisés et généraux sans logique.
risques_et_vigilances:
    - Difficultés importantes pour dépanner ou modifier l’installation.
    - Risques d’erreur de raccordement lors d’une intervention ultérieure.
    - Echauffement localisé si les conducteurs sont mal répartis.
    - Mauvaise image professionnelle auprès du client.
indices_de_comprehension:
    - L’alternant anticipe l’emplacement des départs avant de câbler.
    - Il garde une cohérence entre schéma et disposition réelle.
    - Il prend le temps de soigner le repérage.
    - Il est capable d’expliquer la logique de son organisation.
indices_de_fragilite:
    - Il câble au fur et à mesure sans vision d’ensemble.
    - Il ne se préoccupe pas de l’esthétique ni de la lisibilité.
    - Il oublie d’étiqueter ou repère de manière illisible.
    - Il a du mal à retrouver un circuit une fois le tableau terminé.
questions_hugo_possibles:
    - Comment décides-tu de l’emplacement de chaque circuit dans le tableau ?
    - Qu’est-ce qui t’aide à garder un tableau lisible pendant le câblage ?
    - Comment t’y prends-tu pour gérer les longueurs de conducteurs ?
    - Que ressens-tu quand tu ouvres un tableau bien organisé ou au contraire très fouillis ?
mini_cas_probleme: "Une fois ton câblage terminé, tu n’arrives plus à suivre le chemin d’un circuit précis dans le tableau."
mini_cas_situation_interessante: "Tu reprends un tableau existant très fouillis et tu proposes avec ton tuteur une réorganisation plus claire."
mini_cas_besoin_aide: "On te confie le câblage complet d’un petit tableau et tu ne sais pas par où commencer pour rester organisé."
- situation_id: S10
titre: Installer un détecteur de mouvement pour éclairage
bloc: realisation
contexte_entreprise:
    - Couloir ou cage d’escalier d’immeuble
    - Parking ou local de stockage
    - Parties communes de petit tertiaire
description_courte:
    - L’alternant installe et raccorde un détecteur de mouvement pour commander un éclairage.
    - Il choisit l’emplacement, câble le détecteur et règle ses paramètres de base.
ce_que_l_apprenant_fait:
    - Repère sur plan ou sur place la zone à couvrir par le détecteur.
    - Fixe le détecteur au mur ou au plafond en respectant les recommandations.
    - Raccorde phase, neutre, retour lampe et éventuellement borne de commande.
    - Règle la temporisation, la sensibilité et le seuil de luminosité.
savoirs_mobilises:
    - Compréhension du schéma de câblage du détecteur.
    - Notions de zones de détection et d’angles morts.
    - Paramètres de base : temps d’éclairage, luminosité, sensibilité.
    - Différences entre câblage deux fils et trois fils.
savoir_faire_observables:
    - Sait choisir un emplacement cohérent pour couvrir la zone utile.
    - Sait raccorder correctement le détecteur au circuit d’éclairage.
    - Sait régler le détecteur en fonction de la situation réelle.
    - Sait tester le fonctionnement et ajuster les réglages.
connaissances_sous_jacentes:
    - Principe de détection de mouvement (infrarouge, etc.) de manière simple.
    - Lien entre réglages et confort d’utilisation pour les occupants.
    - Effet du positionnement sur les déclenchements intempestifs.
    - Contraintes de compatibilité avec certains luminaires ou sources.
erreurs_frequentes:
    - Mauvais positionnement ne couvrant pas correctement la zone souhaitée.
    - Réglages de temporisation ou de luminosité inadaptés.
    - Confusion entre borniers selon schéma deux fils ou trois fils.
    - Oubli de tests en conditions réelles (jour/nuit, passage réel).
risques_et_vigilances:
    - Zones non éclairées au bon moment, risque de chute ou d’accident.
    - Allumages intempestifs gênants ou énergivores.
    - Mécontentement des utilisateurs si l’éclairage les surprend ou ne suit pas leur rythme.
    - Risque de mauvais câblage conduisant à un non-fonctionnement.
indices_de_comprehension:
    - L’alternant justifie l’emplacement choisi par rapport aux passages.
    - Il adapte les réglages après observation du comportement réel.
    - Il sait expliquer simplement le cheminement du courant dans le montage.
    - Il propose des ajustements en fonction des retours des utilisateurs.
indices_de_fragilite:
    - Il place le détecteur sans réfléchir à la zone couverte.
    - Il laisse les réglages par défaut sans les questionner.
    - Il ne comprend pas les différences entre les schémas proposés.
    - Il ne teste pas le détecteur dans des conditions variées.
questions_hugo_possibles:
    - Comment choisis-tu l’emplacement d’un détecteur dans un couloir ?
    - Quels réglages modifies-tu en premier et pourquoi ?
    - Comment sais-tu que ton réglage convient aux utilisateurs ?
    - Peux-tu m’expliquer le cheminement de la phase dans ce montage ?
mini_cas_probleme: "Le détecteur déclenche l’éclairage sans arrêt alors que personne ne passe réellement dans la zone."
mini_cas_situation_interessante: "Après plusieurs essais, tu trouves un réglage qui satisfait à la fois la sécurité et le confort des occupants."
mini_cas_besoin_aide: "Tu es face à un schéma deux fils / trois fils et tu ne sais pas quel montage choisir ni comment raccorder."
- situation_id: S11
titre: Poser un câblage de commande moteur simple
bloc: realisation
contexte_entreprise:
    - Petite ligne de production en atelier
    - Machine simple avec moteur asynchrone
    - Installation de ventilateur ou pompe en industrie légère
description_courte:
    - L’alternant réalise le câblage de commande d’un moteur en démarrage direct.
    - Il met en œuvre commande, contacteur, protection thermique et boutons.
ce_que_l_apprenant_fait:
    - Suit le schéma de commande pour raccorder bobine, contacts et boutons.
    - Raccorde la partie puissance du contacteur vers le moteur.
    - Intègre un relais thermique ou une protection équivalente.
    - Vérifie la cohérence de son câblage avant essai.
savoirs_mobilises:
    - Lecture d’un schéma de commande moteur simple.
    - Distinction contacts NO et NC et leur rôle.
    - Principe de la bobine de contacteur et de son alimentation.
    - Notions de base sur la protection thermique du moteur.
savoir_faire_observables:
    - Sait câbler correctement la boucle de commande (marche/arrêt).
    - Sait utiliser contacts auxiliaires pour le maintien.
    - Sait insérer et raccorder le relais thermique.
    - Sait vérifier visuellement la conformité de son câblage au schéma.
connaissances_sous_jacentes:
    - Principe du démarrage direct d’un moteur asynchrone.
    - Rôle du contacteur et de ses contacts principaux et auxiliaires.
    - Fonction de la protection thermique pour éviter la surchauffe.
    - Lien entre schéma de commande et schéma de puissance.
erreurs_frequentes:
    - Inversion contacts NO/NC entraînant un fonctionnement anormal.
    - Bobine mal alimentée ou non protégée.
    - Oubli d’intégrer la protection thermique dans la chaîne.
    - Câblage peu lisible rendant le dépannage difficile.
risques_et_vigilances:
    - Risque de démarrage intempestif ou impossible du moteur.
    - Absence de protection efficace en cas de surcharge.
    - Difficulté à diagnostiquer une panne ultérieure.
    - Risque pour l’opérateur si la fonction arrêt ne marche pas correctement.
indices_de_comprehension:
    - L’alternant explique le rôle de chaque élément de la commande.
    - Il identifie les contacts de maintien et de sécurité.
    - Il suit le trajet de l’alimentation de la bobine sans se perdre.
    - Il fait le lien entre un défaut de câblage et le symptôme observé.
indices_de_fragilite:
    - Il se trompe régulièrement entre contacts NO et NC.
    - Il ne voit pas l’utilité du relais thermique.
    - Il ne parvient pas à suivre le schéma de commande.
    - Son câblage est désordonné et difficile à relire.
questions_hugo_possibles:
    - Peux-tu me raconter le parcours du courant dans ta boucle de commande ?
    - Comment fais-tu pour être sûr de ne pas inverser NO et NC ?
    - À quoi sert exactement le relais thermique dans ce montage ?
    - Qu’as-tu observé la dernière fois qu’un moteur ne démarrait pas comme prévu ?
mini_cas_probleme: "Après ton câblage, le moteur ne démarre pas ou ne s’arrête plus correctement au bouton arrêt."
mini_cas_situation_interessante: "En analysant le schéma, tu détectes une erreur avant même de mettre sous tension et tu la corriges."
mini_cas_besoin_aide: "Tu as du mal à faire le lien entre le schéma de commande et ce que tu vois physiquement dans l’armoire."
- situation_id: S12
titre: Tirer et fixer des chemins de câbles
bloc: realisation
contexte_entreprise:
    - Plateaux tertiaires avec nombreux câbles
    - Atelier de production léger
    - Local technique avec plusieurs armoires
description_courte:
    - L’alternant installe des chemins de câbles pour supporter des faisceaux de conducteurs.
    - Il trace, fixe les supports, pose les éléments et prépare le futur tirage.
ce_que_l_apprenant_fait:
    - Repère le parcours des chemins de câbles à partir des plans ou des consignes.
    - Mesure et marque les points de fixation sur les murs ou plafonds.
    - Pose les consoles, tiges filetées et éléments de cheminement.
    - Contrôle l’horizontalité, la continuité et les distances avec les autres réseaux.
savoirs_mobilises:
    - Lecture de plans de cheminement simples.
    - Utilisation d’outils de perçage, fixation et mesure.
    - Règles de distance avec d’autres réseaux (eau, gaz, données).
    - Notions de dilatation et de charges admissibles.
savoir_faire_observables:
    - Sait prendre des cotes et reporter les axes de cheminement.
    - Sait choisir et poser les ancrages adaptés au support.
    - Sait assembler et niveler les éléments de chemin de câbles.
    - Sait vérifier l’accessibilité pour le futur tirage et la maintenance.
connaissances_sous_jacentes:
    - Contraintes mécaniques supportées par les chemins de câbles.
    - Effets des vibrations, de la chaleur et de la dilatation.
    - Importance des distances de sécurité avec certains réseaux.
    - Rôle du chemin de câbles dans la pérennité de l’installation.
erreurs_frequentes:
    - Mauvaise prise de cotes entraînant des décalages.
    - Fixations sous-dimensionnées ou inadaptées au support.
    - Non-respect des distances avec d’autres canalisations.
    - Trajectoires compliquées rendant le tirage difficile.
risques_et_vigilances:
    - Chute ou affaissement du chemin de câbles en charge.
    - Détérioration de câbles à cause d’arêtes vives ou de contraintes.
    - Difficulté d’accès pour maintenance ou modifications.
    - Non-conformité aux exigences de sécurité du site.
indices_de_comprehension:
    - L’alternant anticipe où et comment passer les câbles.
    - Il choisit des fixations adaptées au type de mur ou de plafond.
    - Il contrôle régulièrement son alignement et ses niveaux.
    - Il signale les points où le chemin risque d’être surchargé.
indices_de_fragilite:
    - Il perce et fixe sans vérifier l’alignement global.
    - Il ne se préoccupe pas des autres réseaux présents.
    - Il ne pense pas au tirage futur des câbles.
    - Il utilise toujours les mêmes fixations sans tenir compte du support.
questions_hugo_possibles:
    - Comment décides-tu du meilleur parcours pour un chemin de câbles ?
    - Quels contrôles fais-tu avant de percer et de fixer un support ?
    - Comment sais-tu que ton chemin supportera bien les câbles prévus ?
    - Qu’as-tu déjà observé comme problème sur des chemins mal posés ?
mini_cas_probleme: "Après la pose, tu découvres qu’un virage trop serré empêche le passage d’un gros câble."
mini_cas_situation_interessante: "En discutant avec ton tuteur, tu proposes un parcours plus simple et plus accessible que celui envisagé au départ."
mini_cas_besoin_aide: "Tu dois poser un chemin de câbles au-dessus d’autres réseaux et tu ne sais pas quelles distances respecter ni quels supports choisir."

