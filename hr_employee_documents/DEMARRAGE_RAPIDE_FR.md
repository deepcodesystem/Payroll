# 🚀 DÉMARRAGE RAPIDE - Gestion des Documents Employés

## Bienvenue! 👋

Vous avez installé le module **Gestion des Documents Employés** pour Odoo 18.0.
Ce guide vous aidera à commencer en 5 minutes!

---

## ⚡ Étapes Rapides (5 minutes)

### Étape 1: Vérifier l'Installation ✓
1. Allez à **Applications > Mettre à jour la liste**
2. Recherchez "Employee Document Management"
3. Confirmez que le module est **Installé** (vert)

### Étape 2: Accéder au Module
1. Allez à **Ressources Humaines** dans le menu
2. Vous verrez une nouvelle option: **Documents Employés**
3. Cliquez sur **Documents** pour voir la liste

### Étape 3: Créer Votre Premier Document
1. Cliquez sur le bouton **Créer**
2. Remplissez le formulaire:
   - **Employé**: Sélectionnez un employé
   - **Type de Document**: "Work Certificate"
   - **Titre**: "Attestation de Travail 2024"
   - **Fichier**: Cliquez pour télécharger un PDF
3. Cliquez sur **Enregistrer**

### Étape 4: Approuver le Document
1. Cliquez sur **Soumettre pour Approbation**
2. Le statut devient: **En attente d'approbation**
3. Cliquez sur **Approuver**
4. Le document est maintenant visible pour l'employé!

### Étape 5: L'Employé Peut Télécharger
1. Employé se connecte
2. Va à **Ressources Humaines > Employés > Mon Profil**
3. Clique sur l'onglet **Documents**
4. Voit le document approuvé
5. Clique sur **Télécharger** pour obtenir le fichier

---

## 📚 Types de Documents (Prédéfinis)

Le module inclut 7 types de documents prêts à l'emploi:

| Type | Code | Description |
|------|------|-------------|
| 📄 Attestation de Travail | WORK_CERT | Certificat d'emploi officiel |
| 🎓 Certificat d'Expérience | EXP_CERT | Preuve d'expérience professionnelle |
| 💰 Certificat de Salaire | SALARY_CERT | Preuve de revenu/salaire |
| 🏫 Certificat de Formation | TRAINING_CERT | Documents de formation professionnelle |
| 🏥 Dossier Médical | MEDICAL_REC | Documents médicaux |
| 📊 Évaluation de Performance | PERF_REVIEW | Évaluation annuelle |
| 📎 Autres Documents | OTHER | Documents divers |

**Besoin d'un autre type?** Allez à **Documents > Types de Documents** et créez-en un!

---

## 👥 Rôles et Permissions

### Gestionnaire RH (HR Manager)
- ✓ Créer et modifier tous les documents
- ✓ Approuver/Rejeter les documents
- ✓ Gérer les types de documents
- ✓ Voir tous les documents
- ✓ Voir les notes internes

### Agent RH (HR Officer)
- ✓ Créer et modifier les documents
- ✓ Gérer les documents
- ✓ Voir la plupart des documents

### Manager
- ✓ Voir les documents des collaborateurs
- ✓ Modifier les documents des collaborateurs
- ✓ Soumettre pour approbation

### Employé
- ✓ Voir ses propres documents approuvés
- ✓ Télécharger ses documents

---

## 🔄 Flux de Travail Principal

```
1. CRÉER (Brouillon)
   ↓
2. SOUMETTRE (En attente d'approbation)
   ↓
3. APPROUVER (Approuvé) ✓
   OU
   REJETER (Rejeté) ✗
   ↓
4. VISIBLE À L'EMPLOYÉ
   ↓
5. EMPLOYÉ PEUT TÉLÉCHARGER
```

---

## ❓ Questions Fréquentes

### Q: Où trouver les documents que j'ai créés?
**A:** Allez à **Ressources Humaines > Documents Employés > Documents**

### Q: Comment changer le statut d'un document?
**A:** Ouvrez le document et utilisez les boutons en haut:
- **Soumettre pour Approbation** (Brouillon → En attente)
- **Approuver** (En attente → Approuvé)
- **Rejeter** (En attente → Rejeté)

### Q: Que se passe-t-il si je rejette un document?
**A:** 
1. Vous devez fournir une raison
2. L'employé est notifié (si option activée)
3. Le manager peut réinitialiser au brouillon et réessayer

### Q: L'employé peut-il voir les documents rejetés?
**A:** Non, seulement les documents approuvés et visibles

### Q: Comment les dates d'expiration fonctionnent?
**A:**
1. Remplissez la date d'expiration lors de la création
2. Le système détecte automatiquement les documents expirés
3. Un indicateur rouge apparaît
4. Vous pouvez filter par documents expirés

### Q: Puis-je télécharger plusieurs documents à la fois?
**A:** Pas encore, mais vous pouvez les créer rapidement un par un

---

## 🔍 Recherche et Filtrage

### Filtres Rapides Disponibles
- **Brouillon**: Documents non soumis
- **En Attente d'Approbation**: Documents attendant validation
- **Approuvés**: Documents validés
- **Rejetés**: Documents refusés
- **Expirés**: Documents ayant dépassé leur date

### Grouper par:
- **Employé**: Voir les documents par employé
- **Type**: Voir les documents par catégorie
- **Statut**: Voir les documents par état
- **Manager**: Voir les documents par manager

