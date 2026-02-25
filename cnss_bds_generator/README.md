# Module CNSS BDS Generator — Odoo 18.0

## Présentation

Module Odoo 18.0 de génération des fichiers **BDS (Bordereau de Déclaration de Salaires)** CNSS,
conformément au **Cahier des Charges CNSS v2 / Février 2006** pour le portail **Damancom (e-BDS)**.

---

## Prérequis

- Odoo 18.0
- Module `hr_payroll` (OCA l10n_ma_payroll recommandé)
- Python 3.10+

---

## Installation

1. Copier le dossier `cnss_bds_generator` dans votre répertoire `addons` Odoo.
2. Mettre à jour la liste des modules : **Paramètres → Activer le mode développeur → Mettre à jour la liste des modules**.
3. Chercher **"CNSS BDS"** et cliquer **Installer**.

---

## Configuration

### 1. Configurer l'Affilié CNSS

**CNSS - Télédéclaration → Configuration → Affiliés CNSS**

- **Numéro Affilié** : 7 chiffres (validé algorithmiquement selon le cahier des charges)
- **Raison Sociale**, **Activité**, **Adresse**, **Code Agence**

### 2. Configurer les Employés

Dans chaque fiche employé (onglet **Informations Privées**), renseigner :
- **N° Immatriculation CNSS** (validé selon l'algorithme CNSS)
- **Enfants (droits AF)**
- **N° CIN**
- **Statut CNSS** : Actif / Sortant / Nouveau / Occasionnel

---

## Utilisation

### Flux de travail

```
Préétabli CNSS (fichier A00..A03)
        ↓
Créer Déclaration → Importer Bulletins → Vérifier/Corriger → Confirmer → Générer BDS → Déposer sur Damancom
```

### Étape 1 : Créer une Déclaration

**CNSS - Télédéclaration → Déclarations BDS → Nouveau**

- Sélectionner l'**Affilié CNSS**
- Choisir **Année** et **Mois**
- Saisir l'**Identifiant Transfert** (copier depuis le fichier préétabli CNSS, champ A00)
- Vérifier les **dates** d'émission et d'exigibilité

### Étape 2 : Importer les Bulletins de Paie

Cliquer **"Importer Bulletins de Paie"** pour lancer l'assistant :

1. Vérifier la **période** et le **code règle salariale** (`GROSS` ou votre code brut)
2. Ajuster le **plafond CNSS** (600 000 centimes = 6 000 MAD par défaut)
3. Cliquer **"Rechercher les Bulletins"**
4. Vérifier l'aperçu, ajuster si nécessaire
5. Cliquer **"Importer dans la Déclaration"**

> Les employés avec statut "Nouveau/Entrant" sont automatiquement placés dans la section **Entrants**.

### Étape 3 : Compléter les données AF (Allocations Familiales)

Dans l'onglet **Assurés Existants**, renseigner depuis le préétabli CNSS :
- **AF à Payer**, **AF à Déduire** (si applicables)
- **AF à Reverser** (≤ AF Net à Payer)

> ⚠️ Pour les situations **Sorti (SO)** et **Décédé (DE)**, l'AF à reverser = AF net à payer.

### Étape 4 : Vérifier et Corriger

- Vérifier les **situations** (SO, DE, IT, IL, AT, CS, MS, MP)
- Contrôler que le **salaire plafonné** ≤ salaire réel ET ≤ plafond CNSS
- Vérifier que le nombre de **jours** ≤ 26

### Étape 5 : Générer le Fichier BDS

1. Cliquer **"Confirmer"** → valide les données
2. Cliquer **"Générer Fichier BDS"**
3. Le fichier `.txt` est créé et téléchargeable

**Nom du fichier généré :**
- Principale : `DS_NNNNNNN_MMAAAA.txt`
- Complémentaire : `DSC[N]_NNNNNNN_MMAAAA.txt`

### Étape 6 : Déposer sur Damancom

Déposer le fichier sur [https://www.damancom.ma](https://www.damancom.ma)
dans votre espace privé → Télédéclaration.

---

## Structure du Fichier BDS Généré

| Enregistrement | Type   | Description                        |
|---------------|--------|------------------------------------|
| B00           | AN(3)  | Nature du fichier                  |
| B01           | AN(3)  | Entête globale                     |
| B02 (×n)      | AN(3)  | Détail assurés existants           |
| B03           | AN(3)  | Récapitulatif existants            |
| B04 (×n)      | AN(3)  | Détail entrants                    |
| B05           | AN(3)  | Récapitulatif entrants             |
| B06           | AN(3)  | Récapitulatif global               |

Chaque enregistrement : **260 caractères** + saut de ligne (ASCII 10).

---

## Contrôles automatiques

- ✅ Validation numéro affilié (algorithme clé de contrôle)
- ✅ Validation numéro immatriculation CNSS (algorithme C9)
- ✅ Vérification du salaire plafonné ≤ salaire réel
- ✅ Vérification jours ≤ 26
- ✅ Contrôle AF à reverser ≤ AF net à payer
- ✅ Cohérence situations (CS/MS → jours et salaires nuls)
- ✅ Calcul automatique des totaux horizontaux (CTR)
- ✅ Calcul automatique des totaux verticaux (B03, B05, B06)
- ✅ Détection des doublons de numéros d'immatriculation

---

## Codes Situation

| Code | Libellé                     | Jours/Sal |
|------|-----------------------------|-----------|
| ''   | Normale (travail effectif)  | Obligatoires |
| SO   | Sortant                     | Nuls       |
| DE   | Décédé                      | Nuls       |
| IT   | Maternité                   | Optionnels |
| IL   | Maladie                     | Optionnels |
| AT   | Accident de Travail         | Optionnels |
| CS   | Congé Sans Salaire          | Nuls       |
| MS   | Maintenu Sans Salaire       | Nuls       |
| MP   | Maladie Professionnelle     | Nuls       |

---

## Support et Évolutions

- Conformité : Cahier des Charges CNSS v2 / Février 2006
- Portail cible : Damancom (e-BDS)
