class Player {
    constructor(name) {
        this.name = name;
        this.hand = [];
        this.score = 0;
        this.isBust = false;
        this.isStanding = false;
        this.result = null;
        this.hasBlackjack = false;
        this.balance = 1000;
        this.currentBet = 0;
    }

    hit(card) {
        this.hand.push(card);
        this.calculateScore();
    }

    calculateScore() {
        this.score = 0;
        let aceCount = 0;
        for (let card of this.hand) {
            if (['J', 'Q', 'K'].includes(card.value)) {
                this.score += 10;
            } else if (card.value === 'A') {
                aceCount++;
            } else {
                this.score += parseInt(card.value);
            }
        }
        for (let i = 0; i < aceCount; i++) {
            if (this.score + 11 <= 21) {
                this.score += 11;
            } else {
                this.score += 1;
            }
        }
        if (this.score > 21) {
            this.isBust = true;
            this.result = 'Bust';
        } else if (this.score === 21 && this.hand.length === 2) {
            this.hasBlackjack = true;
            this.result = 'Blackjack';
        }
    }

    placeBet(amount) {
        if (amount <= this.balance) {
            this.currentBet = amount;
            this.balance -= amount;
            return true;
        }
        return false;
    }

    winBet(multiplier = 1) {
        this.balance += this.currentBet * (1 + multiplier);
        this.currentBet = 0;
    }

    loseBet() {
        this.currentBet = 0;
    }

    resetForNewRound() {
        this.hand = [];
        this.score = 0;
        this.isBust = false;
        this.isStanding = false;
        this.result = null;
        this.hasBlackjack = false;
        this.currentBet = 0;
    }
}
