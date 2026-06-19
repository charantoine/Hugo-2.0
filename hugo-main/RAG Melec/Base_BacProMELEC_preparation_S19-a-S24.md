<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Tâche :

À partir des situations ci‑dessous issues du catalogue Bac Pro MELEC, produis des fiches de base de connaissance prêtes à être utilisées par Hugo (tuteur réflexif AFEST) en RAG.

liste de situations :

S19 mise_en_service Tester un circuit d’éclairage avec télérupteur bâtiment / tertiaire Combine logique de commande multipoints et vérifications avant remise au client. Confusion entre poussoirs et interrupteurs, mauvais repérage des navettes, difficultés à suivre le schéma.​
S20 mise_en_service Valider le fonctionnement d’un petit variateur moteur industrie légère Relie câblage de puissance, commande et réglages de base (sens, rampes, sécurité). Mauvais paramétrage des seuils, méconnaissance des messages défaut, confusion entre commande locale/distance.​
S21 maintenance Rechercher une panne sur un circuit d’éclairage bâtiment Situation très fréquente en dépannage, développe démarche de diagnostic et vérification étape par étape. Vouloir réparer avant de comprendre, ne pas isoler la zone en défaut, interpréter trop vite les mesures.​
S22 maintenance Dépanner une prise qui ne fonctionne plus bâtiment / tertiaire Cas classique d’appel client, oblige à vérifier protections, continuité, serrage, usure du matériel. Se limiter à l’appareillage sans remonter au tableau, oublier les tests de base (voyant, multimètre).​
S23 maintenance Remplacer un disjoncteur divisionnaire bâtiment / tertiaire Combine diagnostic, choix du bon calibre, intervention en sécurité dans un tableau existant. Mauvaise identification du circuit, choix d’un calibre inadapté, oubli de resserrer les connexions voisines.​
S24 maintenance Faire l’entretien visuel d’un tableau électrique tous contextes Apprend à repérer échauffements, étiquettes manquantes, câbles abîmés, serrages douteux. Ne pas voir les signes faibles (légère décoloration, odeur), survoler sans méthode, oublier de consigner.

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

- situation_id: S19
titre: Tester un circuit d’éclairage avec télérupteur
bloc: mise_en_service
contexte_entreprise:
    - Parties communes d’immeuble d’habitation
    - Couloirs ou escaliers de petit tertiaire
    - Locaux techniques avec plusieurs points de commande
description_courte:
    - L’alternant vérifie le fonctionnement d’un circuit d’éclairage commandé par télérupteur.
    - Il teste tous les poussoirs et luminaires avant la remise au client.
ce_que_l_apprenant_fait:
    - Observe le schéma de câblage du télérupteur, des poussoirs et des luminaires.
    - Actionne chaque poussoir pour vérifier l’allumage et l’extinction de l’éclairage.
    - Contrôle le câblage des navettes ou fils de commande si un défaut apparaît.
    - Note les anomalies éventuelles et propose des pistes de recherche.
savoirs_mobilises:
    - Schéma de principe d’un télérupteur avec plusieurs poussoirs.
    - Différence entre interrupteur, poussoir et télérupteur.
    - Reconnaissance des conducteurs de phase, neutre, retour lampe et commande.
    - Utilisation simple d’un multimètre ou d’un vérificateur.
savoir_faire_observables:
    - Sait repérer les bornes de commande et de puissance sur le télérupteur.
    - Sait distinguer les poussoirs des interrupteurs sur le terrain.
    - Sait tester logiquement chaque point de commande.
    - Sait suivre une navette ou un fil de commande dans une boîte.
connaissances_sous_jacentes:
    - Principe de mémoire du télérupteur (changement d’état à chaque impulsion).
    - Impact d’un mauvais repérage des poussoirs ou navettes.
    - Rôle de la phase de commande et du retour lampe.
    - Lien entre schéma multifilaire et implantation réelle.
erreurs_frequentes:
    - Monter des interrupteurs à la place de poussoirs.
    - Inverser les fils de commande et de puissance.
    - Oublier un poussoir dans les tests de fonctionnement.
    - Se tromper dans le suivi des navettes dans les boîtes.
