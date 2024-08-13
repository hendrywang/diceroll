function renderGame() {
    const bankerArea = document.getElementById('banker');
    const playersArea = document.getElementById('players');
    bankerArea.innerHTML = '';
    playersArea.innerHTML = '';

    bankerArea.appendChild(renderPlayerOrBanker(game.banker, true));

    for (let player of game.players) {
        playersArea.appendChild(renderPlayerOrBanker(player, false));
    }
}

function renderPlayerOrBanker(player, isBanker) {
    const div = document.createElement('div');
    div.className = isBanker ? 'banker' : 'player';
    
    if (!isBanker) {
        if (player.hasBlackjack) {
            div.classList.add('player-blackjack');
        } else if (player.isBust) {
            div.classList.add('player-busted');
        } else if (game.gameEnded) {
            switch(player.result) {
                case 'Win':
                    div.classList.add('player-won');
                    break;
                case 'Tie':
                    div.classList.add('player-tie');
                    break;
                case 'Lose':
                    div.classList.add('player-lost');
                    break;
            }
        }
    }

    let scoreDisplay = player.isBust ? 'Bust' : player.score;
    if (isBanker && !game.gameEnded) {
        scoreDisplay = '?';
    }
    div.innerHTML = `
        <h2 class="player-name">${player.name}</h2>
        <p class="player-score">Score: ${scoreDisplay}</p>
        ${!isBanker ? `<p class="player-balance">Balance: $${player.balance}</p>` : ''}
        ${!isBanker ? `<p class="player-bet">Current Bet: $${player.currentBet}</p>` : ''}
        <div class="hand">
            ${player.hand.map((card, index) => 
                isBanker && index === 1 && !game.gameEnded
                    ? renderHiddenCard() 
                    : renderCard(card)
            ).join('')}
        </div>
        ${player.result ? `<p>Result: ${player.result}</p>` : ''}
        ${renderActions(player)}
    `;
    return div;
}

function renderCard(card) {
    const suitEmoji = getSuitEmoji(card.suit);
    const isRed = ['hearts', 'diamonds'].includes(card.suit);
    return `
        <div class="card ${isRed ? 'red' : ''}">
            <div class="card-value">${card.value}</div>
            <div class="card-suit">${suitEmoji}</div>
        </div>
    `;
}

function getSuitEmoji(suit) {
    switch(suit) {
        case 'hearts': return '♥️';
        case 'diamonds': return '♦️';
        case 'clubs': return '♣️';
        case 'spades': return '♠️';
        default: return '';
    }
}

function renderHiddenCard() {
    return '<div class="card"><div class="card-value">[Hidden]</div></div>';
}

function renderActions(player) {
    if (game.gameEnded || player !== game.players[game.currentPlayerIndex] || player.isStanding || player.isBust || player.hasBlackjack) {
        return '';
    }
    return `
        <div class="actions">
            <button onclick="game.playerAction('hit')">Hit</button>
            <button onclick="game.playerAction('stand')">Stand</button>
            ${player.hand.length === 2 && player.balance >= player.currentBet ? `<button onclick="game.playerAction('double')">Double</button>` : ''}
        </div>
    `;
}

function renderBettingUI(player, callback) {
    const div = document.createElement('div');
    div.className = 'betting-ui';
    div.innerHTML = `
        <h2>${player.name}</h2>
        <p>Balance: $${player.balance}</p>
        <p>Place your bet:</p>
        <button onclick="placeBet(5)">$5</button>
        <button onclick="placeBet(10)">$10</button>
        <button onclick="placeBet(20)">$20</button>
        <button onclick="placeBet(50)">$50</button>
        <button onclick="placeBet(100)">$100</button>
    `;

    const playersArea = document.getElementById('players');
    playersArea.innerHTML = '';
    playersArea.appendChild(div);

    window.placeBet = function(amount) {
        if (player.balance >= amount) {
            callback(amount);
        } else {
            alert("Not enough balance for this bet!");
        }
    };
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const startGameButton = document.getElementById('start-game');
    startGameButton.addEventListener('click', () => {
        game = new Game();
        game.startGame();
    });
});