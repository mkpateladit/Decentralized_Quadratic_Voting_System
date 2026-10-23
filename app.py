from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import json
import os
from web3 import Web3

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"

# --- Blockchain connection ---
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # or 8545
if not w3.is_connected():
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

with open("build/QuadraticVoting.abi", "r") as f:
    contract_abi = json.load(f)
with open("build/contract_address.txt", "r") as f:
    contract_address = f.read().strip()

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
w3.eth.default_account = w3.eth.accounts[0]  # Use first Ganache account for transactions

# --- Database setup ---
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            credits INTEGER DEFAULT 100
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_user_credits(username):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT credits FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 100

def update_user_credits(username, new_credits):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (username, credits) VALUES (?, ?)", (username, new_credits))
    conn.commit()
    conn.close()

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        if request.method == "POST":
            username = request.form["username"]
            session["username"] = username
            # Ensure user exists
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (username, credits) VALUES (?, 100)", (username,))
            conn.commit()
            conn.close()
            return redirect(url_for("index"))
        return render_template("login.html")

    username = session["username"]
    credits = get_user_credits(username)

    # Fetch proposals from smart contract
    count = contract.functions.proposalCount().call()
    proposals = []
    for i in range(count):
        title, desc, total_votes = contract.functions.getProposal(i).call()
        user_vote = contract.functions.getVote(i, w3.eth.accounts[0]).call()  # simplified: same account for all
        proposals.append({
            "id": i,
            "title": title,
            "description": desc,
            "total_votes": total_votes,
            "user_vote": user_vote,
        })

    return render_template("index.html", proposals=proposals, credits=credits, username=username)

@app.route("/create", methods=["GET", "POST"])
def create():
    if "username" not in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["description"]
        tx_hash = contract.functions.createProposal(title, desc).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        flash("Proposal created on blockchain!", "success")
        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/vote/<int:proposal_id>", methods=["POST"])
def vote(proposal_id):
    if "username" not in session:
        return redirect(url_for("index"))
    username = session["username"]
    votes = int(request.form["votes"])  # can be negative
    cost = votes * votes

    current_credits = get_user_credits(username)
    if cost > current_credits:
        flash("Not enough credits!", "danger")
        return redirect(url_for("index"))

    # Send transaction to smart contract
    tx_hash = contract.functions.vote(proposal_id, votes).transact()
    w3.eth.wait_for_transaction_receipt(tx_hash)

    # Deduct credits off-chain (credits are managed in SQLite)
    update_user_credits(username, current_credits - cost)
    flash(f"Voted {votes} (cost: {cost} credits). Transaction mined!", "success")
    return redirect(url_for("index"))

@app.route("/results")
def results():
    count = contract.functions.proposalCount().call()
    proposals = []
    for i in range(count):
        title, desc, total_votes = contract.functions.getProposal(i).call()
        proposals.append({
            "id": i,
            "title": title,
            "description": desc,
            "total_votes": total_votes,
        })
    return render_template("results.html", proposals=proposals)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)