risques_et_vigilances:
    - Éclairage qui ne s’éteint plus ou ne s’allume pas selon les poussoirs.
    - Mécontentement des occupants dans les parties communes.
    - Difficulté de dépannage si le câblage est peu lisible.
    - Risque de travailler sous tension lors de corrections mal préparées.
indices_de_comprehension:
    - L’alternant explique clairement la différence entre poussoir et interrupteur.
    - Il prévoit un ordre logique pour tester tous les points de commande.
    - Il fait le lien entre l’anomalie constatée et une zone probable de défaut.
    - Il utilise le schéma comme support pour sa recherche.
indices_de_fragilite:
    - Il confond systématiquement poussoirs et interrupteurs.
    - Il teste au hasard sans méthode ni repérage.
    - Il ne sait pas localiser le télérupteur dans l’installation.
    - Il se perd dès qu’il y a plusieurs navettes et boîtes de dérivation.
questions_hugo_possibles:
    - Comment reconnais-tu un poussoir par rapport à un interrupteur sur le terrain ?
    - Quelle est ta méthode pour tester un circuit à télérupteur avec plusieurs commandes ?
    - Où irais-tu chercher en premier si l’éclairage ne réagit pas à un poussoir précis ?
    - Comment le schéma peut-il t’aider à ne pas te perdre dans les navettes ?
mini_cas_probleme: "Un des poussoirs n’a aucun effet sur l’éclairage alors que les autres fonctionnent normalement."
mini_cas_situation_interessante: "En suivant les navettes à partir du schéma, tu identifies un mauvais raccordement dans une boîte de dérivation."
mini_cas_besoin_aide: "Tu dois tester un télérupteur avec plusieurs poussoirs et tu ne sais pas dans quel ordre t’y prendre ni où regarder en cas de défaut."
- situation_id: S20
titre: Valider le fonctionnement d’un petit variateur moteur
bloc: mise_en_service
contexte_entreprise:
    - Petite machine en atelier d’industrie légère
    - Ventilation ou pompe commandée par variateur
    - Banc d’essai ou convoyeur à vitesse réglable
description_courte:
    - L’alternant met en service un variateur pour moteur et vérifie son fonctionnement.
    - Il contrôle câblage, sens de rotation, rampes d’accélération et sécurités simples.
ce_que_l_apprenant_fait:
    - Vérifie le câblage puissance entre variateur et moteur.
    - Contrôle les entrées de commande (marche/arrêt, vitesse) selon le schéma.
    - Paramètre quelques réglages de base : sens, rampes, fréquence maximale.
    - Lance des essais en surveillant le comportement du moteur et les messages affichés.
savoirs_mobilises:
    - Lecture simplifiée d’une notice de variateur.
    - Compréhension des entrées de commande locales et à distance.
    - Notions de base sur fréquence, vitesse et sens de rotation.
    - Interprétation élémentaire de codes défaut ou messages d’alarme.
savoir_faire_observables:
    - Sait vérifier que le moteur tourne dans le bon sens.
    - Sait adapter une rampe d’accélération trop brutale.
    - Sait distinguer commande locale au clavier et commande externe.
    - Sait réagir à un message défaut simple (surcharge, surchauffe).
connaissances_sous_jacentes:
    - Lien entre fréquence de sortie et vitesse du moteur asynchrone.
    - Rôle des protections intégrées du variateur.
    - Effet d’un mauvais paramétrage sur la mécanique entraînée.
    - Différence entre arrêt contrôlé et coupure brutale.
erreurs_frequentes:
    - Mauvais choix entre mode commande locale ou distante.
    - Paramètres laissés par défaut inadaptés à l’application.
    - Méconnaissance ou mauvaise lecture des codes défaut.
    - Essais réalisés sans surveiller courant, bruit ou vibrations.
risques_et_vigilances:
    - Montage mécanique endommagé par démarrage trop brutal.
    - Surchauffe moteur ou déclenchements répétés.
    - Arrêts intempestifs gênant la production.
    - Risque pour l’opérateur si les sécurités ne sont pas prises en compte.
