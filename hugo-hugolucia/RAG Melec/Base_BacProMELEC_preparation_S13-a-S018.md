

liste de situations :
S13 réalisation Installer une prise RJ45 et la raccorder tertiaire / domotique Relie électricité et réseaux VDI, de plus en plus demandé dans logements connectés et bureaux. Mauvais ordre de brins, rayon de courbure non respecté, écrasement du câble, test de continuité oublié.​
S14 réalisation Remplacer un appareillage (prise, interrupteur) bâtiment / tertiaire Tâche souvent confiée seul à l’alternant, permet de travailler diagnostic simple, sécurité, finition. Ne pas couper au bon endroit, méconnaître les anciens montages, vis de serrage insuffisantes ou trop serrées.​
S15 mise_en_service Contrôler l’isolement d’une installation neuve bâtiment / tertiaire Étape clé avant mise sous tension, fait le lien entre mesure, norme et sécurité des personnes. Mauvais choix de calibre de mesure, interprétation erronée des valeurs, oublier de déconnecter certains récepteurs.​
S16 mise_en_service Vérifier les continuités de terre tous contextes Renforce la compréhension du rôle de la terre et des liaisons équipotentielles, crucial pour la protection. Oublier certains points (salles d’eau, masses métalliques), mauvaise utilisation de l’ohmmètre, repérage flou.​
S17 mise_en_service Mettre sous tension un petit tableau bâtiment Moment marquant pour l’alternant, demande rigueur dans les dernières vérifications et la gestion des risques. Sauter des étapes de contrôle, précipitation, difficulté à garder une vue d’ensemble des circuits.​
S18 mise_en_service Paramétrer un contacteur jour/nuit ou horloge bâtiment / tertiaire Montre le lien entre programmation simple et économies d’énergie / confort d’usage. Mauvaise compréhension des plages horaires, confusion modes auto/manuel, perte des réglages en cas de coupure.

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

- situation_id: S13
titre: Installer une prise RJ45 et la raccorder
bloc: realisation
contexte_entreprise:
    - Aménagement de bureaux dans un petit tertiaire
    - Installation domotique dans une maison individuelle
    - Rénovation d’un réseau VDI dans un logement récent
description_courte:
    - L’alternant installe une prise RJ45 murale et la raccorde à un câble VDI ou Ethernet.
    - Il doit respecter l’ordre des brins, le rayon de courbure et assurer un contact fiable.
ce_que_l_apprenant_fait:
    - Prépare l’emplacement de la prise et fixe le support adapté.
    - Dégaine le câble, trie les paires torsadées et les positionne dans l’insert.
    - Sertit ou clipse les brins selon le code couleur choisi (T568A ou T568B).
    - Remonte la prise, étiquette le point réseau et réalise un test de continuité ou de liaison.
savoirs_mobilises:
    - Lecture simple d’un plan de réseau VDI ou d’une légende de prises.
    - Connaissance des codes couleurs de câblage RJ45 usuels.
    - Utilisation basique d’un testeur de continuité ou testeur de réseau.
    - Règles de pose d’un câble VDI (rayon de courbure, écrasement, torsade).
savoir_faire_observables:
    - Respecte le code couleur choisi sans inversion de brins.
    - Garde les torsades au plus près des contacts de la prise.
    - Positionne correctement la prise dans son boîtier sans forcer sur le câble.
    - Réalise et interprète un test simple (continuité ou clignotement testeur).
connaissances_sous_jacentes:
    - Rôle des paires torsadées pour limiter les perturbations et assurer le débit.
    - Différence entre câblage téléphonique ancien et câblage RJ45 moderne.
    - Influence de la qualité de raccordement sur la performance du réseau.
    - Notions basiques de catégorie de câble (Cat5e, Cat6) et compatibilité.
erreurs_frequentes:
    - Inverser l’ordre de deux brins ou de deux paires.
    - Trop détoronner les paires et détériorer la performance.
    - Pincer ou écraser le câble derrière la prise.
    - Oublier de faire un test de continuité ou de liaison après raccordement.
risques_et_vigilances:
    - Dysfonctionnements réseau difficiles à diagnostiquer après finition.
    - Perte de débit ou coupures aléatoires ressenties par l’utilisateur.
    - Risque de devoir déposer les finitions pour corriger le câblage.
    - Nécessité de vérifier la compatibilité du type de câble avec l’usage prévu.
