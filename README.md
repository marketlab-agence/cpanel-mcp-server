# Serveur Avancé MCP (Master Control Program) pour cPanel

Version 2.0 du serveur MCP, conçue comme une passerelle API complète pour les opérations **WHM (WebHost Manager)** et **cPanel**. Ce serveur fournit une interface sécurisée, unifiée et locale pour gérer l'ensemble de votre environnement d'hébergement, en implémentant directement les fonctionnalités de votre plan d'architecture.

Il est conçu pour les développeurs et les administrateurs qui ont besoin d'automatiser, de scripter et d'intégrer avec cPanel/WHM dans un flux de travail de développement moderne (par exemple, VS Code, CLI, applications personnalisées).


## Architecture Principale

Ce serveur expose deux ensembles principaux de points de terminaison (endpoints) :

1. `/whmapi/*` : Pour les appels directs à l'**API 1 de WHM**. Ceux-ci sont destinés aux tâches administratives au niveau du serveur comme la création de comptes, la gestion des plans d'hébergement et la surveillance du serveur.

2. `/uapi/<user>/*` : Pour les appels à l'**UAPI de cPanel** via un proxy. Cela permet au serveur, en utilisant ses privilèges d'administrateur, d'effectuer des actions en toute sécurité au nom d'un utilisateur cPanel spécifique sans avoir besoin de son mot de passe. C'est la méthode correcte et sécurisée pour l'automatisation au niveau de l'utilisateur.


## Fonctionnalités

- **Passerelle API Double :** Un seul serveur pour contrôler les fonctions de WHM et de cPanel.

- **Sécurisé par Conception :** Votre jeton d'API WHM est stocké en tant que variable d'environnement côté serveur, jamais exposé aux clients.

- **Dynamique & Complet :** Pas besoin de coder en dur les fonctions. Toute fonction de l'API 1 de WHM ou de l'UAPI peut être appelée via les routes dynamiques.

- **Gestion d'Erreurs Robuste :** Traduit les erreurs de l'API cPanel/WHM en réponses JSON standardisées pour un débogage plus facile.

- **Convivial pour les Développeurs :** La journalisation détaillée dans la console montre exactement ce qui est transmis au serveur cPanel/WHM.


## 1. Prérequis

