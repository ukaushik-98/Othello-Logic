#othello_ui.py
#Udit Kaushik
#75825974

import othello_logic

def board_printer(b_struct) -> None:
    b_list = b_struct.current_board
    score_list = b_struct.score_counter(b_list)
    print('B: {} W: {}'.format(score_list[0], score_list[1]))
    for i in range(b_struct.rows):
        for j in range(b_struct.columns):
            print(b_list[j][i], end = (' '))
        print('')
    print('TURN: {}'.format(b_struct.current_player_move))

def user_input() -> list:
    input_list = []
    u_in = input()

    a = int(u_in[0])
    b = int(u_in[2])
    input_list.append(a)
    input_list.append(b)
    return input_list

def input_checker(u_in: list, b_struct) -> str:
    if (0 < u_in[0] <= b_struct.rows) and (0 < u_in[1] <= b_struct.columns):
        return ('pass')
    else:
        return ('INVALID')

def main():
    b_struct = othello_logic.board_structure()
    board_printer(b_struct)
    while True:
        u_in = user_input()
        if input_checker(u_in, b_struct) == 'INVALID':
            print('INVALID')  
        else:
            checker = b_struct.move(u_in)
            if checker == 'INVALID':
                print('INVALID')   
            else:
                print(checker)
                board_printer(b_struct)
        
if __name__ == '__main__':
    main()