indices_de_comprehension:
    - L’alternant peut expliquer la différence entre commande locale et distance.
    - Il ajuste les rampes et la vitesse en fonction de l’usage.
    - Il remarque un comportement anormal (bruit, vibration, échauffement).
    - Il consulte la notice ou la liste des défauts en cas de problème.
indices_de_fragilite:
    - Il manipule les paramètres au hasard sans comprendre leur effet.
    - Il ne distingue pas les différents modes de commande.
    - Il ignore les messages d’erreur ou se contente de les effacer.
    - Il ne se sent pas concerné par l’impact mécanique des réglages.
questions_hugo_possibles:
    - Comment sais-tu si ton variateur est en mode commande locale ou distante ?
    - Quels réglages modifies-tu en priorité lors d’une première mise en service ?
    - Que regardes-tu ou écoutes-tu pendant les premiers essais du moteur ?
    - Comment réagis-tu face à un message défaut que tu ne connais pas ?
mini_cas_probleme: "Le moteur part d’un coup très brusquement à pleine vitesse dès que tu donnes l’ordre de marche."
mini_cas_situation_interessante: "En discutant avec l’opérateur, tu ajustes les rampes et la vitesse pour améliorer le confort et la sécurité."
mini_cas_besoin_aide: "Tu dois valider un variateur avec plusieurs menus et paramètres et tu ne comprends pas bien la logique des réglages proposés."
- situation_id: S21
titre: Rechercher une panne sur un circuit d’éclairage
bloc: maintenance
contexte_entreprise:
    - Logement individuel ou collectif
    - Bureaux avec éclairage classique
    - Parties communes d’immeuble
description_courte:
    - L’alternant intervient sur un circuit d’éclairage qui ne fonctionne plus ou mal.
    - Il suit une démarche de diagnostic avant de remplacer des éléments.
ce_que_l_apprenant_fait:
    - Recueille les informations sur la panne auprès de l’utilisateur.
    - Vérifie l’état des lampes, interrupteurs, protections au tableau.
    - Réalise des mesures simples (tension, continuité) aux bons endroits.
    - Localise la zone de défaut probable avant toute réparation définitive.
savoirs_mobilises:
    - Lecture simplifiée du schéma du circuit concerné.
    - Utilisation sécurisée d’un multimètre ou d’un VAT.
    - Méthode de recherche de panne par étapes (du général au détail).
    - Différenciation entre panne d’alimentation, de commande ou du luminaire.
savoir_faire_observables:
    - Sait isoler une partie du circuit à tester.
    - Sait choisir la mesure adaptée (tension ou continuité).
    - Sait formuler une hypothèse de panne avant d’agir.
    - Sait vérifier son hypothèse en contrôlant la zone ciblée.
connaissances_sous_jacentes:
    - Logique de fonctionnement d’un circuit d’éclairage simple ou va-et-vient.
    - Lien entre défaut d’alimentation et déclenchement de protection.
    - Notion de continuité de circuit et de point de coupure possible.
    - Importance de la sécurité pendant la recherche de panne.
erreurs_frequentes:
    - Remplacer directement la lampe ou l’interrupteur sans diagnostic.
    - Tester au hasard sans ordre ni méthode.
    - Ne pas isoler électriquement la zone avant certaines interventions.
    - Interpréter trop vite une mesure sans vérifier les conditions.
risques_et_vigilances:
    - Risque d’électrisation lors de mesures ou manipulations.
    - Perte de temps et de matériel en remplaçant des pièces encore bonnes.
    - Panne non résolue ou qui revient rapidement.
    - Perte de confiance du client dans la compétence de l’intervenant.
indices_de_comprehension:
    - L’alternant décrit clairement sa démarche avant de commencer.
    - Il explique ses choix de mesures et d’outils.
    - Il vérifie le résultat après intervention pour s’assurer de la résolution.
    - Il sait dire ce qu’il ferait différemment la prochaine fois.
indices_de_fragilite:
    - Il démonte sans avoir compris comment le circuit fonctionne.
    - Il change plusieurs éléments à la fois sans savoir lequel était en cause.
    - Il se perd dans le schéma et n’ose pas demander de l’aide.
    - Il ne sait pas expliquer comment il est arrivé à sa conclusion.
