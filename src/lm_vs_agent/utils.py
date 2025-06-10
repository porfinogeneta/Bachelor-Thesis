from src.consts import PYBIND_DIR, PROJECT_PATH, STANDARD, APPLES_CORPORA, NO_TAILS, MINIMAL




def create_game_sequence(corpora_type: str, game_sequence: str, prev_state, current_state):
        """
            Game sequence should be created based on model type, since each model may accept different game sequence
            
            returns: New game string, that should replace the former one!!
        """
        if corpora_type == STANDARD:

            # initializing sequence
            if prev_state == None:
                assert game_sequence == "", "At the beginning game sequence shouldn't be empty"
                game_sequence = "<START> "
                game_sequence += f"S0 R{current_state.snakes[0].head[0]}C{current_state.snakes[0].head[1]} L{len(current_state.snakes[0].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                game_sequence += f"S1 R{current_state.snakes[1].head[0]}C{current_state.snakes[1].head[1]} L{len(current_state.snakes[1].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                return game_sequence

            # get snake, for which sequence needs to be created
            # take prev state, since turn is for the previous one, the one that moved and 
            # whose move resulted in current_state
            currently_moving_snake_idx = prev_state.turn % prev_state.n_snakes
            # current snake is dead, return dead sequence if this happens
            # if the snake dies in the current turn we still provide valid position for the last move
            # token dead shows up if it was already dead
            if currently_moving_snake_idx in prev_state.eliminated_snakes:
                apple_positions = ' '.join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples])
                # dead snake gets S_AGENT_IDX <DEAD> L10 A12A23A34A35A36 
                game_sequence += f"S{currently_moving_snake_idx} <DEAD> L{len(current_state.snakes[currently_moving_snake_idx].tail)} {apple_positions} "
                return game_sequence
            # normal sequence filling
            else:
                game_sequence += f"S{currently_moving_snake_idx} R{current_state.snakes[currently_moving_snake_idx].head[0]}C{current_state.snakes[currently_moving_snake_idx].head[1]} L{len(current_state.snakes[currently_moving_snake_idx].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                return game_sequence


        elif corpora_type == APPLES_CORPORA:
            # prev_state is the state before currently_moving_snake_idx move
            # state is the state after

            # EACH SEQUENCE NEEDS TO FINISH WITH SPACE

            # initializing sequence
            if prev_state == None:
                assert game_sequence == "", "At the beginning game sequence shouldn't be empty"
                game_sequence = "<START> "
                game_sequence += f"S0 R{current_state.snakes[0].head[0]}C{current_state.snakes[0].head[1]} L{len(current_state.snakes[0].tail)} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                game_sequence += f"S1 R{current_state.snakes[1].head[0]}C{current_state.snakes[1].head[1]} L{len(current_state.snakes[1].tail)} "
                game_sequence += "<APPLES_UNCHANGED> "
                return game_sequence
            
            currently_moving_snake_idx = prev_state.turn % prev_state.n_snakes

            if currently_moving_snake_idx in prev_state.eliminated_snakes:
                # if in the previous state snake was already dead, apples certainly won't change
                game_sequence += f"S{currently_moving_snake_idx} <DEAD> L{len(current_state.snakes[currently_moving_snake_idx].tail)} <APPLES_UNCHANGED> "
                return game_sequence
            # normal sequence filling
            else:

                # get apple that was added after eating, or write <APPLES_UNCHANGED> if nothing was eaten
                cur_apples = [(apple.position[0], apple.position[1]) for apple in current_state.apples]
                prev_apples = [(apple.position[0], apple.position[1]) for apple in prev_state.apples]
                diff = list(set(cur_apples) - set(prev_apples))

                s0 = prev_state.get_full_history()
                s1 = current_state.get_full_history()
                
                assert diff == [] or len(diff) == 1, f"only one apple can differ {s0}\n\n{s1}\n\n{diff}"
                assert diff == [] or diff not in prev_apples, "assert that new apple was actually added"

                # if apple was eaten, show the new apple position
                game_sequence += f"S{currently_moving_snake_idx} R{current_state.snakes[currently_moving_snake_idx].head[0]}C{current_state.snakes[currently_moving_snake_idx].head[1]} L{len(current_state.snakes[currently_moving_snake_idx].tail)} "
                if diff != []:
                    apple = diff[0]
                    game_sequence += f"A{apple[0]}{apple[1]} "
                else:
                    game_sequence += "<APPLES_UNCHANGED> "
                
                return game_sequence

        elif corpora_type == NO_TAILS:
            # essentially the same as standard, but without tails
            
            # initializing sequence
            if prev_state == None:
                assert game_sequence == "", "At the beginning game sequence shouldn't be empty"
                game_sequence = "<START> "
                game_sequence += f"S0 R{current_state.snakes[0].head[0]}C{current_state.snakes[0].head[1]} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                game_sequence += f"S1 R{current_state.snakes[1].head[0]}C{current_state.snakes[1].head[1]} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                return game_sequence

            # get snake, for which sequence needs to be created
            # take prev state, since turn is for the previous one, the one that moved and 
            # whose move resulted in current_state
            currently_moving_snake_idx = prev_state.turn % prev_state.n_snakes
            # current snake is dead, return dead sequence if this happens
            # if the snake dies in the current turn we still provide valid position for the last move
            # token dead shows up if it was already dead
            if currently_moving_snake_idx in prev_state.eliminated_snakes:
                apple_positions = ' '.join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples])
                # dead snake gets S_AGENT_IDX <DEAD> L10 A12A23A34A35A36 
                game_sequence += f"S{currently_moving_snake_idx} <DEAD> {apple_positions} "
                return game_sequence
            # normal sequence filling
            else:
                game_sequence += f"S{currently_moving_snake_idx} R{current_state.snakes[currently_moving_snake_idx].head[0]}C{current_state.snakes[currently_moving_snake_idx].head[1]} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                return game_sequence


        elif corpora_type == MINIMAL:
            # EACH SEQUENCE NEEDS TO FINISH WITH SPACE

            # initializing sequence
            if prev_state == None:
                assert game_sequence == "", "At the beginning game sequence shouldn't be empty"
                game_sequence = "<START> "
                game_sequence += f"S0 R{current_state.snakes[0].head[0]}C{current_state.snakes[0].head[1]} "
                game_sequence += " ".join([f'A{apple.position[0]}{apple.position[1]}' for apple in current_state.apples]) + " "
                game_sequence += f"S1 R{current_state.snakes[1].head[0]}C{current_state.snakes[1].head[1]} "
                game_sequence += "<APPLES_UNCHANGED> "
                return game_sequence
            
            currently_moving_snake_idx = prev_state.turn % prev_state.n_snakes

            if currently_moving_snake_idx in prev_state.eliminated_snakes:
                # if in the previous state snake was already dead, apples certainly won't change
                game_sequence += f"S{currently_moving_snake_idx} <DEAD> <APPLES_UNCHANGED> "
                return game_sequence
            # normal sequence filling
            else:

                # get apple that was added after eating, or write <APPLES_UNCHANGED> if nothing was eaten
                cur_apples = [(apple.position[0], apple.position[1]) for apple in current_state.apples]
                prev_apples = [(apple.position[0], apple.position[1]) for apple in prev_state.apples]
                diff = list(set(cur_apples) - set(prev_apples))

                s0 = prev_state.get_full_history()
                s1 = current_state.get_full_history()
                
                assert diff == [] or len(diff) == 1, f"only one apple can differ {s0}\n\n{s1}\n\n{diff}"
                assert diff == [] or diff not in prev_apples, "assert that new apple was actually added"

                # if apple was eaten, show the new apple position
                game_sequence += f"S{currently_moving_snake_idx} R{current_state.snakes[currently_moving_snake_idx].head[0]}C{current_state.snakes[currently_moving_snake_idx].head[1]} "
                if diff != []:
                    apple = diff[0]
                    game_sequence += f"A{apple[0]}{apple[1]} "
                else:
                    game_sequence += "<APPLES_UNCHANGED> "
                
                return game_sequence

        else:
            raise Exception("Incorrect Corpora Type")