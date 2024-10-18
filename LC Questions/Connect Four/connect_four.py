import sys
import pprint


class ConnectFour:
  EMPTY_BOARD = [   ['.','.','.','.','.','.','.'],
                    ['.','.','.','.','.','.','.'],
                    ['.','.','.','.','.','.','.'],
                    ['.','.','.','.','.','.','.'],
                    ['.','.','.','.','.','.','.'],
                    ['.','.','.','.','.','.','.']  ] # Default Empty Baord if game has no pre loaded board
                    
  def __init__(self, board: list[list] = EMPTY_BOARD) -> None:
    self.board = board
    self.score= {'Y': 0, 'R': 0} # For a fair game, regrdless whether the board is pre loaded or not, point starts at 0
    self.ROW = len(self.board) - 1 # O Index (6 Rows)
    self.COL = len(self.board[0]) - 1 # 0 Index (7 Cols)
    self.first_available_row = {col: index for col, index in self._find_available_row().items()}
    self.ALLOWED_COLORS = self.score.keys()
    if not self.first_available_row:
      raise ValueError("There are no available slots for this board")
      
  def _is_game_col_valid(self, col: int) -> None:
    if not (0 <= col <= self.COL):
        raise ValueError(f"Invalid column number: {col}. It must be between 0 and {self.COL}.")

  def _find_available_row(self) -> dict:
    available_rows = dict()
    for r in range(self.ROW, -1, -1):
      if len(available_rows) == self.COL: # Quit Iteration Early if rows are found in the bottom
        break
      
      for c in range(self.COL + 1):
        if self.board[r][c] == '.' and c not in available_rows:
          available_rows[c] = r
          
    return available_rows
    
  def _vertical_scoring_opportunity(self, color: str, col: int) -> bool: 
    # On the Dropped Row check if at least the previous three rows are the same color with BOTTOM-UP iteration

    dropped_to_row = self.first_available_row[col]
    if dropped_to_row + 3 <= self.ROW:
        # Check the next three rows downwards for the same color
        for row in range(dropped_to_row + 1, dropped_to_row + 4):
            if self.board[row][col] != color:
                return False
        # If all three below match the color, it's a scoring opportunity
        print("DEBUG: Gained in Vertical Check")
        return True
    
    # Not enough rows below to form a vertical scoring opportunity
    return False
      
  def _horizontal_scoring_opportunity(self, color: str, col: int) -> bool:
    """
    We can check for scoring opportunity on the dropped row within these 4 conditions if width exists:
    (n - 1) + x + (n + 2), (n - 2) + x + (n + 1), (n - 3) + x, or x + (n + 3)
    
    However these 4 checks double the iertaion we need to do so we can have a single LEFT-RIGHT iteration to check for the case
    where 3 colors and the dropped to row exist consecutively
    """
    dropped_to_row = self.first_available_row[col]
    lowest_index = 0 if col - 3 < 0 else col - 3
    higest_index = self.COL if col +  3 > self.COL else col +  3
    
    color_count, have_used_chip = 0, False
    for curr_col in range(lowest_index, higest_index + 1):
      if color_count == 3 and have_used_chip:
        print("DEBUG: Gained in Horizontal Check 1")
        return True
        
      if self.board[dropped_to_row][curr_col] == color:
        color_count += 1
      elif curr_col == col and not have_used_chip:
        have_used_chip = True
      else:
        color_count = 0 # Reset consecutive color
        
    if color_count == 3 and have_used_chip: # Check for last iteration
        print("DEBUG: Gained in Horizontal Check 2")
        return True
      
    return False
    
   """
    We can check for scoring opportunity on the dropped row within these 8 conditions if width exists:
    x = new dropped spot, . = previos macthing colors
    .           x     x           .     .           .     .           .
     .         .       .         .       x         x       .         .  
      .       .         .       .         .       .         x       x
       x     .           .     x           .     .           .     .
    However these 8 checks double the iertaion we need to do so we can have a single BOTTOM-UP iteration diagonally and anti-diagonally 
    to check for the case where 3 colors and the dropped to row exist consecutively
  """

  def _diagonal_scoring_opportunity(self, color: str, col: int) -> bool:
    dropped_to_row = self.first_available_row[col]
    
    # Diagnal Iter (start from the lowest left point within the 3 range and iterate ↑→)
    lowest_row_col_index = [ dropped_to_row, col ]
    while lowest_row_col_index[0] < self.ROW and lowest_row_col_index[1] > 0: # They are interdependant so drag together until one runs out
      lowest_row_col_index[0] += 1
      lowest_row_col_index[1] -= 1
      
    higest_row_col_index = [ 0 if dropped_to_row - 3 < 0 else dropped_to_row - 3, 
                             self.COL if col + 3 > self.COL else col + 3]
    
    color_count, have_used_chip = 0, False
    while lowest_row_col_index[0] >= higest_row_col_index[0] and lowest_row_col_index[1] < higest_row_col_index[1] + 1:
      if color_count == 3 and have_used_chip:
        print("DEBUG: Gained in Diagnal Check 1")
        return True
        
      if self.board[lowest_row_col_index[0]][lowest_row_col_index[1]] == color:
        color_count += 1
      elif lowest_row_col_index[1] == col and not have_used_chip:
        have_used_chip = True
      else:
        color_count = 0
        
      lowest_row_col_index[0] -= 1
      lowest_row_col_index[1] += 1
      
    if color_count == 3 and have_used_chip: # Check for last iteration
        print("DEBUG: Gained in Diagnal Check 2")
        return True

    return False
      


  def _anti_diagonal_scoring_opportunity(self, color: str, col: int) -> bool:
    dropped_to_row = self.first_available_row[col]
    
    # Anti-Diagonal Iter (start from the lowest right point within the 3 range and iterate ←↑)
    lowest_row_col_index = [ dropped_to_row, col ]
    while lowest_row_col_index[0] < self.ROW and lowest_row_col_index[1] < self.COL: # They are interdependent so drag them together until one runs out
      lowest_row_col_index[0] += 1
      lowest_row_col_index[1] += 1
      
    higest_row_col_index = [ 0 if dropped_to_row - 3 < 0 else dropped_to_row - 3, 
                             0 if col - 3 < 0 else col - 3]
    
    color_count, have_used_chip = 0, False
    while lowest_row_col_index[0] >= higest_row_col_index[0] and lowest_row_col_index[1] >= higest_row_col_index[0]:
      if color_count == 3 and have_used_chip:
        print("DEBUG: Gained in Anti-Diagnal Check 1")
        return True
        
      if self.board[lowest_row_col_index[0]][lowest_row_col_index[1]] == color:
        color_count += 1
      elif lowest_row_col_index[1] == col and not have_used_chip:
        have_used_chip = True
      else:
        color_count = 0
        
      lowest_row_col_index[0] -= 1
      lowest_row_col_index[1] -= 1
      
    if color_count == 3 and have_used_chip: # Check for last iteration
        return True
        print("DEBUG: Gained in Anti-Diagonal Check 2")

    return False
    
  def play(self, color: str, col: int) -> int:
    # Early Defense
    if color not in self.ALLOWED_COLORS:
      raise ValueError("There are no other chips or players besides 'Y' - Yellow and 'R' - Red")
    self._is_game_col_valid(col)
      
    total_score = sum([ self._vertical_scoring_opportunity(color,col),
                        self._horizontal_scoring_opportunity(color,col),
                        self._diagonal_scoring_opportunity(color,col),
                        self._anti_diagonal_scoring_opportunity(color,col) ])
    
    if total_score:
      self.score[color] += total_score
      print(f"Player: {color} has gained {total_score} points.")
      
    # Report Score
    print(f"Current Score: Yellow has {self.score['Y']} points and Red has {self.score['R']} points")
    
    # Already Calculated and Reported the Score without modifying the board so now update the board to keep the play going
    dropped_to_row = self.first_available_row[col]
    self.board[dropped_to_row][col] = color
    
    # Report Updated Board
    pprint.pprint(self.board)
    
    # Update Dropped Row availability Dict
    if self.first_available_row[col] == 0:
      del self.first_available_row[col]
    else:
      self.first_available_row[col] -= 1
      
    """
    Shortcomings:
    1. This game will go on and will only end when all slots are filled instead of detecting 
    the presence or lack of scoring opportunity to end the game early, which could be implemented by an 
    additional boolean function _is_there_potential_scoring_slot() to end the game early
    
    2. In a case where we have a connect 4 score obtained and one more chip of the same color is added to the
    already made connection in an adjacent direction another point is gained. This comes from the fact that
    I am not well aware of the point limitations of the continuing version of the game. However, this can easily be solved by adding
    a set that contains tuples of (row,col) for connect four points already gained if the rule states otherwise.
    """
    
    if len(self.first_available_row) > 0:
      return total_score
    else:
      print('Yellow Wins' if self.score['Y'] > self.score['R'] else ('Red Wins' if self.score['Y'] < self.score['R'] else 'Tied'))
      print("Game is Over.")
      sys.exit()
      
      
