document.addEventListener('DOMContentLoaded', function() {
    const voteInputs = document.querySelectorAll('.vote-input');
    voteInputs.forEach(input => {
        input.addEventListener('input', function() {
            const votes = parseInt(this.value) || 0;
            const cost = votes * votes;
            const proposalId = this.dataset.proposalId;
            const costSpan = document.getElementById('cost-' + proposalId);
            if (costSpan) {
                costSpan.textContent = cost;
            }
        });
    });
});