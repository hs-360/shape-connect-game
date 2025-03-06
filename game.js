class Game {
    constructor() {
        this.board = Array(6).fill().map(() => Array(7).fill(null));
        this.currentPlayer = 'player';
        this.gameOver = false;
        this.winner = null;
        this.winType = null;
        this.shapes = ['circle', 'square', 'triangle', 'diamond'];
        this.currentShape = 'circle';
        
        this.initializeGame();
        this.setupEventListeners();
    }

    initializeGame() {
        // Create the game board
        const boardGrid = document.getElementById('boardGrid');
        boardGrid.innerHTML = '';
        
        for (let row = 0; row < 6; row++) {
            for (let col = 0; col < 7; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                boardGrid.appendChild(cell);
            }
        }

        // Setup shape selector
        const shapeSelect = document.getElementById('shapeSelect');
        shapeSelect.value = this.currentShape;
    }

    setupEventListeners() {
        // Board click handler
        document.getElementById('boardGrid').addEventListener('click', (e) => {
            if (this.gameOver || this.currentPlayer !== 'player') return;
            
            const cell = e.target.closest('.cell');
            if (!cell) return;
            
            const col = parseInt(cell.dataset.col);
            this.makeMove(col);
        });

        // Shape selector handler
        document.getElementById('shapeSelect').addEventListener('change', (e) => {
            this.currentShape = e.target.value;
        });

        // Play again button handler
        document.getElementById('playAgain').addEventListener('click', () => {
            this.resetGame();
        });

        // Close button handler
        document.getElementById('closeGameOver').addEventListener('click', () => {
            document.getElementById('gameOver').classList.remove('active');
        });
    }

    makeMove(col) {
        if (this.gameOver) return false;

        // Find the lowest empty cell in the column
        for (let row = 5; row >= 0; row--) {
            if (!this.board[row][col]) {
                this.placePiece(row, col);
                return true;
            }
        }
        return false;
    }

    placePiece(row, col) {
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        const shape = this.currentPlayer === 'player' ? this.currentShape : this.getRandomShape();
        
        this.board[row][col] = {
            player: this.currentPlayer,
            shape: shape
        };

        cell.className = `cell ${this.currentPlayer} ${shape}`;

        if (this.checkWin(row, col)) {
            this.gameOver = true;
            this.winner = this.currentPlayer;
            this.showGameOver();
            return;
        }

        this.currentPlayer = this.currentPlayer === 'player' ? 'ai' : 'player';

        if (this.currentPlayer === 'ai') {
            setTimeout(() => this.aiMove(), 500);
        }
    }

    getRandomShape() {
        return this.shapes[Math.floor(Math.random() * this.shapes.length)];
    }

    checkWin(row, col) {
        const directions = [
            [[0, 1], [0, -1]],  // horizontal
            [[1, 0], [-1, 0]],  // vertical
            [[1, 1], [-1, -1]], // diagonal down
            [[1, -1], [-1, 1]]  // diagonal up
        ];

        const piece = this.board[row][col];
        if (!piece) return false;

        // Check for color win
        for (const direction of directions) {
            let colorCount = 1;
            let winningCells = [[row, col]];
            
            for (const [dr, dc] of direction) {
                let r = row + dr;
                let c = col + dc;
                
                while (
                    r >= 0 && r < 6 && 
                    c >= 0 && c < 7 && 
                    this.board[r][c] && 
                    this.board[r][c].player === piece.player
                ) {
                    colorCount++;
                    winningCells.push([r, c]);
                    r += dr;
                    c += dc;
                }
            }

            if (colorCount >= 4) {
                this.winType = 'color';
                this.winningCells = winningCells;
                return true;
            }
        }

        // Check for shape win
        for (const direction of directions) {
            let shapeCount = 1;
            let winningCells = [[row, col]];
            
            for (const [dr, dc] of direction) {
                let r = row + dr;
                let c = col + dc;
                
                while (
                    r >= 0 && r < 6 && 
                    c >= 0 && c < 7 && 
                    this.board[r][c] && 
                    this.board[r][c].shape === piece.shape
                ) {
                    shapeCount++;
                    winningCells.push([r, c]);
                    r += dr;
                    c += dc;
                }
            }

            if (shapeCount >= 4) {
                this.winType = 'shape';
                this.winningCells = winningCells;
                return true;
            }
        }

        return false;
    }

    highlightWinningCells() {
        if (!this.winningCells) return;
        
        // Determine the direction of the winning sequence
        const [firstRow, firstCol] = this.winningCells[0];
        const [lastRow, lastCol] = this.winningCells[this.winningCells.length - 1];
        
        let direction = 'horizontal';
        if (firstCol === lastCol) {
            direction = 'vertical';
        } else if (lastRow - firstRow === lastCol - firstCol) {
            direction = 'diagonal-down';
        } else if (lastRow - firstRow === firstCol - lastCol) {
            direction = 'diagonal-up';
        }
        
        this.winningCells.forEach(([row, col]) => {
            const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
            if (cell) {
                cell.classList.add('highlight');
                cell.setAttribute('data-direction', direction);
            }
        });
    }

    aiMove() {
        // First, check if AI can win in one move
        for (let col = 0; col < 7; col++) {
            const row = this.getLowestEmptyRow(col);
            if (row === -1) continue;

            // Try placing AI piece
            this.board[row][col] = { player: 'ai', shape: this.getRandomShape() };
            if (this.checkWin(row, col)) {
                this.placePiece(row, col);
                return;
            }
            this.board[row][col] = null;
        }

        // Then, check if player can win in one move and block
        for (let col = 0; col < 7; col++) {
            const row = this.getLowestEmptyRow(col);
            if (row === -1) continue;

            // Try placing player piece
            this.board[row][col] = { player: 'player', shape: this.currentShape };
            if (this.checkWin(row, col)) {
                this.board[row][col] = null;
                this.placePiece(row, col);
                return;
            }
            this.board[row][col] = null;
        }

        // Look for opportunities to create a winning position
        for (let col = 0; col < 7; col++) {
            const row = this.getLowestEmptyRow(col);
            if (row === -1) continue;

            // Try placing AI piece
            this.board[row][col] = { player: 'ai', shape: this.getRandomShape() };
            
            // Check if this move creates a winning opportunity
            let createsWin = false;
            for (let nextCol = 0; nextCol < 7; nextCol++) {
                const nextRow = this.getLowestEmptyRow(nextCol);
                if (nextRow === -1) continue;

                this.board[nextRow][nextCol] = { player: 'ai', shape: this.getRandomShape() };
                if (this.checkWin(nextRow, nextCol)) {
                    createsWin = true;
                    this.board[nextRow][nextCol] = null;
                    break;
                }
                this.board[nextRow][nextCol] = null;
            }

            this.board[row][col] = null;
            if (createsWin) {
                this.placePiece(row, col);
                return;
            }
        }

        // Look for opportunities to block player's winning position
        for (let col = 0; col < 7; col++) {
            const row = this.getLowestEmptyRow(col);
            if (row === -1) continue;

            // Try placing player piece
            this.board[row][col] = { player: 'player', shape: this.currentShape };
            
            // Check if player can win in the next move
            let playerCanWin = false;
            for (let nextCol = 0; nextCol < 7; nextCol++) {
                const nextRow = this.getLowestEmptyRow(nextCol);
                if (nextRow === -1) continue;

                this.board[nextRow][nextCol] = { player: 'player', shape: this.currentShape };
                if (this.checkWin(nextRow, nextCol)) {
                    playerCanWin = true;
                    this.board[nextRow][nextCol] = null;
                    break;
                }
                this.board[nextRow][nextCol] = null;
            }

            this.board[row][col] = null;
            if (playerCanWin) {
                this.placePiece(row, col);
                return;
            }
        }

        // If no immediate threats or opportunities, make a strategic move
        // Prefer center columns and avoid edges
        const columnWeights = [0, 1, 2, 3, 2, 1, 0];
        const availableCols = Array.from({ length: 7 }, (_, i) => i)
            .filter(col => this.getLowestEmptyRow(col) !== -1);
        
        if (availableCols.length > 0) {
            // Sort columns by weight (higher weight = better position)
            availableCols.sort((a, b) => columnWeights[b] - columnWeights[a]);
            
            // Add some randomness to avoid predictable play
            const topCols = availableCols.slice(0, Math.min(3, availableCols.length));
            const randomCol = topCols[Math.floor(Math.random() * topCols.length)];
            this.makeMove(randomCol);
        }
    }

    getLowestEmptyRow(col) {
        for (let row = 5; row >= 0; row--) {
            if (!this.board[row][col]) return row;
        }
        return -1;
    }

    showGameOver() {
        const gameOver = document.getElementById('gameOver');
        const message = gameOver.querySelector('.message');
        
        message.textContent = this.winner === 'player' ? 'You are the winner!' : 'AI is the winner!';
        this.highlightWinningCells();
        gameOver.classList.add('active');
    }

    resetGame() {
        this.board = Array(6).fill().map(() => Array(7).fill(null));
        this.currentPlayer = 'player';
        this.gameOver = false;
        this.winner = null;
        this.winType = null;
        this.currentShape = 'circle';
        this.winningCells = null;
        
        // Remove highlight class from all cells
        document.querySelectorAll('.cell').forEach(cell => {
            cell.classList.remove('highlight');
        });
        
        document.getElementById('shapeSelect').value = this.currentShape;
        document.getElementById('gameOver').classList.remove('active');
        this.initializeGame();
    }
}

// Start the game when the page loads
window.addEventListener('load', () => {
    new Game();
}); 