game = ConnectFour()
game.play('Y', 1)
game.play('Y', 0)
game.play('Y', 2)
game.play('Y', 5)
game.play('Y', 6)
game.play('Y', 3)
game.play('R', 4)
game.play('R', 4)
game.play('R', 4)
game.play('R', 4)
game.play('Y', 1)
game.play('Y', 2)
game.play('Y', 2)
game.play('Y', 3)
game.play('Y', 3)
game.play('Y', 3)
game.play('R', 0)
game.play('R', 1)
game.play('R', 2)
game.play('R', 3)
game.play('R', 6)


"""
RESULT:
Current Score: Yellow has 0 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', 'Y', '.', '.', '.', '.', '.']]
Current Score: Yellow has 0 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['Y', 'Y', '.', '.', '.', '.', '.']]
Current Score: Yellow has 0 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['Y', 'Y', 'Y', '.', '.', '.', '.']]
Current Score: Yellow has 0 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['Y', 'Y', 'Y', '.', '.', 'Y', '.']]
Current Score: Yellow has 0 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['Y', 'Y', 'Y', '.', '.', 'Y', 'Y']]
DEBUG: Gained in Horizontal Check 1
Player: Y has gained 1 points.
Current Score: Yellow has 1 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', '.', 'Y', 'Y']]
Current Score: Yellow has 1 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 1 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 1 points and Red has 0 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
DEBUG: Gained in Vertical Check
Player: R has gained 1 points.
Current Score: Yellow has 1 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 1 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', 'Y', '.', '.', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 1 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', 'Y', 'Y', '.', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 1 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', '.', 'Y', '.', 'R', '.', '.'],
 ['.', 'Y', 'Y', '.', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 1 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', '.', 'Y', '.', 'R', '.', '.'],
 ['.', 'Y', 'Y', 'Y', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 1 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', 'R', '.', '.'],
 ['.', '.', 'Y', 'Y', 'R', '.', '.'],
 ['.', 'Y', 'Y', 'Y', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
DEBUG: Gained in Vertical Check
DEBUG: Gained in Diagnal Check 1
Player: Y has gained 2 points.
Current Score: Yellow has 3 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', 'Y', 'R', '.', '.'],
 ['.', '.', 'Y', 'Y', 'R', '.', '.'],
 ['.', 'Y', 'Y', 'Y', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 3 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', 'Y', 'R', '.', '.'],
 ['.', '.', 'Y', 'Y', 'R', '.', '.'],
 ['R', 'Y', 'Y', 'Y', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 3 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', 'Y', 'R', '.', '.'],
 ['.', 'R', 'Y', 'Y', 'R', '.', '.'],
 ['R', 'Y', 'Y', 'Y', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 3 points and Red has 1 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', 'R', 'Y', 'R', '.', '.'],
 ['.', 'R', 'Y', 'Y', 'R', '.', '.'],
 ['R', 'Y', 'Y', 'Y', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
DEBUG: Gained in Diagnal Check 1
Player: R has gained 1 points.
Current Score: Yellow has 3 points and Red has 2 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', 'R', '.', '.', '.'],
 ['.', '.', 'R', 'Y', 'R', '.', '.'],
 ['.', 'R', 'Y', 'Y', 'R', '.', '.'],
 ['R', 'Y', 'Y', 'Y', 'R', '.', '.'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
Current Score: Yellow has 3 points and Red has 2 points
[['.', '.', '.', '.', '.', '.', '.'],
 ['.', '.', '.', 'R', '.', '.', '.'],
 ['.', '.', 'R', 'Y', 'R', '.', '.'],
 ['.', 'R', 'Y', 'Y', 'R', '.', '.'],
 ['R', 'Y', 'Y', 'Y', 'R', '.', 'R'],
 ['Y', 'Y', 'Y', 'Y', 'R', 'Y', 'Y']]
"""
      

    
  
          
