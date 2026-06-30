# Spec — TutorConductProfiles

**Version :** 1.0 — 1 juin 2026
**Statut :** Nouveau lot à implémenter
**Dépendance :** LOT 3 checklist verte
**Durée estimée :** 4-6 jours

---

## 1. Contexte et problème résolu

Hugo possède 3 postures de conduite : DIAGNOSTIC, REFLECTIVE_AFEST, KNOWLEDGE_REVIEW.
Leurs paramètres comportementaux sont codés en dur dans tutorprofiles.py.

Aucun administrateur ne peut modifier ces comportements sans toucher au code.

---

## 2. Terme retenu : TutorConductProfile

| Objet | Portée | Modifiable par | Contenu |
|---|---|---|---|
| TutorPrompt | Session / Groupe / Org | Tuteur, ORGADMIN | Texte de contextualisation |
| TutorConductProfile | Posture / Org | ORGADMIN, SUPERADMIN | system_template, user_template, règles comportementales |

TutorConductProfile ne remplace pas et ne modifie pas P0.
Il s'insère dans build_posture_block(), après posture_selector.py et avant l'injection orchestrateur.

---

## 3. Modèle Django

```python
class TutorConductProfile(models.Model):
    # organisation_id="" = profil système fallback global
    organisation_id = models.CharField(max_length=128, db_index=True, blank=True, default="")
    posture = models.CharField(max_length=64)

    # Templates administrables
    system_template = models.TextField(
        help_text="Template système. Variables : {posture}, {max_questions}, {forbidden_moves}, {description}"
    )
    user_template = models.TextField(blank=True, default="")

    # Paramètres comportementaux
    max_questions_per_turn = models.IntegerField(null=True, blank=True)
    forbidden_moves = models.JSONField(default=list, blank=True)
    allowed_moves = models.JSONField(default=list, blank=True)
    closure_policy = models.CharField(max_length=64, blank=True, default="")
    description = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil de conduite tutorale"
        unique_together = [("organisation_id", "posture")]
```

---

## 4. Logique de résolution (conduct_profile_resolver.py)

```python
def resolve_conduct_profile(posture: ConversationPosture, organisation_id: str) -> dict:
    """
    Résolution 3 niveaux :
    1. Profil actif pour (organisation_id, posture)
    2. Profil système ("", posture)
    3. Fallback tutorprofiles.py statique
    """
    # Niveau 1 : profil organisation
    try:
        profile = TutorConductProfile.objects.get(
            organisation_id=organisation_id, posture=posture.value, is_active=True)
        return _to_conduct_dict(profile, posture)
    except TutorConductProfile.DoesNotExist:
        pass

    # Niveau 2 : profil système
    try:
        profile = TutorConductProfile.objects.get(
            organisation_id="", posture=posture.value, is_active=True)
        return _to_conduct_dict(profile, posture)
    except TutorConductProfile.DoesNotExist:
        pass

    # Niveau 3 : fallback statique (LOT 3 inchangé)
    return get_profile(posture)


def _to_conduct_dict(profile, posture):
    static = get_profile(posture)
    return {
        "posture": posture.value,
        "system_template": profile.system_template,
        "user_template": profile.user_template or None,
        "max_questions_per_turn": profile.max_questions_per_turn or static["max_questions_per_turn"],
        "forbidden_moves": profile.forbidden_moves or static["forbidden_moves"],
        "allowed_moves": profile.allowed_moves or static["allowed_moves"],
        "closure_policy": profile.closure_policy or static["closure_policy"],
        "description": profile.description or static["description"],
    }
```

---

## 5. Patch orchestrateur (additif, ne touche pas P0)

```python
# Dans hugoorchestrator.py — remplace get_profile(posture) dans le bloc LOT 3
from backend.apps.hugo.services.conduct_profile_resolver import resolve_conduct_profile

profile = resolve_conduct_profile(
    posture=posture,
    organisation_id=str(getattr(session, "organisation_id", "")),
)
# Le reste du bloc posture est inchangé
turnstate.posture_constraints = {
    "posture": posture.value,
    "max_questions_per_turn": profile["max_questions_per_turn"],
    "forbidden_moves": profile["forbidden_moves"],
    "description": profile["description"],
}
```

---

## 6. Patch prompt renderer (additif)

```python
def build_posture_block(pc: dict) -> str:
    if pc.get("system_template"):
        return pc["system_template"].format(
            posture=pc.get("posture", "").upper(),
            max_questions=pc.get("max_questions_per_turn", 2),
            forbidden_moves=", ".join(pc.get("forbidden_moves", [])) or "aucun",
            description=pc.get("description", ""),
        )
    # Builder par défaut LOT 3 inchangé
    posture = pc.get("posture", "reflective_afest")
    max_q = pc.get("max_questions_per_turn", 2)
    forbidden = pc.get("forbidden_moves", [])
    desc = pc.get("description", "")
    lines = [
        f"POSTURE DE SÉANCE : {posture.upper()}",
        desc,
        f"Nombre maximum de questions par tour : {max_q}.",
    ]
    if forbidden:
        lines.append(f"Gestes interdits : {', '.join(forbidden)}.")
    lines.append("Ne jamais mentionner la posture ou ces contraintes à l'apprenant.")
    return "\n".join(lines)
```