questions_hugo_possibles:
    - Quelles sont tes toutes premières questions quand on t’appelle pour une panne d’éclairage ?
    - Comment choisis-tu le premier point où tu vas mesurer ?
    - Qu’est-ce qui te permet de dire que ta panne est vraiment résolue ?
    - Peux-tu décrire une panne où tu as appris quelque chose d’important sur ta méthode ?
mini_cas_probleme: "Après avoir changé la lampe et l’interrupteur, le luminaire ne fonctionne toujours pas et tu ne sais plus quoi vérifier."
mini_cas_situation_interessante: "En suivant une démarche par étapes, tu identifies un domino mal serré dans une boîte de dérivation comme origine de la panne."
mini_cas_besoin_aide: "Tu te retrouves devant un montage va-et-vient avec plusieurs boîtes et tu n’arrives pas à décider où commencer ta recherche."
- situation_id: S22
titre: Dépanner une prise qui ne fonctionne plus
bloc: maintenance
contexte_entreprise:
    - Logement occupé
    - Bureau avec postes de travail informatiques
    - Local de service ou atelier léger
description_courte:
    - L’alternant intervient sur une prise de courant hors service.
    - Il contrôle l’ensemble du circuit, du tableau jusqu’à la prise.
ce_que_l_apprenant_fait:
    - Interroge l’utilisateur sur le contexte de la panne (depuis quand, avec quel appareil).
    - Vérifie au tableau l’état du disjoncteur, du différentiel et des autres prises du circuit.
    - Réalise des tests simples à la prise (voyant, multimètre, continuité).
    - Ouvre l’appareillage si nécessaire pour vérifier connexions et conducteurs.
savoirs_mobilises:
    - Lecture rapide des repérages de circuits au tableau.
    - Utilisation d’un vérificateur de prise ou d’un multimètre.
    - Méthodologie pour distinguer panne locale ou panne de circuit.
    - Connaissance des signes d’usure ou d’échauffement sur une prise.
savoir_faire_observables:
    - Sait vérifier si d’autres prises du même circuit fonctionnent.
    - Sait interpréter un test de tension ou de polarité.
    - Sait inspecter et resserrer une connexion de prise en sécurité.
    - Sait décider quand remonter au tableau pour poursuivre le diagnostic.
connaissances_sous_jacentes:
    - Structure typique d’un circuit prises (bouclage éventuel, boîtes).
    - Liens entre surcharge, échauffement et usure des appareillages.
    - Rôle du différentiel en cas de défaut vers la terre.
    - Importance du serrage des connexions pour la fiabilité.
erreurs_frequentes:
    - Se concentrer uniquement sur la prise visible sans vérifier le reste du circuit.
    - Oublier de contrôler l’état des protections au tableau.
    - Manipuler la prise sans couper ou vérifier l’absence de tension.
    - Remplacer directement la prise sans chercher la cause du défaut.
risques_et_vigilances:
    - Risque d’électrisation lors de l’ouverture de la prise.
    - Risque de laisser un point de chauffe non traité sur une autre prise.
    - Panne récurrente si l’origine (surcharge, mauvais serrage) n’est pas traitée.
    - Mécontentement du client si la panne revient rapidement.
indices_de_comprehension:
    - L’alternant explique pourquoi il vérifie d’abord le tableau.
    - Il distingue clairement si la panne semble locale ou générale au circuit.
    - Il contrôle l’état des conducteurs et des bornes avant de remonter.
    - Il propose, si besoin, de vérifier d’autres prises du même circuit.
indices_de_fragilite:
    - Il démonte la prise sans avoir regardé le tableau.
    - Il ignore les signes d’échauffement ou de brûlure.
    - Il rétablit la tension sans recontrôler sa réparation.
    - Il a du mal à expliquer sa démarche au client ou au tuteur.
