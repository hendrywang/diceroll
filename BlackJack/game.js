class Game {
    constructor() {
        this.players = Array.from({length: 8}, (_, i) => new Player(`Player ${i + 1}`));
        this.banker = new Player('Banker');
        this.currentPlayerIndex = 0;
        this.gameEnded = false;
    }

    async startGame() {
        this.gameEnded = false;
        this.currentPlayerIndex = 0;
        this.players.forEach(player => player.resetForNewRound());
        this.banker.resetForNewRound();

        // Betting phase
        for (let player of this.players) {
            await this.playerBet(player);
        }

        // Deal initial cards
        for (let i = 0; i < 2; i++) {
            for (let player of this.players) {
                if (player.currentBet > 0) {
                    await this.dealCard(player);
                }
            }
            await this.dealCard(this.banker);
        }

        this.checkForBlackjacks();
        renderGame();
    }

    async playerBet(player) {
        return new Promise(resolve => {
            renderBettingUI(player, (betAmount) => {
                player.placeBet(betAmount);
                resolve();
            });
        });
    }

    checkForBlackjacks() {
        let allBlackjackOrBust = true;
        for (let player of this.players) {
            if (player.hasBlackjack) {
                player.result = 'Blackjack';
                player.isStanding = true;
                player.winBet(1.5);  // Blackjack typically pays 3:2
            } else if (!player.isBust && player.currentBet > 0) {
                allBlackjackOrBust = false;
            }
        }
        if (this.banker.hasBlackjack) {
            this.endGame();
        } else if (allBlackjackOrBust) {
            this.bankerPlay();
        }
    }

    async dealCard(player) {
        try {
            const response = await fetch('http://localhost:3040/draw');
            const data = await response.json();
            player.hit(data.cards[0]);
        } catch (error) {
            console.error('Error drawing card:', error);
        }
    }

    async playerAction(action) {
        const currentPlayer = this.players[this.currentPlayerIndex];
        if (action === 'hit') {
            await this.dealCard(currentPlayer);
            if (currentPlayer.score === 21) {
                currentPlayer.result = 'Win';
                currentPlayer.winBet(1);
                this.nextPlayer();
            } else if (currentPlayer.isBust) {
                currentPlayer.loseBet();
                this.nextPlayer();
            }
        } else if (action === 'stand') {
            currentPlayer.isStanding = true;
            this.nextPlayer();
        } else if (action === 'double') {
            if (currentPlayer.balance >= currentPlayer.currentBet) {
                currentPlayer.balance -= currentPlayer.currentBet;
                currentPlayer.currentBet *= 2;
                await this.dealCard(currentPlayer);
                currentPlayer.isStanding = true;
                if (currentPlayer.isBust) {
                    currentPlayer.loseBet();
                }
                this.nextPlayer();
            }
        }
        renderGame();
    }

    nextPlayer() {
        do {
            this.currentPlayerIndex++;
            if (this.currentPlayerIndex >= this.players.length) {
                this.bankerPlay();
                return;
            }
        } while (this.players[this.currentPlayerIndex].isStanding || 
                 this.players[this.currentPlayerIndex].isBust ||
                 this.players[this.currentPlayerIndex].hasBlackjack ||
                 this.players[this.currentPlayerIndex].currentBet === 0);
    }

    async bankerPlay() {
        while (this.banker.score < 17) {
            await this.dealCard(this.banker);
        }
        this.endGame();
    }

    endGame() {
        for (let player of this.players) {
            if (!player.isBust && !player.hasBlackjack && player.currentBet > 0) {
                if (this.banker.isBust) {
                    player.result = 'Win';
                    player.winBet(1);
                } else if (player.score > this.banker.score) {
                    player.result = 'Win';
                    player.winBet(1);
                } else if (player.score === this.banker.score) {
                    player.result = 'Tie';
                    player.winBet(0);  // Return the original bet
                } else {
                    player.result = 'Lose';
                    player.loseBet();
                }
            }
        }
        this.gameEnded = true;
        renderGame();
    }
}
