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
                    
        score_list.append(black_count)
        score_list.append(white_count)

        return score_list

    def move(self, u_in: list) -> None:
        board_structure.current_board[u_in[1]-1][u_in[0]-1] = board_structure.current_player_move

        if board_structure.current_player_move == 'B':
            board_structure.current_player_move = 'W'
        elif board_structure.current_player_move == 'W':
            board_structure.current_player_move = 'B'
        

                    