### Chercher par:
- **Nom**: Titre du document
- **Employé**: Nom de l'employé
- **Type**: Catégorie du document
- **Date**: Date de création ou expiration

---

## 📊 Générer un Rapport

### Créer un rapport PDF:
1. Ouvrez un document ou sélectionnez plusieurs
2. Cliquez sur le bouton **Imprimer** (🖨️)
3. Sélectionnez "Rapport Document Employé"
4. Cliquez sur **Télécharger/Imprimer**

Le rapport inclut:
- Détails du document
- Statut actuel
- Dates (émission, expiration)
- Raison du rejet (si applicable)

---

## ⚙️ Configuration de Base

### 1. Créer un Nouveau Type de Document
1. Allez à **Documents Employés > Types de Documents**
2. Cliquez **Créer**
3. Remplissez:
   - **Nom**: ex. "Assurance Maladie"
   - **Code**: ex. "HEALTH_INS" (unique)
   - **Approbation Requise**: Oui/Non
4. Enregistrez

### 2. Attribuer des Permissions
1. Allez à **Paramètres > Utilisateurs & Entreprises > Utilisateurs**
2. Sélectionnez un utilisateur
3. Dans "Droits d'Accès", assignez:
   - **Ressources Humaines / Manager** (accès complet)
   - **Ressources Humaines / Officier** (gestion documents)
4. Enregistrez

---

## 💡 Conseils et Astuces

### Conseil 1: Organisez par Type
Utilisez les types de documents pour catégoriser
→ Facilite la recherche et le filtrage

### Conseil 2: Utilisez les Notes Internes
Ajoutez des notes uniquement visibles par les managers
→ Pour les commentaires confidentiels

### Conseil 3: Configurez les Approbations
Certains types peuvent ne pas avoir besoin d'approbation
→ Les certificats de formation peuvent être auto-approuvés

### Conseil 4: Suivi des Expirations
Configurez les dates d'expiration pour les documents limités
→ Le système vous alerte automatiquement

### Conseil 5: Groupez Intelligemment
Utilisez le groupage pour surveiller rapidement
→ Groupez par Manager pour voir qui a des documents en attente

---

## 🐛 Résolution de Problèmes

### Problème: "Je ne peux pas créer de documents"
**Solution:**
- Vérifiez que votre utilisateur a le rôle "Manager RH"
- Allez à Paramètres > Utilisateurs, vérifiez votre rôle
- Redémarrez Odoo si vous venez d'être assigné

### Problème: "Le document n'est pas visible à l'employé"
**Solution:**
- Vérifiez que le statut est "Approuvé" (pas "En attente")
- Cochez la case "Visible à l'Employé"
- L'employé doit être connecté pour voir

### Problème: "Le bouton Approuver est gris"
**Solution:**
- Le document doit être en statut "En attente d'approbation"
- Vous devez d'abord cliquer "Soumettre pour Approbation"
- Vous devez avoir le rôle Manager RH

### Problème: "Le fichier est trop volumineux"
**Solution:**
- Réduisez la taille du fichier
- Compressez le PDF
- Vérifiez la limite de taille dans les paramètres Odoo

---

## 📞 Besoin d'Aide?

### Documentation Disponible

| Document | Contenu | Pour Qui |
|----------|---------|----------|
| **README.md** | Guide complet des fonctionnalités | Tous les utilisateurs |
| **INSTALL_GUIDE.md** | Installation et configuration | Administrateurs |
| **QUICK_REFERENCE.txt** | Référence rapide | Utilisateurs finaux |
| **MODULE_STRUCTURE.md** | Architecture technique | Développeurs |
| **CONFIGURATION_EXAMPLES.md** | Exemples de code | Développeurs |

### Accès à la Documentation
1. Ouvrez le fichier **DOCUMENTATION_INDEX.html** dans un navigateur
2. Ou lisez les fichiers .md directement

### Support
- **Email**: support@getap.pro
- **Site Web**: https://www.getap.pro
- **Documentations**: Voir les fichiers dans le module

---

## ✨ Prochaines Étapes

### Après l'installation:
1. ✓ Créer votre premier document (ce guide)
2. → Configurer les types personnalisés
3. → Entraîner votre équipe RH
4. → Mettre en place les workflows
5. → Former les employés à utiliser

### Pour les Administrateurs:
1. Lisez **INSTALL_GUIDE.md** (complet)
2. Configurez les permissions utilisateur
3. Créez les types de documents nécessaires
4. Testez le flux d'approbation

### Pour les Développeurs:
1. Lisez **MODULE_STRUCTURE.md** (architecture)
2. Consultez **CONFIGURATION_EXAMPLES.md** (code)
3. Explorez les tests unitaires
4. Préparez les customisations

---

## 🎉 Félicitations!

Vous êtes prêt à utiliser le module **Gestion des Documents Employés**!

### Rappel Rapide:
```
1️⃣ Créer un document
2️⃣ Soumettre pour approbation
3️⃣ Approuver le document
4️⃣ L'employé peut télécharger!
```

**Bonne utilisation!**

---

*Questions? Consultez les fichiers de documentation ou contactez le support.*

*Module Version: 18.0.1.0.0*
*Par: GetapPRO*
*Licence: LGPL-3*
