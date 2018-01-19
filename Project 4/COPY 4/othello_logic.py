#othello_logic.py
#Udit Kaushik
#75825974

class User_Input_Error(Exception):
    pass

class board_structure:
    rows = 0
    columns = 0
    current_player_move = '' 
    win_condition = ''
    current_board = []
    black_list = []
    white_list = []
    winner = True
    white_count = 0
    black_count = 0
    
    def __init__(self):
        u_in = self.user_input()
        self.user_check(u_in)
        board_structure.rows = u_in[0]
        board_structure.columns = u_in[1]
        board_structure.current_player_move = u_in[2]
        board_structure.win_condition = u_in[3]
        board_structure.current_board = self.initial_board_parser(u_in)
    
    def user_input(self) -> list:
        print('FULL')
        rows = int(input())
        columns = int(input())
        player_move = input()
        win_condition = input()

        initial_board = []
        for i in range(rows):
            temp = []
            initial_row = input()
            temp.append(initial_row)
            initial_board.append(temp)
        
        user_input_list = []
        user_input_list.append(rows)
        user_input_list.append(columns)
        user_input_list.append(player_move)
        user_input_list.append(win_condition)
        user_input_list.append(initial_board)

        return user_input_list

    def user_check(self, u_in: list) -> None:
        if (u_in[0] % 2 == 0) and (4 <= u_in[0] <= 16):
            pass
        else:
            raise User_Input_Error()

        if (u_in[1] % 2 == 0) and (4 <= u_in[1] <= 16):
            pass
        else:
            raise User_Input_Error()

        if (u_in[2] == 'B') or (u_in[2] == 'W'):
            pass
        else:
            raise User_Input_Error()

        if (u_in[3] == '>') or (u_in[3] == '<'):
            pass
        else:
            raise User_Input_Error()

        check_list = ['B', 'W', '.', ' ']
        for row_list in u_in[4]:
            for row in row_list:
                for char in row:
                    if char in check_list:
                        pass
                    else:
                        raise User_Input_Error()

    def initial_board_parser(self, u_list) -> list:
        check_list = ['B', 'W', '.']
        new_list = []
        for row_list in u_list[4]:
            temp = []
            for row in row_list:
                for char in row:
                    if char in check_list:
                        temp.append(char)
                        
            new_list.append(temp)
            
        final_list = []
        for i in range(len(new_list)):
            temp_column = []
            for j in range(len(new_list[i])):
                temp_column.append(new_list[j][i])
            final_list.append(temp_column)

        return final_list

    def score_counter(self, game_list: list) -> list:
        score_list = []
        white_count = 0
        black_count = 0

        for row in game_list:
            for position in row:
                if position == 'B':
                    black_count += 1
                elif position == 'W':
                    white_count += 1

        board_structure.white_count = white_count
        board_structure.black_count = black_count
        score_list.append(black_count)
        score_list.append(white_count)

        return score_list

    def move(self, u_in: list) -> str:
        checker = self.location_checker(u_in)
        if checker == 'VALID':
            pass
        elif checker == 'INVALID':
            return 'INVALID'

        p_loc = self.possible_locations(u_in)
        checker = self.color_finder(p_loc)
        if checker == 'INVALID':
            return 'INVALID'
        elif checker == 'VALID':
            board_structure.current_board[u_in[1]][u_in[0]] = board_structure.current_player_move

        self.score_counter(board_structure.current_board)
        self.check_winner()
        checker = self.game_winner()
        if checker == 'PASS':
            pass
        else:
            return checker

        if (len(board_structure.black_list) == 0):
            board_structure.current_player_move = 'W'
        elif (len(board_structure.white_list) == 0):
            board_structure.current_player_move = 'B'
        else:
             if board_structure.current_player_move == 'B':
                 board_structure.current_player_move = 'W'
             elif board_structure.current_player_move == 'W':
                board_structure.current_player_move = 'B'

        return 'VALID'

    def location_checker(self, u_in) -> str:
        if board_structure.current_board[u_in[1]][u_in[0]] == '.':
            return 'VALID'
        else:
            return 'INVALID'

    def possible_locations(self, u_in) -> list:
        row_num = u_in[1]
        col_num = u_in[0]
        location_list = []

        left_list = []
        right_list = []
        diag_up_right = []
        diag_up_left = []
        for i in range(1, board_structure.rows):
            if row_num - i >= 0:
                temp = []
                temp.append(col_num)
                temp.append(row_num - i)
                left_list.append(temp)
            if row_num + i < board_structure.rows:
                temp = []
                temp.append(col_num)
                temp.append(row_num + i)
                right_list.append(temp)
            if (row_num - i >= 0) and (col_num + i < board_structure.columns):
                temp = []
                temp.append(col_num + i)
                temp.append(row_num - i)
                diag_up_right.append(temp)
            if (row_num - i >= 0) and (col_num - i >= 0):
                temp = []
                temp.append(col_num - i)
                temp.append(row_num - i)
                diag_up_left.append(temp)
            if row_num == 0:
                temp = []
                temp.append(col_num)
                temp.append(row_num)
                left_list.append(temp)

        up_list = []
        down_list = []
        diag_down_right = []
        diag_down_left = []
        for i in range(1, board_structure.columns):
            if col_num - i >= 0:
                temp = []
                temp.append(col_num - i)
                temp.append(row_num)
                up_list.append(temp)
            if col_num + i < board_structure.columns:
                temp = []
                temp.append(col_num + i)
                temp.append(row_num)
                down_list.append(temp)
            if (row_num + i <  board_structure.rows) and (col_num + i < board_structure.columns):
                temp = []
                temp.append(col_num + i)
                temp.append(row_num + i)
                diag_down_right.append(temp)
            if (row_num + i <  board_structure.rows) and (col_num - i >= 0):
                temp = []
                temp.append(col_num - i)
                temp.append(row_num + i)
                diag_down_left.append(temp)
            if col_num == 0:
                temp = []
                temp.append(col_num)
                temp.append(row_num)
                up_list.append(temp)

                
        location_list.append(left_list)
        location_list.append(right_list)
        location_list.append(up_list)
        location_list.append(down_list)
        location_list.append(diag_up_right)
        location_list.append(diag_up_left)
        location_list.append(diag_down_right)
        location_list.append(diag_down_left)
        return location_list

    def color_finder(self, p_loc) -> str:
        color_changes = []
        for dir_list in p_loc:
            if board_structure.current_player_move == 'B':
                target_move = 'W'
            elif board_structure.current_player_move == 'W':
                target_move = 'B'

            if len(dir_list) > 0:
                loc = dir_list[0]
                h = int(loc[1])
                j = int(loc[0])
                if board_structure.current_board[h][j] == '.':
                    pass
                elif board_structure.current_board[h][j] == board_structure.current_player_move:
                    pass
                elif board_structure.current_board[h][j] == target_move:
                    temp = []
                    temp.append(loc)
                    
                    for i in range(1, len(dir_list)):
                        loc = dir_list[i]
                        h = int(loc[1])
                        j = int(loc[0])
                        if board_structure.current_board[h][j] == '.':
                            temp = []
                            break
                        
                        elif board_structure.current_board[h][j] == board_structure.current_player_move:
                            temp.append(loc)
                            break

                        elif board_structure.current_board[h][j] == target_move:
                            if i == len(dir_list) - 1:
                                temp = []
                            else:
                                temp.append(loc)

                    if len(temp) >= 2:
                        for item in temp:
                            color_changes.append(item)
            else:
                pass
                        
        if len(color_changes) > 0:
            for i in range(len(color_changes)):
                h = int(color_changes[i][1])
                j = int(color_changes[i][0])
                board_structure.current_board[h][j] = board_structure.current_player_move
            return 'VALID'

        else:
            return 'INVALID'
        
    def check_winner(self):
        new_list = []
        for i in range(len(board_structure.current_board)):
            for j in range(len(board_structure.current_board[i])):
                temp = []
                temp.append(j)
                temp.append(i)
                new_list.append(temp)

        black_list = []
        white_list = []
        for item in new_list:
            h = int(item[1])
            j = int(item[0])

            if board_structure.current_board[h][j] == '.':
                pass

            elif board_structure.current_board[h][j] == 'B':
                temp_list = self.possible_locations(item)
                for dir_list in temp_list:
                    if len(dir_list) > 0:
                        loc = dir_list[0]
                        h = int(loc[1])
                        j = int(loc[0])
                        if board_structure.current_board[h][j] == '.':
                            pass
                        elif board_structure.current_board[h][j] == 'B':
                            pass
                        elif board_structure.current_board[h][j] == 'W':
                            temp = []
                            for i in range(1, len(dir_list)):
                                loc = dir_list[i]
                                h = int(loc[1])
                                j = int(loc[0])
                                if board_structure.current_board[h][j] == '.':
                                    temp.append(loc)
                                    break
                                
                                elif board_structure.current_board[h][j] == 'B':
                                    temp = []
                                    break

                                elif board_structure.current_board[h][j] == 'W':
                                    pass

                            if len(temp) > 0:
                                for item in temp:
                                    black_list.append(item)
                    else:
                        pass

            
            elif board_structure.current_board[h][j] == 'W':
                temp_list = self.possible_locations(item)
                for dir_list in temp_list:                           
                    if len(dir_list) > 0:
                        loc = dir_list[0]
                        h = int(loc[1])
                        j = int(loc[0])
                        if board_structure.current_board[h][j] == '.':
                            pass
                        elif board_structure.current_board[h][j] == 'W':
                            pass
                        elif board_structure.current_board[h][j] == 'B':
                            temp = []
                            for i in range(1, len(dir_list)):
                                loc = dir_list[i]
                                h = int(loc[1])
                                j = int(loc[0])
                                if board_structure.current_board[h][j] == '.':
                                    temp.append(loc)
                                    break
                                
                                elif board_structure.current_board[h][j] == 'W':
                                    temp = []
                                    break

                                elif board_structure.current_board[h][j] == 'B':
                                    pass

                            if len(temp) > 0:
                                for item in temp:
                                    white_list.append(item)
                    else:
                        pass
        

        board_structure.black_list = black_list
        board_structure.white_list = white_list

    def game_winner(self):
        if (len(board_structure.black_list) == 0) and (len(board_structure.white_list) == 0):
            board_structure.winner = False

            if board_structure.win_condition == '>':
                if board_structure.white_count > board_structure.black_count:
                    return 'WINNER: W'
                elif board_structure.white_count < board_structure.black_count:
                    return 'WINNER: B'
                elif board_structure.white_count == board_structure.black_count:
                    return 'WINNER: NONE'
                
            elif board_structure.win_condition == '<':
                if board_structure.white_count < board_structure.black_count:
                    return 'WINNER: W'
                elif board_structure.white_count > board_structure.black_count:
                    return 'WINNER: B'
                elif board_structure.white_count == board_structure.black_count:
                    return 'WINNER: NONE'
        else:
            return 'PASS'

                                            
