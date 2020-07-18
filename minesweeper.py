import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def __hash__(self):
        return hash(repr(self))

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if self.count == len(self.cells):
            return set(self.cells)
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        if self.count == 0:
            return set(self.cells)
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        to_be_removed = set()

        for eachCell in self.cells:
            if (cell == eachCell):
                to_be_removed.add(eachCell)
                self.count -= 1;

        for eachCell in to_be_removed:
            self.cells.remove(eachCell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        to_be_removed = set()

        for eachCell in self.cells:
            if (cell == eachCell):
                to_be_removed.add(eachCell)

        for eachCell in to_be_removed:
            self.cells.remove(eachCell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)

        self.mark_safe(cell)

        sentence_set = set()

        for i in [cell[0] - 1, cell[0], cell[0] + 1]:
            for j in [cell[1] - 1, cell[1], cell[1] + 1]:
                if 0 <= i and i <= self.height - 1 and 0 <= j and j <= self.width - 1 and (i != cell[0] or j != cell[1]):
                    if (i, j) in set(self.mines):
                        count -= 1
                    elif (i, j) not in set(self.safes):
                        sentence_set.add((i, j))

        my_sentence = Sentence(sentence_set, count)

        self.knowledge.append(my_sentence)

        self.check(my_sentence)

        new_sentences = set()

        for sentence_1 in self.knowledge:
            for sentence_2 in self.knowledge:
                if sentence_1.cells != sentence_2.cells:
                    if sentence_1.cells.issubset(sentence_2.cells):
                        new_cells = set(sentence_2.cells)
                        new_count = sentence_2.count
                        for tuple in sentence_1.cells:
                            new_cells.remove(tuple)
                        new_count -= sentence_1.count
                        new_sentences.add(Sentence(new_cells, new_count))
                        self.check(sentence_1)
                        self.check(sentence_2)
                    elif sentence_2.cells.issubset(sentence_1.cells):
                        new_cells = set(sentence_1.cells)
                        new_count = sentence_1.count
                        for tuple in sentence_2.cells:
                            new_cells.remove(tuple)
                        new_count -= sentence_2.count
                        new_sentences.add(Sentence(new_cells, new_count))
                        self.check(sentence_1)
                        self.check(sentence_2)

        for eachSentence in new_sentences:
            self.knowledge.append(eachSentence)
            self.check(eachSentence)


    def check(self, checking_set):
        if bool(checking_set.known_mines()):
            for element in checking_set.known_mines():
                self.mines.add(element)
        elif bool(checking_set.known_safes()):
            for element in checking_set.known_safes():
                self.safes.add(element)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        for tuple in self.safes:
            if tuple not in set(self.moves_made):
                return tuple

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        for i in range(self.height):
            for j in range(self.width):
                tuple = (i, j)
                if tuple not in set(self.moves_made):
                    if tuple not in set(self.mines):
                        return tuple