indices_de_comprehension:
    - L’alternant explique clairement pourquoi il respecte la torsade des paires.
    - Il choisit et applique un code couleur de manière cohérente sur plusieurs prises.
    - Il prévoit et réalise un test systématique après son câblage.
    - Il remarque et signale un défaut de gaine, d’écrasement ou de rayon trop serré.
indices_de_fragilite:
    - Il confond les codes couleur ou les applique au hasard.
    - Il coupe les paires très longues et les laisse complètement détordues.
    - Il ne voit pas l’intérêt de tester le point réseau après raccordement.
    - Il hésite à manipuler le câble par peur de casser sans savoir pourquoi.
questions_hugo_possibles:
    - Comment choisis-tu le code couleur pour câbler ta prise RJ45 et pourquoi ?
    - Qu’est-ce qui te fait dire que ton raccordement est de bonne qualité avant même le test ?
    - Quelles précautions prends-tu pour éviter d’abîmer le câble lors de la pose ?
    - Que fais-tu si le testeur indique qu’une paire n’est pas correctement reliée ?
mini_cas_probleme: "Après ton raccordement, le poste de travail n’a pas de réseau alors que la box et le switch fonctionnent normalement."
mini_cas_situation_interessante: "En vérifiant une ancienne installation, tu constates un câblage incohérent des prises RJ45 et tu proposes une méthode pour les remettre au propre."
mini_cas_besoin_aide: "Tu te retrouves avec plusieurs codes couleur possibles et tu ne sais plus lequel appliquer pour être cohérent avec le reste de l’installation."
- situation_id: S14
titre: Remplacer un appareillage (prise, interrupteur)
bloc: realisation
contexte_entreprise:
    - Dépannage rapide dans un logement occupé
    - Intervention de maintenance dans un petit bureau
    - Remise à niveau esthétique d’un appartement avant relocation
description_courte:
    - L’alternant remplace un appareillage existant défectueux ou obsolète par un modèle récent.
    - Il doit intervenir en sécurité, identifier le câblage existant et assurer une finition propre.
ce_que_l_apprenant_fait:
    - Identifie le circuit concerné et coupe l’alimentation de manière sûre.
    - Dépose l’appareillage en place en observant le câblage utilisé.
    - Repère les conducteurs (phase, neutre, terre, navettes) et les rebranche sur le nouvel appareil.
    - Remonte l’appareillage, contrôle la tenue mécanique et teste le bon fonctionnement.
savoirs_mobilises:
    - Reconnaissance des différents montages courants (simple allumage, va-et-vient, prise).
    - Connaissance du code couleur des conducteurs usuels.
    - Utilisation sécurisée d’un vérificateur d’absence de tension.
    - Notions de base sur les volumes et les contraintes selon les pièces sensibles.
savoir_faire_observables:
    - Vérifie systématiquement l’absence de tension avant de toucher les conducteurs.
    - Repère et reconnecte correctement chaque conducteur sur le nouvel appareillage.
    - Réalise un serrage adapté des bornes, ni trop faible ni excessif.
    - Laisse un appareillage proprement aligné, sans fils écrasés ni gaines coincées.
connaissances_sous_jacentes:
    - Différence entre phase, neutre, terre et conducteurs de commande.
    - Impact d’un mauvais serrage ou d’un mauvais contact sur l’échauffement.
    - Risques particuliers liés aux anciens montages ou anciens conducteurs.
    - Règles élémentaires de sécurité lors d’une intervention sur installation existante.
erreurs_frequentes:
    - Oublier de couper le bon circuit ou de vérifier l’absence de tension.
    - Rebrancher les conducteurs sans respecter le montage d’origine.
    - Trop serrer les vis et endommager les bornes ou les fils.
    - Laisser des conducteurs dénudés visibles ou mal isolés.
risques_et_vigilances:
    - Risque d’électrisation lors de la dépose ou du remontage.
    - Risque d’échauffement local et de début d’incendie à cause d’un mauvais contact.
    - Dégradation de l’esthétique ou du fonctionnement (appui difficile, prise branlante).
    - Obligation de respecter la compatibilité entre ancien et nouvel appareillage.
indices_de_comprehension:
    - L’alternant explique pourquoi il coupe à tel endroit et comment il vérifie.
    - Il sait décrire le montage rencontré avant de démonter complètement.
    - Il contrôle visuellement et par essai l’appareillage une fois remonté.
    - Il sait repérer un appareillage inadapté à l’emplacement (volume, usage).
