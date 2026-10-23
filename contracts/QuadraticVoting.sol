// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract QuadraticVoting {
    struct Proposal {
        string title;
        string description;
        int256 totalVotes;               // net votes (positive - negative)
        mapping(address => int256) votes; // user's net vote for this proposal
    }

    Proposal[] public proposals;
    mapping(address => bool) public hasVotedOnProposal; // optional, not strictly needed

    event ProposalCreated(uint256 id, string title);
    event Voted(uint256 proposalId, address voter, int256 votes, uint256 cost);

    function createProposal(string memory _title, string memory _description) public {
        proposals.push();
        Proposal storage p = proposals[proposals.length - 1];
        p.title = _title;
        p.description = _description;
        p.totalVotes = 0;
        emit ProposalCreated(proposals.length - 1, _title);
    }

    function vote(uint256 _proposalId, int256 _votes) public {
        require(_proposalId < proposals.length, "Proposal does not exist");
        int256 cost = _votes * _votes; // quadratic cost (positive)
        // In a full implementation you would deduct credits here,
        // but we keep credits off-chain for simplicity.
        Proposal storage p = proposals[_proposalId];
        int256 previous = p.votes[msg.sender];
        p.votes[msg.sender] = previous + _votes;
        p.totalVotes += _votes;
        emit Voted(_proposalId, msg.sender, _votes, uint256(cost));
    }

    function getProposal(uint256 _id) public view returns (string memory, string memory, int256) {
        require(_id < proposals.length, "Invalid ID");
        Proposal storage p = proposals[_id];
        return (p.title, p.description, p.totalVotes);
    }

    function getVote(uint256 _id, address _voter) public view returns (int256) {
        return proposals[_id].votes[_voter];
    }

    function proposalCount() public view returns (uint256) {
        return proposals.length;
    }
}