- [Python 3.7+](https://www.python.org/downloads/ "null")

- [Pip](https://pip.pypa.io/en/stable/installation/ "null")

- Un compte WHM avec les permissions pour créer et utiliser des jetons d'API (généralement `root` ou un revendeur avec les ACL appropriées).


## 2. Installation et Configuration

### Étape 1 : Cloner le Dépôt

    git clone <url-de-votre-depot>
    cd <repertoire-du-depot>


### Étape 2 : Créer un Environnement Virtuel

    # Pour macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Pour Windows
    python -m venv venv
    .\venv\Scripts\activate


### Étape 3 : Installer les Dépendances

    pip install -r requirements.txt


### Étape 4 : Configurer les Variables d'Environnement

Ce serveur nécessite les informations d'identification d'un **utilisateur WHM** (comme `root`) qui possède un **Jeton d'API**.

1\. Créer un Jeton d'API WHM :

Connectez-vous à WHM, allez dans WHM -> Development -> Manage API Tokens, et générez un nouveau jeton. Assurez-vous de lui accorder les permissions nécessaires pour les fonctions que vous souhaitez utiliser (pour un accès complet, accordez toutes les permissions). Copiez le jeton immédiatement, car il ne sera pas affiché à nouveau.

2\. Définir les Variables d'Environnement :

Créez un fichier .env à la racine du projet (ce fichier est ignoré par git) ou définissez les variables directement dans votre shell.

    WHM_HOST="[https://nom-hote-votre-serveur.com:2087](https://nom-hote-votre-serveur.com:2087)"
    WHM_USER="root"
    WHM_API_TOKEN="votre_jeton_api_whm_ici"


## 3. Lancer le Serveur

Démarrez le serveur MCP avec cette commande :

    python cpanel_mcp_server.py

Le serveur sera en cours d'exécution sur `http://localhost:5001`.


## 4. Exemples d'Utilisation (CLI avec `curl`)

Tous les exemples utilisent `curl` avec les options `-s` (silencieux) et `| jq` (pour un affichage JSON formaté) pour une sortie plus propre.


### Phase 1 : Administration Centrale du Serveur (API 1 de WHM)

Ces points de terminaison interagissent directement avec WHM pour les tâches au niveau du serveur.


#### Module 1.2 : Gestion du Cycle de Vie des Comptes

- **Lister Tous les Comptes :**

      curl -s "http://localhost:5001/whmapi/listaccts" | jq

- **Créer un Compte cPanel :**

      curl -s -X POST http://localhost:5001/whmapi/createacct \
           -d "username=nouveluser" \
           -d "domain=domaine-nouveluser.com" \
           -d "password=unMotDePasseTresSolide123!" \
           -d "plan=default" | jq

- **Suspendre un Compte :**

      curl -s -X POST http://localhost:5001/whmapi/suspendacct \
           -d "user=nouveluser" \
           -d "reason=Test de suspension" | jq


#### Module 1.3 : Gestion des Plans et des Quotas

- **Lister les Plans d'Hébergement :**

      curl -s "http://localhost:5001/whmapi/listpkgs" | jq

- **Modifier le Quota de Bande Passante :**

      curl -s -X POST http://localhost:5001/whmapi/limitbw \
           -d "user=nouveluser" \
           -d "bwlimit=2048" | jq # En Mégaoctets


### Phase 2 : Gestion au Niveau du Compte (UAPI via Proxy WHM)

Ces points de terminaison effectuent des actions pour un _utilisateur cPanel spécifique_. Remplacez `nouveluser` dans l'URL par le nom d'utilisateur du compte cPanel cible.


#### Module 2.1 : Gestion des Domaines et des DNS

- **Lister les Domaines d'un Utilisateur :**

      curl -s "http://localhost:5001/uapi/nouveluser/DomainInfo/list_domains" | jq


#### Module 2.2 : Gestion des Services de Messagerie

- **Lister les Comptes E-mail d'un Utilisateur :**

      curl -s "http://localhost:5001/uapi/nouveluser/Email/list_pops" | jq

- **Créer un Compte E-mail pour un Utilisateur :**

      curl -s -X POST http://localhost:5001/uapi/nouveluser/Email/add_pop \
           -d "domain=domaine-nouveluser.com" \
           -d "email=test" \
           -d "password=unAutreMotDePasseSolide456!" \
           -d "quota=50" | jq


#### Module 2.3 : Gestion des Bases de Données

- **Créer une Base de Données MySQL pour un Utilisateur :**

      curl -s -X POST http://localhost:5001/uapi/nouveluser/Mysql/create_database \
           -d "name=bddwebapp" | jq

- **Créer un Utilisateur MySQL :**

      curl -s -X POST http://localhost:5001/uapi/nouveluser/Mysql/create_user \
           -d "name=userbdd" \
           -d "password=mdpUserBdd789!" | jq

- **Attribuer les Privilèges d'un Utilisateur à une Base de Données :**

      curl -s -X POST http://localhost:5001/uapi/nouveluser/Mysql/set_privileges_on_database \
           -d "user=userbdd" \
           -d "database=nouveluser_bddwebapp" \
           -d "privileges=ALL PRIVILEGES" | jq

======================EN======================

# **cPanel Advanced Master Control Program (MCP) Server**

Version 2.0 of the MCP server, designed as a comprehensive API Gateway for both **WHM (WebHost Manager)** and **cPanel** operations. This server provides a secure, unified, and local interface to manage your entire hosting environment, directly implementing the features from your architectural plan.

It's built for developers and administrators who need to automate, script, and integrate with cPanel/WHM in a modern development workflow (e.g., VS Code, CLIs, custom applications).


## **Core Architecture**

This server exposes two primary sets of endpoints:

1. /whmapi/\*: For direct **WHM API 1** calls. These are for server-level administrative tasks like creating accounts, managing hosting packages, and monitoring the server.

2. /uapi/\<user>/\*: For proxied **cPanel UAPI** calls. This allows the server, using its admin privileges, to securely perform actions on behalf of a specific cPanel user without needing their password. This is the correct and secure method for user-level automation.


## **Features**

- **Dual API Gateway:** A single server to control both WHM and cPanel functions.

- **Secure by Design:** Your WHM API Token is stored as a server-side environment variable, never exposed to clients.

- **Dynamic & Comprehensive:** No need to hardcode functions. Any WHM API 1 or UAPI function can be called through the dynamic routes.

- **Robust Error Handling:** Translates cPanel/WHM API errors into standardized JSON responses for easier debugging.

- **Developer-Friendly:** Detailed console logging shows exactly what is being forwarded to the cPanel/WHM server.

***


## **1. Prerequisites**

- [Python 3.7+](https://www.python.org/downloads/)

- [Pip](https://pip.pypa.io/en/stable/installation/)

- A WHM account with permissions to create and use API Tokens (usually root or a reseller with appropriate ACLs).


## **2. Setup and Installation**

\



### **Step 1: Clone the Repository**

\


Bash

\


git clone \<your-repository-url>\
cd \<repository-directory>


### **Step 2: Create a Virtual Environment**

\


Bash

\


\# For macOS/Linux\
python3 -m venv venv\
source venv/bin/activate\
\
\# For Windows\
python -m venv venv\
.\venv\Scripts\activate


### **Step 3: Install Dependencies**

\


Bash

\


pip install -r requirements.txt


### **Step 4: Configure Environment Variables**

This server requires credentials for a **WHM user** (like root) that has an **API Token**.

1\. Create a WHM API Token:

Log into WHM, go to WHM -> Development -> Manage API Tokens, and generate a new token. Make sure to grant it the necessary permissions for the functions you want to use (for full access, grant all permissions). Copy the token immediately, as it will not be shown again.

2\. Set Environment Variables:

Create a .env file in the project root (this is git-ignored) or set the variables directly in your shell.

\
\


WHM\_HOST="https\://your-server-hostname.com:2087"\
WHM\_USER="root"\
WHM\_API\_TOKEN="your\_whm\_api\_token\_here"

***


## **3. Running the Server**

Start the MCP server with this command:

Bash

\


python cpanel\_mcp\_server.py

The server will be running on http\://localhost:5001.

***


## **4. Usage Examples (CLI with curl)**

All examples use curl with the -s (silent) and | jq (pretty-print JSON) flags for cleaner output.


### **Phase 1: Core Server Administration (WHM API 1)**

These endpoints interact directly with WHM for server-level tasks.


#### **Module 1.2: Account Lifecycle Management**

- **List All Accounts:**\
  Bash\
  curl -s "http\://localhost:5001/whmapi/listaccts" | jq

- **Create a cPanel Account:**\
  Bash\
  curl -s -X POST http\://localhost:5001/whmapi/createacct \\\
  &#x20;    -d "username=newuser" \\\
  &#x20;    -d "domain=newuserdomain.com" \\\
  &#x20;    -d "password=aVeryStrongPassword123!" \\\
  &#x20;    -d "plan=default" | jq

- **Suspend an Account:**\
  Bash\
  curl -s -X POST http\://localhost:5001/whmapi/suspendacct \\\
  &#x20;    -d "user=newuser" \\\
  &#x20;    -d "reason=Testing suspension" | jq


#### **Module 1.3: Package and Quota Management**

- **List Hosting Packages:**\
  Bash\
  curl -s "http\://localhost:5001/whmapi/listpkgs" | jq

- **Modify Bandwidth Quota:**\
  Bash\
  curl -s -X POST http\://localhost:5001/whmapi/limitbw \\\
  &#x20;    -d "user=newuser" \\\
  &#x20;    -d "bwlimit=2048" | jq # In Megabytes


### **Phase 2: Account-Level Management (UAPI via WHM Proxy)**

These endpoints perform actions for a _specific cPanel user_. Replace newuser in the URL with the target cPanel account's username.


#### **Module 2.1: Domain and DNS Management**

- **List a User's Domains:**\
  Bash\
  curl -s "http\://localhost:5001/uapi/newuser/DomainInfo/list\_domains" | jq


#### **Module 2.2: Email Services Management**

- **List a User's Email Accounts:**\
  Bash\
  curl -s "http\://localhost:5001/uapi/newuser/Email/list\_pops" | jq

- **Create an Email Account for a User:**\
  Bash\
  curl -s -X POST http\://localhost:5001/uapi/newuser/Email/add\_pop \\\
  &#x20;    -d "domain=newuserdomain.com" \\\
  &#x20;    -d "email=test" \\\
  &#x20;    -d "password=anotherStrongPassword456!" \\\
  &#x20;    -d "quota=50" | jq


#### **Module 2.3: Database Management**

- **Create a MySQL Database for a User:**\
  Bash\
  curl -s -X POST http\://localhost:5001/uapi/newuser/Mysql/create\_database \\\
  &#x20;    -d "name=webappdb" | jq

- **Create a MySQL User:**\
  Bash\
  curl -s -X POST http\://localhost:5001/uapi/newuser/Mysql/create\_user \\\
  &#x20;    -d "name=dbuser" \\\
  &#x20;    -d "password=dbUserPass789!" | jq

- **Assign User Privileges to a Database:**\
  Bash\
  curl -s -X POST http\://localhost:5001/uapi/newuser/Mysql/set\_privileges\_on\_database \\\
  &#x20;    -d "user=dbuser" \\\
  &#x20;    -d "database=newuser\_webappdb" \\\
  &#x20;    -d "privileges=ALL PRIVILEGES" | jq
