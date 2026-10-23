Decentralized Quadratic Voting Governance Platform

A full-stack web application that lets users vote on governance proposals using Quadratic Voting (QV). Proposals and votes are recorded on a local Ethereum blockchain (Ganache) through a Solidity smart contract, while user credits are tracked in SQLite.

What is Quadratic Voting?

Each voter receives a fixed pool of credits and "buys" votes at a rising price:

Cost = Votes²
Votes	1	2	3	4	5
Credits	1	4	9	16	25

Strong preferences are possible, but dominating a vote becomes expensive, so minorities keep a voice on the issues they care about most. Votes can be positive (support) or negative (oppose).

Features
Mock wallet login: sign in with a username or wallet address and receive 100 governance credits.
Proposal creation: any user can submit a proposal with a title and description, stored on-chain.
Quadratic voting interface: enter positive or negative votes and see the credit cost update live before submitting.
Results dashboard: view the net votes for every proposal.
Tech Stack
Layer	Technology
Backend	Python, Flask
Blockchain	Solidity (^0.8.0), Web3.py, Ganache
Database	SQLite (user credits)
Frontend	Jinja templates, Tailwind CSS, JavaScript
Tooling	py-solc-x (contract compilation), python-dotenv
Project Structure
quadratic-governance-blockchain/
├── app.py                    # Flask app and routes
├── requirements.txt          # Python dependencies
├── database.db               # SQLite database (user credits)
├── contracts/
│   └── QuadraticVoting.sol   # Smart contract
├── scripts/
│   └── deploy.py             # Compiles and deploys the contract to Ganache
├── build/                    # Generated: ABI, bytecode, contract address
├── templates/
│   ├── base.html             # Layout with Tailwind CSS
│   ├── login.html            # Mock wallet login
│   ├── index.html            # Proposals and voting interface
│   ├── create.html           # New proposal form
│   └── results.html          # Results dashboard
└── static/js/script.js       # Client-side live cost calculation
Prerequisites
Python 3.9 or newer
Ganache (desktop app or ganache-cli) running locally
Internet access on first run (py-solc-x downloads the Solidity 0.8.0 compiler)
Setup and Run
Create and activate a virtual environment
bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Mac / Linux
   source venv/bin/activate
Install dependencies
bash
   pip install -r requirements.txt
Start Ganache so a local blockchain is available at http://127.0.0.1:7545 (Ganache desktop) or http://127.0.0.1:8545 (ganache-cli). The app tries 7545 first, then 8545.
Deploy the smart contract
bash
   python scripts/deploy.py

This compiles contracts/QuadraticVoting.sol and writes the ABI, bytecode and contract address into build/.

Run the application
bash
   python app.py
Open http://127.0.0.1:5000 in your browser.

Re-run python scripts/deploy.py whenever you restart Ganache with a fresh chain, since the contract address changes.

How to Use
Enter a username or mock wallet address on the login page. You receive 100 credits.
Browse active proposals on the home page, or click + New Proposal to create one.
Enter the number of votes (positive to support, negative to oppose). The cost is shown instantly as votes².
Click Vote. If you have enough credits, the vote is sent to the smart contract and the cost is deducted from your balance.
Open Results to see the net votes per proposal.
Application Routes
Route	Method	Description
/	GET, POST	Login page / proposals and voting dashboard
/create	GET, POST	Create a new proposal
/vote/<proposal_id>	POST	Submit votes on a proposal
/results	GET	Results dashboard
/logout	GET	End the session
Limitations and Future Work
User credits are stored off-chain in SQLite; moving credit accounting into the smart contract would make it fully trustless.
Transactions are signed with the default Ganache account, so the contract does not yet separate vote history per user. Integrating MetaMask would give each voter their own wallet identity.
The results page shows net votes only; adding a standard-vote vs quadratic-vote comparison chart would highlight the effect of QV.
Deploying to an Ethereum testnet (e.g. Sepolia) would move the project beyond local simulation.
Before any real deployment, replace the hard-coded Flask secret_key in app.py with a value loaded from an environment variable.
License

This project is for educational purposes.