indices_de_fragilite:
    - Il manipule les conducteurs alors qu’il n’a pas vérifié l’absence de tension.
    - Il démonte tout sans prendre le temps d’observer le câblage existant.
    - Il serre au hasard sans se soucier du contact ni de l’état du fil.
    - Il se focalise uniquement sur l’aspect esthétique et néglige la sécurité.
questions_hugo_possibles:
    - Quelles sont tes étapes indispensables avant de toucher à un appareillage existant ?
    - Comment fais-tu pour être sûr de rebrancher les conducteurs au bon endroit ?
    - Qu’est-ce qui pourrait te faire douter de la sécurité d’un ancien montage ?
    - Comment réagis-tu si tu découvres un câblage très ancien ou non conforme en démontant ?
mini_cas_probleme: "Après avoir remplacé un interrupteur va-et-vient par un modèle récent, l’éclairage ne fonctionne plus correctement depuis les deux points de commande."
mini_cas_situation_interessante: "En remplaçant une prise, tu découvres des signes d’échauffement et tu proposes de vérifier le reste du circuit avec ton tuteur."
mini_cas_besoin_aide: "Tu dois remplacer un appareillage dans un montage ancien que tu ne reconnais pas et tu n’es pas sûr de comprendre le rôle de chaque conducteur."
- situation_id: S15
titre: Contrôler l’isolement d’une installation neuve
bloc: mise_en_service
contexte_entreprise:
    - Fin de chantier de logement neuf
    - Réfection complète d’un tableau dans un petit tertiaire
    - Ajout de plusieurs circuits dans une installation existante
description_courte:
    - L’alternant réalise un contrôle d’isolement des circuits avant la première mise sous tension.
    - Il utilise un mégohmmètre et interprète les valeurs obtenues pour valider l’installation.
ce_que_l_apprenant_fait:
    - Vérifie que l’installation est hors tension et adaptée au test d’isolement.
    - Déconnecte ou isole les récepteurs sensibles avant la mesure.
    - Relie correctement le mégohmmètre et effectue la mesure sur les différents circuits.
    - Note les valeurs obtenues, compare aux seuils attendus et signale les anomalies.
savoirs_mobilises:
    - Utilisation sécurisée d’un mégohmmètre ou d’une fonction d’isolement sur un appareil de mesure.
    - Connaissance des ordres de grandeur des valeurs d’isolement attendues.
    - Capacité à préparer un circuit pour la mesure (déconnexion de certains équipements).
    - Notions de base sur les documents de contrôle ou PV d’essais.
savoir_faire_observables:
    - Sélectionne le bon calibre de mesure pour l’isolement demandé.
    - Sait où placer les pointes de mesure selon le type de circuit.
    - Compare ses mesures à des valeurs de référence simples.
    - Identifie un circuit suspect et propose une vérification complémentaire.
connaissances_sous_jacentes:
    - Principe de l’isolement entre conducteurs actifs et entre conducteurs et masse.
    - Effet d’un défaut d’isolement sur les déclenchements différentiels ou les échauffements.
    - Rôle des matériaux isolants et des distances d’isolement.
    - Lien entre qualité de pose (écrasement de gaine, humidité) et résultat des mesures.
erreurs_frequentes:
    - Oublier de déconnecter certains récepteurs avant la mesure.
    - Choisir un calibre inadapté ou mal interpréter les indications de l’appareil.
    - Ne pas noter les résultats ou les noter de manière imprécise.
    - Se contenter d’une mesure globale sans vérifier les circuits douteux.
risques_et_vigilances:
    - Détérioration de certains appareils laissés en place pendant la mesure.
    - Mise sous tension ultérieure d’une installation présentant un défaut d’isolement.
    - Déclenchements intempestifs récurrents chez le client.
    - Manque de traçabilité des contrôles réalisés en fin de chantier.
indices_de_comprehension:
    - L’alternant peut expliquer ce qu’il mesure quand il parle d’isolement.
    - Il anticipe les récepteurs à débrancher avant de lancer la mesure.
    - Il repère spontanément une valeur anormale et cherche la cause.
    - Il sait faire le lien entre un défaut d’isolement et un déclenchement différentiel.
indices_de_fragilite:
    - Il lance des mesures sans vérifier l’état de l’installation.
    - Il lit les valeurs sans savoir si elles sont correctes ou non.
    - Il oublie de retirer certains équipements sensibles.
    - Il voit le contrôle d’isolement comme une formalité sans impact réel.
