<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Tâche :

À partir des situations ci‑dessous issues du catalogue Bac Pro MELEC, produis des fiches de base de connaissance prêtes à être utilisées par Hugo (tuteur réflexif AFEST) en RAG.

liste de situations :

S25 maintenance Diagnostiquer un déclenchement différentiel bâtiment / tertiaire Fait le lien entre défaut d’isolement, courant de fuite et sécurité des personnes, très formateur. Confondre surcharge et défaut d’isolement, ne pas isoler les circuits un par un, interpréter mal les mesures.​
S26 maintenance Changer une source lumineuse spécifique (LED, fluocompacte) bâtiment / tertiaire Tâche fréquente, mais qui permet d’aborder compatibilité, chauffe, durée de vie, économies d’énergie. Ne pas vérifier la compatibilité avec le variateur, manipuler sans couper, oublier les consignes de recyclage.​
S27 communication Expliquer au client une coupure nécessaire bâtiment / tertiaire Situe l’alternant dans la relation client, essentiel pour faire accepter les contraintes techniques. Utiliser un vocabulaire trop technique, ne pas annoncer la durée, oublier de proposer une solution de contournement.​
S28 communication Rendre compte à son tuteur en fin de journée tous contextes Habitue à structurer ce qui a été fait, ce qui reste à faire, les problèmes rencontrés, clé pour le tutorat. Rester vague, oublier les points de blocage, difficulté à parler de ses erreurs ou de ses doutes.​
S29 communication Compléter un bon d’intervention simple tertiaire / domotique Relie l’aspect technique aux traces écrites attendues par l’entreprise et le client. Oublier des infos (heures, matériel utilisé), rédaction peu lisible, description trop floue de l’intervention.​
S30 communication Participer à une réunion de chantier bâtiment / tertiaire Donne une vision globale du projet, des interfaces avec autres corps d’état, des délais et contraintes. Oser prendre la parole, comprendre les termes des autres métiers, retenir les décisions importantes

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

- situation_id: S25
titre: Diagnostiquer un déclenchement différentiel
bloc: maintenance
contexte_entreprise:
    - Logement avec tableau domestique
    - Petit commerce avec plusieurs circuits
    - Bureaux avec équipements informatiques
description_courte:
    - L’alternant intervient sur une installation où un dispositif différentiel déclenche.
    - Il distingue surcharge, court-circuit et défaut d’isolement par une démarche de test.
ce_que_l_apprenant_fait:
    - Recueille les informations sur les circonstances du déclenchement.
    - Observe quels circuits sont protégés par le différentiel concerné.
    - Coupe puis réenclenche progressivement les circuits pour isoler celui en défaut.
    - Réalise des mesures simples d’isolement ou de fuite sur le circuit ciblé.
savoirs_mobilises:
    - Rôle et principe de fonctionnement d’un différentiel.
    - Différence entre défaut d’isolement, surcharge et court-circuit.
    - Utilisation de base d’un multimètre et/ou d’un testeur d’isolement.
    - Méthodologie de recherche de défaut par élimination de circuits.
savoir_faire_observables:
    - Sait identifier le différentiel qui déclenche et les circuits associés.
    - Sait isoler un circuit suspect en coupant uniquement son disjoncteur.
    - Sait tester un appareil ou un tronçon de circuit pour vérifier la fuite.
    - Sait expliquer sa démarche de diagnostic au tuteur ou au client.
connaissances_sous_jacentes:
    - Lien entre courant de fuite vers la terre et déclenchement différentiel.
    - Influence de l’humidité, des vieux appareils ou des câbles abîmés.
    - Importance de ne pas confondre surintensité et défaut d’isolement.
    - Effet de l’addition des petites fuites sur un même différentiel.
erreurs_frequentes:
    - Réarmer le différentiel sans chercher la cause.
    - Mélanger surcharge, court-circuit et défaut d’isolement.
    - Ne pas isoler les circuits un par un pour trouver le responsable.
    - Interpréter de travers les mesures d’isolement ou de continuité.
