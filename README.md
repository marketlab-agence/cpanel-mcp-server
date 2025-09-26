cPanel Advanced Master Control Program (MCP) ServerVersion 2.0 of the MCP server, designed as a comprehensive API Gateway for both WHM (WebHost Manager) and cPanel operations. This server provides a secure, unified, and local interface to manage your entire hosting environment, directly implementing the features from your architectural plan.It's built for developers and administrators who need to automate, script, and integrate with cPanel/WHM in a modern development workflow (e.g., VS Code, CLIs, custom applications).Core ArchitectureThis server exposes two primary sets of endpoints:/whmapi/*: For direct WHM API 1 calls. These are for server-level administrative tasks like creating accounts, managing hosting packages, and monitoring the server./uapi/<user>/*: For proxied cPanel UAPI calls. This allows the server, using its admin privileges, to securely perform actions on behalf of a specific cPanel user without needing their password. This is the correct and secure method for user-level automation.FeaturesDual API Gateway: A single server to control both WHM and cPanel functions.Secure by Design: Your WHM API Token is stored as a server-side environment variable, never exposed to clients.Dynamic & Comprehensive: No need to hardcode functions. Any WHM API 1 or UAPI function can be called through the dynamic routes.Robust Error Handling: Translates cPanel/WHM API errors into standardized JSON responses for easier debugging.Developer-Friendly: Detailed console logging shows exactly what is being forwarded to the cPanel/WHM server.1. PrerequisitesPython 3.7+PipA WHM account with permissions to create and use API Tokens (usually root or a reseller with appropriate ACLs).2. Setup and InstallationStep 1: Clone the RepositoryBashgit clone <your-repository-url>
cd <repository-directory>
Step 2: Create a Virtual EnvironmentBash# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
Step 3: Install DependenciesBashpip install -r requirements.txt
Step 4: Configure Environment VariablesThis server requires credentials for a WHM user (like root) that has an API Token.1. Create a WHM API Token:Log into WHM, go to WHM -> Development -> Manage API Tokens, and generate a new token. Make sure to grant it the necessary permissions for the functions you want to use (for full access, grant all permissions). Copy the token immediately, as it will not be shown again.2. Set Environment Variables:Create a .env file in the project root (this is git-ignored) or set the variables directly in your shell.WHM_HOST="https://your-server-hostname.com:2087"
WHM_USER="root"
WHM_API_TOKEN="your_whm_api_token_here"
3. Running the ServerStart the MCP server with this command:Bashpython cpanel_mcp_server.py
The server will be running on http://localhost:5001.4. Usage Examples (CLI with curl)All examples use curl with the -s (silent) and | jq (pretty-print JSON) flags for cleaner output.Phase 1: Core Server Administration (WHM API 1)These endpoints interact directly with WHM for server-level tasks.Module 1.2: Account Lifecycle ManagementList All Accounts:Bashcurl -s "http://localhost:5001/whmapi/listaccts" | jq
Create a cPanel Account:Bashcurl -s -X POST http://localhost:5001/whmapi/createacct \
     -d "username=newuser" \
     -d "domain=newuserdomain.com" \
     -d "password=aVeryStrongPassword123!" \
     -d "plan=default" | jq
Suspend an Account:Bashcurl -s -X POST http://localhost:5001/whmapi/suspendacct \
     -d "user=newuser" \
     -d "reason=Testing suspension" | jq
Module 1.3: Package and Quota ManagementList Hosting Packages:Bashcurl -s "http://localhost:5001/whmapi/listpkgs" | jq
Modify Bandwidth Quota:Bashcurl -s -X POST http://localhost:5001/whmapi/limitbw \
     -d "user=newuser" \
     -d "bwlimit=2048" | jq # In Megabytes
Phase 2: Account-Level Management (UAPI via WHM Proxy)These endpoints perform actions for a specific cPanel user. Replace newuser in the URL with the target cPanel account's username.Module 2.1: Domain and DNS ManagementList a User's Domains:Bashcurl -s "http://localhost:5001/uapi/newuser/DomainInfo/list_domains" | jq
Module 2.2: Email Services ManagementList a User's Email Accounts:Bashcurl -s "http://localhost:5001/uapi/newuser/Email/list_pops" | jq
Create an Email Account for a User:Bashcurl -s -X POST http://localhost:5001/uapi/newuser/Email/add_pop \
     -d "domain=newuserdomain.com" \
     -d "email=test" \
     -d "password=anotherStrongPassword456!" \
     -d "quota=50" | jq
Module 2.3: Database ManagementCreate a MySQL Database for a User:Bashcurl -s -X POST http://localhost:5001/uapi/newuser/Mysql/create_database \
     -d "name=webappdb" | jq
Create a MySQL User:Bashcurl -s -X POST http://localhost:5001/uapi/newuser/Mysql/create_user \
     -d "name=dbuser" \
     -d "password=dbUserPass789!" | jq
Assign User Privileges to a Database:Bashcurl -s -X POST http://localhost:5001/uapi/newuser/Mysql/set_privileges_on_database \
     -d "user=dbuser" \
     -d "database=newuser_webappdb" \
     -d "privileges=ALL PRIVILEGES" | jq