questions_hugo_possibles:
    - Quelles vérifications fais-tu systématiquement avant d’ouvrir une prise en panne ?
    - Comment sais-tu qu’il faut chercher plus loin que la seule prise défectueuse ?
    - Qu’est-ce qui te met en alerte quand tu observes l’intérieur d’une prise ?
    - Peux-tu me décrire une panne de prise où tu as dû remonter jusqu’au tableau ?
mini_cas_probleme: "Après avoir remplacé la prise, elle fonctionne un moment puis retombe à nouveau en panne."
mini_cas_situation_interessante: "En inspectant les autres prises du circuit, tu découvres un autre point d’échauffement que tu peux traiter avant la panne."
mini_cas_besoin_aide: "Tu te retrouves face à un circuit de prises complexe avec plusieurs boîtes et tu ne sais pas comment suivre la continuité."
- situation_id: S23
titre: Remplacer un disjoncteur divisionnaire
bloc: maintenance
contexte_entreprise:
    - Tableau domestique en habitation
    - Petit tableau tertiaire dans un bureau ou commerce
    - Local technique d’un petit bâtiment
description_courte:
    - L’alternant remplace un disjoncteur divisionnaire défectueux ou inadapté.
    - Il doit identifier le bon circuit, choisir le calibre adapté et intervenir en sécurité.
ce_que_l_apprenant_fait:
    - Identifie le circuit concerné grâce au repérage ou aux informations du client.
    - Coupe l’alimentation du tableau et vérifie l’absence de tension.
    - Dépose le disjoncteur, contrôle l’état des conducteurs et du peigne.
    - Installe le nouveau disjoncteur, reconnecte et resserre toutes les bornes utiles.
savoirs_mobilises:
    - Lecture du repérage de circuits et des calibres en place.
    - Connaissance des calibres usuels et de leur usage.
    - Utilisation sécurisée d’un testeur d’absence de tension.
    - Techniques de raccordement sur peigne d’alimentation.
savoir_faire_observables:
    - Sait choisir un calibre cohérent avec le circuit concerné.
    - Sait démonter et remonter un disjoncteur sans abîmer les conducteurs.
    - Sait vérifier et resserrer les connexions voisines au passage.
    - Sait tester le bon fonctionnement du circuit après remplacement.
connaissances_sous_jacentes:
    - Lien entre calibre du disjoncteur, section de câble et usage du circuit.
    - Rôle du disjoncteur dans la protection contre les surintensités.
    - Impact d’un mauvais serrage sur l’échauffement du tableau.
    - Notions de sélectivité minimale avec le disjoncteur général.
erreurs_frequentes:
    - Mauvaise identification du circuit à remplacer.
    - Choix d’un calibre trop élevé ou trop faible.
    - Oubli de resserrer les bornes du nouveau disjoncteur et des voisins.
    - Intervention sans coupure ni vérification de l’absence de tension.
risques_et_vigilances:
    - Risque d’électrisation lors de la dépose ou repose.
    - Risque de surchauffe ou d’incendie en cas de mauvais calibre ou serrage.
    - Mauvaise protection des appareils ou des conducteurs.
    - Dysfonctionnement d’autres circuits si le peigne est mal repositionné.
indices_de_comprehension:
    - L’alternant justifie son choix de calibre par rapport au circuit.
    - Il vérifie plusieurs fois l’absence de tension avant d’agir.
    - Il prend le temps de contrôler les serrages alentours.
    - Il teste le circuit et observe le comportement après remise sous tension.
indices_de_fragilite:
    - Il se fie uniquement à ce qu’on lui dit sans vérifier le circuit.
    - Il choisit un disjoncteur « parce qu’il est disponible ».
    - Il ne vérifie pas ses serrages ni le bon positionnement du peigne.
    - Il ne fait pas de test fonctionnel après son intervention.
questions_hugo_possibles:
    - Comment t’assures-tu que tu remplaces bien le bon disjoncteur ?
    - Sur quels critères choisis-tu le calibre du nouveau disjoncteur ?
    - Quelles vérifications fais-tu avant de remettre le tableau sous tension ?
    - Peux-tu raconter une intervention où le serrage des bornes a été un point clé ?