risques_et_vigilances:
    - Remettre en service une installation dangereuse pour les personnes.
    - Risque de dégâts matériels si un défaut persiste.
    - Pannes répétées générant mécontentement et perte de confiance.
    - Risque de se mettre soi-même en danger si l’on travaille sous tension.
indices_de_comprehension:
    - L’alternant explique clairement ce que mesure un différentiel.
    - Il sait décrire la différence entre surcharge et défaut d’isolement.
    - Il adopte une démarche de tests ordonnée et traçable.
    - Il propose des actions préventives (remplacement, contrôle approfondi).
indices_de_fragilite:
    - Il réarme plusieurs fois sans analyse de la situation.
    - Il confond la fonction du disjoncteur et du différentiel.
    - Il ne sait pas sur quoi brancher son appareil de mesure.
    - Il ne parvient pas à expliquer ce qu’il a fait pour trouver le défaut.
questions_hugo_possibles:
    - Quand un différentiel déclenche, quelles sont tes premières questions ?
    - Comment fais-tu pour savoir si c’est un seul circuit ou plusieurs qui posent problème ?
    - Quelles mesures réalises-tu pour confirmer un défaut d’isolement ?
    - Peux-tu raconter une situation où tu as réussi à trouver l’origine d’un déclenchement ?
mini_cas_probleme: "Un différentiel déclenche à chaque fois qu’on branche un appareil dans la cuisine, mais il tient quand tous les circuits sont coupés."
mini_cas_situation_interessante: "En isolant les circuits un par un, tu identifies un vieux congélateur à l’origine des déclenchements et tu expliques cela au client."
mini_cas_besoin_aide: "Tous les circuits te semblent corrects pris séparément, mais le différentiel déclenche encore dès que plusieurs sont réenclenchés."
- situation_id: S26
titre: Changer une source lumineuse spécifique (LED, fluocompacte)
bloc: maintenance
contexte_entreprise:
    - Couloirs et bureaux en tertiaire
    - Commerces avec éclairage décoratif
    - Logements équipés de variateurs ou détecteurs
description_courte:
    - L’alternant remplace une lampe spécifique (LED, fluocompacte) en tenant compte de la compatibilité.
    - Il prend en compte consommation, chauffe, durée de vie et type de commande.
ce_que_l_apprenant_fait:
    - Identifie le type de lampe en place et son environnement (variateur, détecteur, ballast).
    - Coupe l’alimentation ou sécurise la zone avant intervention.
    - Remplace la source lumineuse par un modèle adapté aux contraintes.
    - Vérifie le bon fonctionnement (intensité, absence de scintillement, compatibilité variateur).
savoirs_mobilises:
    - Différences de base entre halogène, fluocompacte et LED.
    - Notions de puissance, flux lumineux et température de couleur.
    - Compatibilité des LED avec certains variateurs ou détecteurs.
    - Règles de sécurité lors du remplacement (coupure, chaleur résiduelle).
savoir_faire_observables:
    - Sait choisir une lampe de remplacement cohérente avec l’usage.
    - Sait repérer et éviter une incompatibilité évidente (message, scintillement).
    - Sait manipuler les lampes sans les endommager ni se brûler.
    - Sait expliquer au client les différences principales entre anciennes et nouvelles sources.
connaissances_sous_jacentes:
    - Impact du choix de la source sur la consommation d’énergie.
    - Effet d’une incompatibilité sur le comportement lumineux (clignotement, bruit).
    - Notions de base sur le recyclage des sources contenant des composants spécifiques.
    - Relation entre température de couleur et confort visuel.
erreurs_frequentes:
    - Remplacer une lampe sans vérifier la compatibilité avec le variateur.
    - Intervenir sans couper, en pensant que « ce n’est que de l’éclairage ».
    - Jeter les anciennes lampes sans respecter les filières de recyclage.
    - Ne pas vérifier l’effet final sur l’ambiance lumineuse.