questions_hugo_possibles:
    - Quand tu mesures l’isolement, qu’est-ce que tu cherches à vérifier exactement ?
    - Comment décides-tu qu’une valeur mesurée est acceptable ou non ?
    - Quels équipements penses-tu à protéger ou à déconnecter avant un test d’isolement ?
    - Que ferais-tu si un seul circuit présente une valeur d’isolement douteuse ?
mini_cas_probleme: "Lors du contrôle d’isolement, un circuit affiche une valeur très basse mais tu ne sais pas d’où peut venir le problème."
mini_cas_situation_interessante: "En analysant tes mesures, tu repères un défaut d’isolement dû à un câble pincé derrière un appareillage et tu participes à la correction."
mini_cas_besoin_aide: "Tu dois utiliser un mégohmmètre pour la première fois sur une installation neuve et tu n’es pas sûr des réglages ni de l’interprétation des résultats."
- situation_id: S16
titre: Vérifier les continuités de terre
bloc: mise_en_service
contexte_entreprise:
    - Mise en service d’un tableau domestique
    - Contrôle d’une petite installation tertiaire avant réception
    - Vérification après ajout de prises ou de circuits dans un local
description_courte:
    - L’alternant vérifie la continuité des conducteurs de protection et des liaisons équipotentielles.
    - Il s’assure que toutes les masses métalliques concernées sont correctement reliées à la terre.
ce_que_l_apprenant_fait:
    - Identifie la barrette ou la borne principale de terre de l’installation.
    - Utilise un ohmmètre ou une fonction de test de continuité pour vérifier chaque départ.
    - Contrôle les liaisons vers les masses métalliques (salles d’eau, châssis, canalisations).
    - Note les points conformes et signale les absences ou les valeurs douteuses.
savoirs_mobilises:
    - Utilisation simple d’un ohmmètre ou d’une fonction bip de continuité.
    - Reconnaissance des conducteurs de protection et des bornes de terre.
    - Identification des éléments devant être reliés à la terre ou équipotentiel.
    - Lecture basique de schémas ou de plans de liaisons de terre.
savoir_faire_observables:
    - Relie correctement les pointes de mesure pour tester une continuité de terre.
    - Repère les points où la continuité est interrompue ou douteuse.
    - Réagit en signalant immédiatement un point de terre manquant ou mal serré.
    - Met à jour un repérage ou un croquis pour garder trace des contrôles.
connaissances_sous_jacentes:
    - Rôle de la terre dans la protection des personnes en cas de défaut.
    - Principe de la liaison équipotentielle dans les locaux particuliers (salles d’eau).
    - Effet d’une terre absente ou défaillante sur le fonctionnement des différentiels.
    - Lien entre résistance de la boucle de défaut et niveau de sécurité.
erreurs_frequentes:
    - Oublier des points à contrôler (radiateurs, armoires métalliques, canalisations).
    - Mal utiliser l’ohmmètre (mauvais calibre, mauvais contact des pointes).
    - Confondre conducteurs de protection et d’autres conducteurs.
    - Se contenter d’un contrôle visuel sans vérification de continuité.
risques_et_vigilances:
    - Risque de choc électrique en cas de défaut sur une masse non reliée.
    - Dysfonctionnement des dispositifs différentiels.
    - Mise en service d’une installation non sécurisée pour les occupants.
    - Fausses impressions de sécurité si le contrôle est mal réalisé.
indices_de_comprehension:
    - L’alternant explique pourquoi la terre est essentielle dans une installation.
    - Il pense spontanément à vérifier les éléments métalliques exposés.
    - Il sait interpréter un signal sonore ou une valeur de continuité.
    - Il fait le lien entre une absence de terre et un danger potentiel.
indices_de_fragilite:
    - Il voit la terre comme un simple fil vert/jaune sans rôle précis.
    - Il ne sait pas où placer ses pointes de mesure pour vérifier une continuité.
    - Il oublie des points importants lors de son contrôle.
    - Il ne sait pas quoi faire en cas de continuité absente ou douteuse.
questions_hugo_possibles:
    - Pour toi, à quoi sert exactement la terre dans une installation électrique ?
    - Comment t’organises-tu pour être sûr de ne pas oublier de points à contrôler ?
    - Qu’est-ce qui te mettrait en alerte lors d’un contrôle de continuité de terre ?
    - Que proposes-tu si tu découvres une masse métallique sans liaison de terre ?
