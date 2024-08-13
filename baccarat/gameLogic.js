let balance = 1000;
let gameCount = 0;
let currentColumn = 0;

const suitEmojis = {
    'hearts': '❤️',
    'diamonds': '♦️',
    'clubs': '♣️',
    'spades': '♠️'
};

async function fetchCards(count) {
    const response = await fetch(`http://localhost:3040/draw?count=${count}`);
    const data = await response.json();
    return data.cards;
}

function calculateHandValue(hand) {
    let value = 0;
    for (const card of hand) {
        if (['J', 'Q', 'K', '10'].includes(card.value)) {
            value += 0;
        } else if (card.value === 'A') {
            value += 1;
        } else {
            value += parseInt(card.value);
        }
    }
    return value % 10;
}

function shouldBankerDraw(bankerValue, playerThirdCardValue) {
    if (bankerValue <= 2) return true;
    if (bankerValue === 3 && playerThirdCardValue !== '8') return true;
    if (bankerValue === 4 && ['2', '3', '4', '5', '6', '7'].includes(playerThirdCardValue)) return true;
    if (bankerValue === 5 && ['4', '5', '6', '7'].includes(playerThirdCardValue)) return true;
    if (bankerValue === 6 && ['6', '7'].includes(playerThirdCardValue)) return true;
    return false;
}

function validateBets() {
    const totalBet = parseInt(bankerBetInput.value) + parseInt(playerBetInput.value) + parseInt(tieBetInput.value);
    if (totalBet > balance) {
        alert('Total bet cannot exceed your balance!');
        return false;
    }
    if (totalBet === 0) {
        alert('Please place a bet before dealing!');
        return false;
    }
    return true;
}

function updateBalance(winningBet) {
    const bankerBet = parseInt(bankerBetInput.value);
    const playerBet = parseInt(playerBetInput.value);
    const tieBet = parseInt(tieBetInput.value);

    const totalBet = bankerBet + playerBet + tieBet;
    let winnings = 0;

    if (winningBet === 'banker') {
        winnings = bankerBet * 1.95; // 5% commission
    } else if (winningBet === 'player') {
        winnings = playerBet * 2;
    } else if (winningBet === 'tie') {
        winnings = tieBet * 9;
    }

    const netWinLoss = winnings - totalBet;
    balance += netWinLoss;

    balanceElement.textContent = `Balance: $${balance.toFixed(2)}`;
    return netWinLoss;
}

async function dealCards() {
    if (!validateBets()) return;

    playerHand.innerHTML = '';
    bankerHand.innerHTML = '';
    result.textContent = '';

    const cards = await fetchCards(6);
    const playerCards = cards.slice(0, 2);
    const bankerCards = cards.slice(2, 4);

    const playerCardElements = playerCards.map(card => displayCard(card, playerHand));
    const bankerCardElements = bankerCards.map(card => displayCard(card, bankerHand));

    let playerValue = calculateHandValue(playerCards);
    let bankerValue = calculateHandValue(bankerCards);

    playerScore.textContent = playerValue;
    bankerScore.textContent = bankerValue;

    if (playerValue >= 8 || bankerValue >= 8) {
        // Natural win
        determineWinner(playerValue, bankerValue, playerCardElements, bankerCardElements);
    } else {
        // Draw additional cards if necessary
        if (playerValue <= 5) {
            const playerThirdCard = cards[4];
            const playerThirdCardElement = displayCard(playerThirdCard, playerHand);
            playerCardElements.push(playerThirdCardElement);
            playerValue = calculateHandValue([...playerCards, playerThirdCard]);
            playerScore.textContent = playerValue;

            if (bankerValue <= 2 || (bankerValue <= 5 && shouldBankerDraw(bankerValue, playerThirdCard.value))) {
                const bankerThirdCard = cards[5];
                const bankerThirdCardElement = displayCard(bankerThirdCard, bankerHand);
                bankerCardElements.push(bankerThirdCardElement);
                bankerValue = calculateHandValue([...bankerCards, bankerThirdCard]);
                bankerScore.textContent = bankerValue;
            }
        } else if (bankerValue <= 5) {
            const bankerThirdCard = cards[5];
            const bankerThirdCardElement = displayCard(bankerThirdCard, bankerHand);
            bankerCardElements.push(bankerThirdCardElement);
            bankerValue = calculateHandValue([...bankerCards, bankerThirdCard]);
            bankerScore.textContent = bankerValue;
        }

        determineWinner(playerValue, bankerValue, playerCardElements, bankerCardElements);
    }
}

function determineWinner(playerValue, bankerValue, playerCardElements, bankerCardElements) {
    let winningBet;
    let resultText;
    let resultColor;

    if (playerValue > bankerValue) {
        resultText = 'Player wins!';
        winningBet = 'player';
        resultColor = 'blue';
        playerCardElements.forEach(card => card.style.backgroundColor = 'lightgreen');
        bankerCardElements.forEach(card => card.style.backgroundColor = 'lightcoral');
    } else if (bankerValue > playerValue) {
        resultText = 'Banker wins!';
        winningBet = 'banker';
        resultColor = 'red';
        bankerCardElements.forEach(card => card.style.backgroundColor = 'lightgreen');
        playerCardElements.forEach(card => card.style.backgroundColor = 'lightcoral');
    } else {
        resultText = 'It\'s a tie!';
        winningBet = 'tie';
        resultColor = 'green';
        playerCardElements.forEach(card => card.style.backgroundColor = 'yellow');
        bankerCardElements.forEach(card => card.style.backgroundColor = 'yellow');
    }

    const netWinLoss = updateBalance(winningBet);
    updateResult(resultText, netWinLoss);
    updateGameHistory(resultColor);

    setTimeout(() => {
        playerCardElements.forEach(card => card.style.backgroundColor = '');
        bankerCardElements.forEach(card => card.style.backgroundColor = '');
    }, 2000);
}