risques_et_vigilances:
    - Scintillement gênant voire dangereux pour certains usagers.
    - Échauffement excessif si la lampe n’est pas adaptée au luminaire.
    - Risques liés aux composants des lampes fluocompactes mal traités.
    - Insatisfaction du client si la lumière est trop différente de l’origine.
indices_de_comprehension:
    - L’alternant vérifie toujours le type de commande avant de choisir la lampe.
    - Il explique au client les changements visibles (couleur, intensité).
    - Il pense à la question du recyclage pour certaines sources.
    - Il repère un comportement anormal et propose un autre choix si besoin.
indices_de_fragilite:
    - Il considère toutes les lampes comme équivalentes.
    - Il remplace sans couper ni se protéger.
    - Il ne s’intéresse pas au rendu lumineux ni au confort.
    - Il ne tient pas compte des consignes de recyclage.
questions_hugo_possibles:
    - Comment choisis-tu une lampe de remplacement quand il y a un variateur sur le circuit ?
    - Qu’est-ce qui te fait dire qu’une lampe est compatible ou non avec l’installation ?
    - Que regardes-tu après le remplacement pour vérifier que tout va bien ?
    - Comment expliques-tu au client la différence entre deux types de lampes ?
mini_cas_probleme: "Après remplacement d’halogènes par des LED, le client se plaint d’un fort scintillement quand il baisse la lumière."
mini_cas_situation_interessante: "En proposant une autre référence de LED, tu supprimes le clignotement et améliores la consommation."
mini_cas_besoin_aide: "On te demande de remplacer toutes les lampes d’un couloir avec variateur, mais tu ne sais pas quelles références choisir."
- situation_id: S27
titre: Expliquer au client une coupure nécessaire
bloc: communication
contexte_entreprise:
    - Intervention dans un logement occupé
    - Dépannage en bureau pendant les heures d’ouverture
    - Travaux dans un petit commerce
description_courte:
    - L’alternant annonce et justifie une coupure de courant avant d’intervenir.
    - Il explique les raisons techniques, la durée estimée et les impacts pour l’utilisateur.
ce_que_l_apprenant_fait:
    - Prévient le client qu’une coupure est indispensable pour travailler en sécurité.
    - Explique avec des mots simples ce qu’il va faire et pourquoi la coupure est nécessaire.
    - Donne une estimation de durée et vérifie les contraintes particulières (informatique, froid).
    - Propose, si possible, un moment ou une organisation limitant la gêne.
savoirs_mobilises:
    - Bases de la communication avec un non-spécialiste.
    - Capacité à vulgariser les risques électriques et la sécurité.
    - Notions d’organisation du travail (durée, séquençage, priorités).
    - Prise en compte des besoins de l’activité du client.
savoir_faire_observables:
    - Sait annoncer calmement la nécessité de couper le courant.
    - Sait adapter son vocabulaire au niveau de compréhension du client.
    - Sait vérifier que le client a bien compris les impacts.
    - Sait s’accorder sur un créneau ou une manière de limiter la gêne.
connaissances_sous_jacentes:
    - Raison pour laquelle certaines opérations ne peuvent pas se faire sous tension.
    - Effets possibles d’une coupure sur les équipements (informatique, froid, alarme).
    - Notions de responsabilité en cas de travail non sécurisé.
    - Importance de la confiance entre client et intervenant.
erreurs_frequentes:
    - Utiliser un vocabulaire trop technique incompréhensible.
    - Ne pas annoncer la durée estimée de la coupure.
    - Oublier de demander si des équipements sensibles sont en service.
    - Couper sans prévenir suffisamment à l’avance.
risques_et_vigilances:
    - Mécontentement du client, perte de confiance.
    - Perte de données informatiques ou détérioration de produits.
    - Pression du client poussant à travailler sans coupure en sécurité.
    - Image négative de l’entreprise intervenante.
indices_de_comprehension:
    - L’alternant prend le temps d’expliquer avant d’agir.
    - Il reformule la demande du client pour vérifier la compréhension.
    - Il anticipe les équipements sensibles et propose des solutions.
    - Il reste calme face à une réaction stressée ou pressée du client.