mini_cas_probleme: "En fin de chantier, tu découvres qu’un radiateur de salle de bain n’est relié à aucune liaison équipotentielle."
mini_cas_situation_interessante: "Lors d’un contrôle systématique, tu repères une barrette de terre mal serrée et tu en profites pour revoir le rôle de cette barrette avec ton tuteur."
mini_cas_besoin_aide: "On te demande de vérifier toutes les continuités de terre d’un tableau et tu ne sais pas comment t’y prendre de manière méthodique."
- situation_id: S17
titre: Mettre sous tension un petit tableau
bloc: mise_en_service
contexte_entreprise:
    - Fin de montage d’un tableau domestique
    - Rénovation d’un tableau dans un appartement occupé
    - Mise en service d’un tableau dans un petit local tertiaire
description_courte:
    - L’alternant participe à la première mise sous tension d’un tableau après les contrôles préalables.
    - Il applique une procédure d’étapes pour limiter les risques et vérifier le bon fonctionnement.
ce_que_l_apprenant_fait:
    - Revoit avec le tuteur la check-list des contrôles déjà réalisés (isolement, terre, serrage).
    - S’assure que tous les circuits non utilisés ou en attente sont correctement isolés.
    - Met sous tension progressivement (général puis circuits) en observant les réactions.
    - Teste rapidement les principaux circuits pour vérifier l’absence de défaut évident.
savoirs_mobilises:
    - Lecture des repérages de circuits et compréhension de la structure du tableau.
    - Connaissance des étapes de base avant mise sous tension.
    - Utilisation de voyants, testeurs simples et déclenchements éventuels comme indicateurs.
    - Notions d’échanges avec les autres intervenants pour choisir le bon moment de mise sous tension.
savoir_faire_observables:
    - Suit une procédure claire plutôt que de tout réenclencher d’un coup.
    - Observe et interprète les éventuels déclenchements immédiats.
    - Coupe rapidement en cas d’anomalie et alerte le tuteur.
    - Note ou mémorise quels circuits ont été testés et avec quels résultats.
connaissances_sous_jacentes:
    - Conséquences possibles d’une mise sous tension d’une installation non conforme.
    - Rôle du disjoncteur général, des différentiels et des divisionnaires au moment de la mise sous tension.
    - Lien entre les défauts d’isolement, de câblage et les déclenchements.
    - Notions de responsabilité et de sécurité lors de la première mise sous tension.
erreurs_frequentes:
    - Tout réenclencher d’un seul coup sans surveillance.
    - Mettre sous tension alors que certains travaux sont encore en cours sur des circuits.
    - Ignorer un déclenchement en le réarmant sans rechercher la cause.
    - Ne pas vérifier les circuits essentiels (éclairage, prises d’usage) après mise sous tension.
risques_et_vigilances:
    - Risque immédiat pour les personnes présentes si un défaut grave existe.
    - Dommages sur des appareils branchés ou sur l’installation.
    - Perte de confiance du client ou des autres corps d’état.
    - Obligation de refaire une partie du travail si un défaut majeur est découvert trop tard.
indices_de_comprehension:
    - L’alternant peut expliquer pourquoi il préfère remettre sous tension par étapes.
    - Il repère vite un comportement anormal au moment du réenclenchement.
    - Il anticipe quels circuits tester en priorité après la mise sous tension.
    - Il demande à être accompagné lors des premières mises sous tension importantes.
indices_de_fragilite:
    - Il considère la mise sous tension comme un simple « on/off » sans importance particulière.
    - Il ne voit pas la différence entre un déclenchement normal et inquiétant.
    - Il n’a pas de méthode pour suivre quels circuits ont été testés.
    - Il minimise les risques liés à une mise sous tension prématurée.
questions_hugo_possibles:
    - Quelles sont, pour toi, les étapes indispensables avant de mettre un tableau sous tension ?
    - Comment réagis-tu si, dès la mise sous tension, un différentiel déclenche ?
    - Quels circuits vérifierais-tu en premier après la mise sous tension et pourquoi ?
    - À quel moment te sembles-tu avoir besoin d’un accompagnement particulier pour cette étape ?
