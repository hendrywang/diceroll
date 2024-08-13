document.addEventListener('DOMContentLoaded', () => {
    initializeGame();
    
    dealButton.addEventListener('click', dealCards);
    resetButton.addEventListener('click', resetGame);

    // Add event listeners for bet buttons
    document.querySelectorAll('.increase-bet').forEach(button => {
        button.addEventListener('click', (e) => {
            const input = e.target.previousElementSibling;
            input.value = parseInt(input.value) + 10;
        });
    });

    document.querySelectorAll('.decrease-bet').forEach(button => {
        button.addEventListener('click', (e) => {
            const input = e.target.nextElementSibling;
            input.value = Math.max(0, parseInt(input.value) - 10);
        });
    });
});