indices_de_fragilite:
    - Il coupe sans prévenir ou se contente d’un mot rapide.
    - Il se réfugie dans le jargon technique en cas de question.
    - Il n’ose pas maintenir la nécessité de la coupure si le client proteste.
    - Il ne pense pas à adapter l’horaire ou l’organisation.
questions_hugo_possibles:
    - Comment expliques-tu à un client qu’il faut couper le courant sans l’inquiéter ?
    - Quelles informations donnes-tu toujours avant d’appuyer sur le disjoncteur ?
    - Comment réagis-tu si le client refuse la coupure au moment prévu ?
    - Peux-tu raconter une situation où ta manière d’expliquer a changé la réaction du client ?
mini_cas_probleme: "Tu coupes sans avoir prévenu que des ordinateurs étaient en cours d’utilisation et le client se fâche."
mini_cas_situation_interessante: "En expliquant clairement les risques, tu obtiens facilement l’accord du client pour une coupure plus longue que prévu."
mini_cas_besoin_aide: "Le client te presse de travailler sans couper et tu ne sais pas comment argumenter sans t’opposer frontalement."
- situation_id: S28
titre: Rendre compte à son tuteur en fin de journée
bloc: communication
contexte_entreprise:
    - Journée de chantier en bâtiment
    - Journée de dépannage en itinérance
    - Journée en atelier de câblage
description_courte:
    - L’alternant fait un retour structuré sur ce qu’il a fait pendant la journée.
    - Il partage les tâches réalisées, les difficultés rencontrées et les points à reprendre.
ce_que_l_apprenant_fait:
    - Note ou mémorise les principales interventions de la journée.
    - Présente à son tuteur les travaux réalisés, seul ou en équipe.
    - Signale les problèmes rencontrés et les questions restées sans réponse.
    - Propose des besoins pour le lendemain (matériel, explications, accompagnement).
savoirs_mobilises:
    - Organisation d’un récit chronologique ou par tâche.
    - Capacité à décrire une situation technique avec des mots simples.
    - Aptitude à parler de ses réussites et de ses erreurs.
    - Notions de priorisation (ce qui est urgent, important, à planifier).
savoir_faire_observables:
    - Sait décrire clairement une intervention sans se perdre dans les détails.
    - Sait identifier et formuler un point de blocage.
    - Sait demander un retour ou un conseil sur une situation vécue.
    - Sait écouter les remarques du tuteur et les noter si besoin.
connaissances_sous_jacentes:
    - Intérêt du retour d’expérience pour progresser.
    - Rôle du tuteur dans l’analyse des pratiques en situation.
    - Lien entre ce qui s’est passé dans la journée et les compétences visées.
    - Importance de la traçabilité pour le suivi de l’alternant.
erreurs_frequentes:
    - Rester très vague sur ce qui a été fait.
    - Oublier de parler des difficultés ou des erreurs.
    - Se focaliser uniquement sur les tâches manuelles sans évoquer la compréhension.
    - Ne pas écouter ou prendre en compte les retours du tuteur.
risques_et_vigilances:
    - Passer à côté de situations très formatrices non analysées.
    - Laisser s’installer des erreurs de méthode.
    - Créer un malentendu sur le niveau d’autonomie réel de l’alternant.
    - Freiner la progression faute de repérage des besoins.
indices_de_comprehension:
    - L’alternant illustre ses propos par des exemples concrets de la journée.
    - Il ose parler de ce qu’il n’a pas compris ou mal réussi.
    - Il fait le lien entre les situations vécues et ce qu’il souhaite travailler.
    - Il revient sur des points abordés précédemment pour montrer l’évolution.
indices_de_fragilite:
    - Il répond par « tout s’est bien passé » sans détails.
    - Il ne mentionne jamais d’erreur ou de doute.
    - Il ne voit pas l’intérêt de ce temps d’échange.
    - Il change de sujet dès que le tuteur pose une question précise.
