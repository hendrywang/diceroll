const playerHand = document.getElementById('playerHand');
const bankerHand = document.getElementById('bankerHand');
const playerScore = document.getElementById('playerScore');
const bankerScore = document.getElementById('bankerScore');
const result = document.getElementById('result');
const dealButton = document.getElementById('dealButton');
const resetButton = document.getElementById('resetButton');
const balanceElement = document.getElementById('balance');
const bankerBetInput = document.getElementById('bankerBet');
const playerBetInput = document.getElementById('playerBet');
const tieBetInput = document.getElementById('tieBet');
const gameHistoryBody = document.querySelector('#gameHistory tbody');

function initializeGame() {
    // Initialize game history table
    for (let i = 0; i < 8; i++) {
        const row = gameHistoryBody.insertRow();
        for (let j = 0; j < 40; j++) {
            row.insertCell();
        }
    }
}

function displayCard(card, container) {
    const cardElement = document.createElement('div');
    cardElement.className = 'card';
    cardElement.textContent = `${card.value}${suitEmojis[card.suit]}`;
    container.appendChild(cardElement);
    return cardElement;
}

function updateResult(resultText, netWinLoss) {
    const netWinLossText = netWinLoss >= 0 ? `+$${netWinLoss.toFixed(2)}` : `-$${Math.abs(netWinLoss).toFixed(2)}`;
    const netWinLossColor = netWinLoss >= 0 ? 'green' : 'red';
    result.innerHTML = `${resultText} <span style="color: ${netWinLossColor}">${netWinLossText}</span>`;
}

function updateGameHistory(resultColor) {
    const row = gameCount % 8;
    const cell = gameHistoryBody.rows[row].cells[currentColumn];
    cell.style.backgroundColor = resultColor;
    
    gameCount++;
    if (gameCount % 8 === 0) {
        currentColumn++;
        if (currentColumn >= 40) {
            currentColumn = 0;
        }
    }
}

function resetGame() {
    playerHand.innerHTML = '';
    bankerHand.innerHTML = '';
    playerScore.textContent = '0';
    bankerScore.textContent = '0';
    result.textContent = '';
    bankerBetInput.value = '0';
    playerBetInput.value = '0';
    tieBetInput.value = '0';
}

function updateBetInput(input, amount) {
    input.value = Math.max(0, parseInt(input.value) + amount);
}

// Expose functions to be used in other files
window.initializeGame = initializeGame;
window.displayCard = displayCard;
window.updateResult = updateResult;
window.updateGameHistory = updateGameHistory;
window.resetGame = resetGame;
window.updateBetInput = updateBetInput;