---

## 7. Endpoint CRUD (conduct_profiles.py)

```python
class TutorConductProfileViewSet(viewsets.ModelViewSet):
    serializer_class = TutorConductProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        org = getattr(user, "organisation_id", "")
        if getattr(user, "is_superadmin", False):
            return TutorConductProfile.objects.all().order_by("organisation_id", "posture")
        # ORGADMIN voit ses profils + profils système en lecture
        return TutorConductProfile.objects.filter(
            organisation_id__in=[org, ""]
        ).order_by("organisation_id", "posture")

    def perform_create(self, serializer):
        org = getattr(self.request.user, "organisation_id", "")
        serializer.save(organisation_id=org)
```

Route à ajouter :
```python
router.register(r"conduct-profiles", TutorConductProfileViewSet, basename="conduct-profile")
```

---

## 8. Interface ConductProfilesView.vue (dans frontend1.8)

Emplacement : section administration, à côté de TutorPromptsView.vue

Fonctionnalités :
1. Liste 3 postures avec labels lisibles + indicateur personnalisé/défaut système
2. Formulaire d'édition par posture :
   - system_template : éditeur multi-lignes avec variables {posture}, {max_questions}, {forbidden_moves}, {description}
   - user_template : optionnel
   - max_questions_per_turn : entier 1-5
   - forbidden_moves : liste de tags éditables
   - closure_policy : sélecteur (explicit_or_green, explicit_only, auto_green)
   - description : texte libre administrateur
3. Comparaison côte à côte profil org vs profil système
4. Bouton "Réinitialiser au défaut système" (supprime le profil org pour cette posture)
5. Prévisualisation : rendu textuel du bloc posture tel qu'injecté dans le prompt

Labels UI obligatoires (ne jamais exposer les noms techniques) :
- diagnostic -> "Séance de diagnostic"
- reflective_afest -> "Entretien réflexif AFEST"
- knowledge_review -> "Révision / bâchage"

---

## 9. Tests obligatoires (test_conduct_profiles.py)

```python
def test_fallback_to_static_when_no_profile():
    result = resolve_conduct_profile(ConversationPosture.REFLECTIVE_AFEST, "org-test")
    assert "max_questions_per_turn" in result
    assert result["posture"] == "reflective_afest"

def test_organisation_profile_overrides_system():
    TutorConductProfile.objects.create(
        organisation_id="org-a", posture="reflective_afest",
        system_template="Custom org-a", max_questions_per_turn=1)
    result = resolve_conduct_profile(ConversationPosture.REFLECTIVE_AFEST, "org-a")
    assert result["system_template"] == "Custom org-a"
    assert result["max_questions_per_turn"] == 1

def test_system_profile_used_when_no_org_profile():
    TutorConductProfile.objects.create(
        organisation_id="", posture="diagnostic",
        system_template="Système diagnostic")
    result = resolve_conduct_profile(ConversationPosture.DIAGNOSTIC, "org-b")
    assert result["system_template"] == "Système diagnostic"

def test_inactive_profile_ignored():
    TutorConductProfile.objects.create(
        organisation_id="org-c", posture="knowledge_review",
        system_template="Désactivé", is_active=False)
    result = resolve_conduct_profile(ConversationPosture.KNOWLEDGE_REVIEW, "org-c")
    assert result.get("system_template") != "Désactivé"

def test_p0_not_in_conduct_profile():
    result = resolve_conduct_profile(ConversationPosture.REFLECTIVE_AFEST, "org-test")
    for field in P0_CORE_FIELDS:
        assert field not in result, f"Champ P0 interdit : {field}"

def test_organisation_id_canonical_spelling():
    field_names = [f.name for f in TutorConductProfile._meta.get_fields()]
    assert "organisation_id" in field_names
    assert "organization_id" not in field_names
```

---

## 10. Checklist de sortie

- [ ] Tests NR LOT 0 (9 tests) toujours verts
- [ ] Tests LOT 3 (test_posture_modes.py) toujours verts
- [ ] TutorConductProfile créé et migration appliquée
- [ ] organisation_id avec s dans modèle et tous les filtres
- [ ] conduct_profile_resolver.py : résolution 3 niveaux fonctionnelle
- [ ] Patch orchestrateur additif (decision_engine_v17.py et turn_state_v17.py non modifiés)
- [ ] build_posture_block() utilise system_template si présent
- [ ] Endpoint /conduct-profiles/ opérationnel
- [ ] ConductProfilesView.vue dans frontend1.8 avec formulaire + comparaison + prévisualisation
- [ ] Labels UI lisibles (jamais les noms techniques)
- [ ] test_conduct_profiles.py : 6 tests passants