questions_hugo_possibles:
    - Si tu devais choisir une seule situation marquante aujourd’hui, laquelle serait-ce ?
    - Qu’est-ce qui t’a posé le plus de questions ou de difficultés aujourd’hui ?
    - Sur quoi aimerais-tu être accompagné différemment demain ?
    - Quelle réussite de ta journée aimerais-tu garder en tête pour la suite ?
mini_cas_probleme: "En fin de semaine, ton tuteur découvre une erreur répétée que tu n’avais jamais évoquée dans tes comptes rendus."
mini_cas_situation_interessante: "En parlant d’une panne compliquée rencontrée, tu prends conscience toi-même des étapes de diagnostic que tu as su mener."
mini_cas_besoin_aide: "Tu ne sais pas comment expliquer une situation où tu t’es senti en difficulté sans avoir l’air incompétent."
- situation_id: S29
titre: Compléter un bon d’intervention simple
bloc: communication
contexte_entreprise:
    - Dépannage en tertiaire ou chez un particulier
    - Intervention domotique ponctuelle
    - Petite opération de maintenance préventive
description_courte:
    - L’alternant remplit un bon d’intervention après un travail chez un client.
    - Il y consigne les informations essentielles : lieu, travaux, temps, matériel utilisé.
ce_que_l_apprenant_fait:
    - Renseigne les informations administratives (client, date, lieu, intervenants).
    - Décrit brièvement le motif de l’appel et l’intervention réalisée.
    - Indique la durée d’intervention, le matériel remplacé ou ajouté.
    - Fait signer le client ou valide le document selon la procédure de l’entreprise.
savoirs_mobilises:
    - Lecture et compréhension du modèle de bon d’intervention.
    - Capacité à décrire une intervention technique en quelques lignes claires.
    - Notions de base de traçabilité (qui, quoi, quand, où).
    - Connaissance des éléments nécessaires pour la facturation ou le suivi.
savoir_faire_observables:
    - Sait remplir toutes les rubriques obligatoires sans en oublier.
    - Sait écrire lisiblement et de façon compréhensible pour un non-technicien.
    - Sait distinguer ce qui est utile d’un texte trop long.
    - Sait vérifier le bon d’intervention avant de le faire signer.
connaissances_sous_jacentes:
    - Rôle du bon d’intervention dans la relation client et la facturation.
    - Importance de la trace écrite en cas de contestation ou de retour.
    - Lien entre description technique et compréhension par le service administratif.
    - Notions de responsabilité de l’intervenant vis-à-vis de ce qu’il écrit.
erreurs_frequentes:
    - Oublier de noter les heures ou le temps passé.
    - Négliger de préciser le matériel remplacé ou la référence.
    - Rédiger de manière illisible ou trop technique.
    - Oublier de faire signer le client ou de valider le document.
risques_et_vigilances:
    - Problèmes de facturation ou de paiement.
    - Incompréhensions avec le client sur ce qui a été fait.
    - Difficulté à reprendre un historique lors d’une future intervention.
    - Mise en cause de l’entreprise si le contenu est imprécis ou erroné.
indices_de_comprehension:
    - L’alternant remplit le bon sans qu’on lui redise chaque champ.
    - Il sait adapter son langage au client tout en restant exact techniquement.
    - Il voit l’intérêt de garder une trace de ce qu’il a fait.
    - Il vérifie les informations avant de faire signer.
indices_de_fragilite:
    - Il laisse des cases vides ou met des formules floues (« réparation faite »).
    - Il écrit de façon illisible ou trop codée.
    - Il oublie régulièrement des informations clés comme le temps passé.
    - Il ne comprend pas pourquoi ce document est important.
questions_hugo_possibles:
    - Quelles informations notes-tu toujours en priorité sur un bon d’intervention ?
    - Comment t’assures-tu que le client comprendra ce que tu as écrit ?
    - Peux-tu me montrer un exemple de description d’intervention claire et suffisante ?
    - Que pourrait-il se passer si le bon d’intervention est mal rempli ?