mini_cas_probleme: "Dès que tu remets le disjoncteur général, un interrupteur différentiel déclenche immédiatement et tu ne sais pas par où commencer."
mini_cas_situation_interessante: "En procédant circuit par circuit, tu identifies rapidement celui qui provoque un défaut et tu participes à sa correction."
mini_cas_besoin_aide: "On te demande de mettre sous tension un tableau que tu n’as pas câblé toi-même et tu n’es pas rassuré sur les contrôles déjà faits."
- situation_id: S18
titre: Paramétrer un contacteur jour/nuit ou horloge
bloc: mise_en_service
contexte_entreprise:
    - Mise en service d’un chauffe-eau en heures creuses dans un logement
    - Programmation d’un éclairage extérieur dans un petit tertiaire
    - Réglage d’un contacteur pour délester ou piloter une charge à certaines heures
description_courte:
    - L’alternant règle un contacteur jour/nuit ou une horloge pour qu’un circuit fonctionne aux bonnes périodes.
    - Il fait le lien entre la programmation, le fonctionnement électrique et le besoin du client.
ce_que_l_apprenant_fait:
    - Identifie le circuit à piloter et le type d’appareil de commande installé.
    - Règle l’heure, les plages de fonctionnement ou les modes automatique / manuel.
    - Vérifie le câblage de commande et le bon basculement du contacteur ou de l’horloge.
    - Teste le fonctionnement en conditions simulées (forçage, changement d’heure).
savoirs_mobilises:
    - Lecture d’une notice simplifiée de contacteur ou d’horloge.
    - Compréhension des modes de fonctionnement (auto, forcé, arrêt).
    - Notions de base sur les signaux de commande (heures creuses, contact EDF, commande locale).
    - Adaptation des plages horaires aux usages réels du client.
savoir_faire_observables:
    - Paramètre correctement les heures et les jours de fonctionnement.
    - Utilise les fonctions de test ou de forçage pour vérifier son réglage.
    - Explique au client ou au tuteur comment changer un réglage simple.
    - Corrige un réglage après avoir constaté un fonctionnement non conforme.
connaissances_sous_jacentes:
    - Lien entre période de fonctionnement et économies d’énergie.
    - Différence entre commande manuelle, automatique et asservie.
    - Impact d’un mauvais réglage sur le confort (eau chaude, éclairage) ou la facture.
    - Influence des changements d’heure ou de tarifs sur la programmation.
erreurs_frequentes:
    - Mauvaise saisie de l’heure ou oubli du changement heure d’été / hiver.
    - Confusion entre mode manuel et automatique.
    - Programmation de plages inversées (marche la nuit au lieu du jour, ou l’inverse).
    - Ne pas vérifier réellement le fonctionnement après réglage.
risques_et_vigilances:
    - Inconfort pour l’utilisateur (pas d’eau chaude, éclairage intempestif).
    - Surconsommation d’énergie si le circuit reste en marche inutilement.
    - Mécontentement du client qui remet en cause le travail de l’équipe.
    - Risque de manipulations ultérieures hasardeuses par l’utilisateur s’il n’a pas compris.
indices_de_comprehension:
    - L’alternant explique clairement la différence entre les modes de l’appareil.
    - Il anticipe un test pour vérifier que la programmation correspond bien au besoin.
    - Il adapte les plages horaires en fonction des habitudes du client.
    - Il est capable de réexpliquer la procédure de réglage de base.
indices_de_fragilite:
    - Il se contente d’un réglage « au hasard » sans tenir compte de l’usage réel.
    - Il s’emmêle dans les boutons et ne sait plus dans quel mode il se trouve.
    - Il oublie de vérifier le fonctionnement réel après programmation.
    - Il est mal à l’aise dès qu’il faut lire une notice ou manipuler un menu.
questions_hugo_possibles:
    - Quand tu règles un contacteur ou une horloge, par quoi commences-tu ?
    - Comment vérifies-tu que la programmation correspond vraiment aux besoins du client ?
    - Qu’est-ce qui te pose le plus de difficultés dans la lecture des notices ?
    - Comment ferais-tu pour expliquer le fonctionnement de ce dispositif à un utilisateur non technicien ?
mini_cas_probleme: "Après ton réglage, le chauffe-eau ne chauffe jamais en heures creuses et le client se plaint de ne plus avoir d’eau chaude."
mini_cas_situation_interessante: "Tu adaptes la programmation d’un éclairage extérieur pour qu’il ne reste plus allumé toute la nuit, et le client constate une baisse de sa consommation."
mini_cas_besoin_aide: "Tu dois programmer une horloge multifonction avec plusieurs plages et tu te perds dans les menus et les modes possibles."