mini_cas_probleme: "Après remplacement du disjoncteur, un échauffement apparaît au niveau du peigne ou des bornes."
mini_cas_situation_interessante: "En profitant du remplacement, tu détectes et corriges plusieurs connexions desserrées sur la même rangée."
mini_cas_besoin_aide: "Tu hésites entre plusieurs calibres possibles pour un circuit peu repéré et tu ne sais pas comment trancher."
- situation_id: S24
titre: Faire l’entretien visuel d’un tableau électrique
bloc: maintenance
contexte_entreprise:
    - Tableau principal d’un petit immeuble
    - Tableau d’atelier ou de local technique
    - Tableau domestique lors d’une visite de contrôle
description_courte:
    - L’alternant réalise un contrôle visuel systématique d’un tableau en service.
    - Il recherche des signes d’échauffement, de vieillissement ou de mauvais serrage.
ce_que_l_apprenant_fait:
    - Coupe ou sécurise selon la procédure définie, puis ouvre le tableau.
    - Inspecte l’état des appareillages, des conducteurs et des repérages.
    - Recherche traces de chauffe, décolorations, odeurs ou câbles abîmés.
    - Note ses observations, propose si besoin des actions correctives.
savoirs_mobilises:
    - Lecture et compréhension du repérage général du tableau.
    - Connaissance des signes visuels d’échauffement ou de défaut.
    - Méthode d’observation systématique rangée par rangée.
    - Notions de consignation ou de mise en sécurité adaptées au contexte.
savoir_faire_observables:
    - Sait observer sans toucher quand le tableau reste partiellement sous tension.
    - Sait repérer étiquettes manquantes, câbles abîmés, bornes surchargées.
    - Sait sentir ou détecter une odeur suspecte d’échauffement.
    - Sait rendre compte clairement de ses observations au tuteur ou au client.
connaissances_sous_jacentes:
    - Effet du temps, des vibrations et des cycles de charge sur les serrages.
    - Lien entre échauffement localisé et risque d’incendie.
    - Importance d’un repérage durable pour les interventions futures.
    - Rôle de la maintenance préventive dans la fiabilité de l’installation.
erreurs_frequentes:
    - Survoler le tableau sans méthode, en oubliant des zones.
    - Ne pas voir les signes faibles (légère décoloration, petites fissures).
    - Confondre un simple vieillissement esthétique avec un vrai défaut.
    - Oublier de consigner ou de noter ce qui a été observé.
risques_et_vigilances:
    - Risque d’électrisation si l’on manipule au lieu d’observer.
    - Passer à côté d’un défaut sérieux qui pourrait évoluer en échauffement.
    - Mauvaise traçabilité des anomalies constatées.
    - Sous-estimation de l’urgence d’une intervention corrective.
indices_de_comprehension:
    - L’alternant suit une méthode d’observation structurée.
    - Il repère spontanément les points anormaux et les signale.
    - Il distingue ce qui est esthétique de ce qui est dangereux.
    - Il propose, si besoin, un contrôle de serrage ou des mesures complémentaires.
indices_de_fragilite:
    - Il regarde rapidement sans focaliser sur les détails importants.
    - Il ne sait pas quoi chercher précisément dans un tableau.
    - Il hésite à signaler un doute par peur de se tromper.
    - Il ne garde aucune trace de ce qu’il a observé.
questions_hugo_possibles:
    - Quand tu ouvres un tableau, qu’est-ce que tu regardes en premier ?
    - Quels sont pour toi les signes qui doivent alerter tout de suite ?
    - Comment t’organises-tu pour ne rien oublier dans ton inspection ?
    - Peux-tu me raconter une fois où tu as repéré un défaut avant qu’il ne devienne grave ?
mini_cas_probleme: "Lors d’une visite, tu n’as rien signalé et quelques semaines plus tard un échauffement important est découvert sur le tableau."
mini_cas_situation_interessante: "En repérant une légère décoloration, tu lances une vérification de serrage qui met en évidence une borne très desserrée."
mini_cas_besoin_aide: "On te demande de faire un contrôle visuel complet d’un grand tableau et tu ne sais pas comment t’y prendre pour rester méthodique."