mini_cas_probleme: "Un client conteste la facture en disant que le temps facturé ne correspond pas à ce qui est écrit sur le bon."
mini_cas_situation_interessante: "Grâce à un bon d’intervention bien rempli, ton collègue comprend vite ce qui a été fait lors d’une précédente visite."
mini_cas_besoin_aide: "Tu bloques au moment de rédiger la description de l’intervention, tu ne sais pas si tu dois tout détailler ou faire très court."
- situation_id: S30
titre: Participer à une réunion de chantier
bloc: communication
contexte_entreprise:
    - Chantier de bâtiment avec plusieurs corps d’état
    - Rénovation de locaux tertiaires occupés
    - Aménagement d’un plateau de bureaux
description_courte:
    - L’alternant assiste à une réunion de chantier avec d’autres intervenants.
    - Il écoute, prend des notes et intervient éventuellement sur les points qui concernent l’électricité.
ce_que_l_apprenant_fait:
    - Écoute les informations sur l’avancement, les délais et les contraintes.
    - Repère les sujets qui concernent directement les travaux électriques.
    - Prend des notes sur les décisions qui impactent son travail ou celui de son équipe.
    - Pose des questions simples ou reformule si quelque chose n’est pas clair.
savoirs_mobilises:
    - Bases de la communication orale en groupe.
    - Capacité à identifier les informations importantes pour son métier.
    - Notions de coordination entre les corps d’état (plomberie, cloisons, peinture).
    - Techniques simples de prise de notes utiles (dates, zones, actions à faire).
savoir_faire_observables:
    - Sait repérer les zones ou tâches où l’électricien doit s’adapter.
    - Sait demander une précision quand un point reste flou.
    - Sait restituer à son tuteur ce qu’il a compris de la réunion.
    - Sait garder une attitude professionnelle (écoute, respect du tour de parole).
connaissances_sous_jacentes:
    - Rôle de la réunion de chantier dans l’organisation globale du projet.
    - Impact des décisions (retards, modifications) sur le planning électrique.
    - Interdépendance entre électricité et autres corps de métier.
    - Importance de la communication pour éviter les conflits de planning ou d’emplacement.
erreurs_frequentes:
    - Se mettre en retrait total sans écouter ni noter.
    - Ne pas oser signaler un problème électrique lié à une autre intervention.
    - Confondre compte rendu détaillé et simples impressions.
    - Oublier de transmettre à l’équipe ce qui a été décidé.
risques_et_vigilances:
    - Mauvaise coordination entraînant des reprises de travaux.
    - Conflits avec d’autres corps d’état (trous rebouchés, gaines coupées).
    - Retards sur le lot électricité faute d’anticipation.
    - Sentiment de mise à l’écart du projet pour l’alternant.
indices_de_comprehension:
    - L’alternant peut expliquer les grandes lignes de ce qui a été décidé.
    - Il identifie clairement ce qui change pour lui ou pour son équipe.
    - Il sait citer un exemple d’interaction avec un autre corps d’état.
    - Il valorise ce moment comme une source d’informations utiles.
indices_de_fragilite:
    - Il sort de réunion sans savoir ce qui a été décidé pour l’électricité.
    - Il ne prend aucune note et oublie rapidement les informations.
    - Il n’ose pas parler même quand un sujet le concerne directement.
    - Il ne transmet pas les éléments clés à son tuteur ou à son équipe.
questions_hugo_possibles:
    - Quand tu sors d’une réunion de chantier, que dois-tu être capable de raconter ?
    - Quelles informations cherches-tu en priorité pour ton travail d’électricien ?
    - Peux-tu donner un exemple où une décision de réunion a changé ton planning ?
    - Qu’est-ce qui t’aiderait à te sentir plus à l’aise pour prendre la parole en réunion ?
mini_cas_probleme: "Après la réunion, les cloisons sont fermées plus tôt que prévu et tu n’as pas passé toutes tes gaines."
mini_cas_situation_interessante: "En posant une question pendant la réunion, tu évites un conflit de passage de câbles avec un autre corps d’état."
mini_cas_besoin_aide: "Tu es présent à une réunion de chantier importante, mais tu n’oses pas demander des précisions sur une décision qui impacte les tableaux électriques."

