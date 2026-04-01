import random
from pyswip import Prolog
from game.pokemon_fuzzy import calculate_prob

class PokemonGame:

    def __init__(self, prolog_file="prolog/pokemon_game.pl", starter_id=1, starter_level=4):
        self.prolog = Prolog()
        self.prolog.consult(prolog_file)

        # Player initial position
        result = list(self.prolog.query("player_starts(X,Y)"))
        self.x_initial = result[0]['X']
        self.y_initial = result[0]['Y']
        self.pos = (self.x_initial,self.y_initial)
        # Starter pokemon
        self.pokemon_starter = starter_id
        self.pokemon_level = starter_level

        pokemon_info = list(self.prolog.query(
            f"pokemon({self.pokemon_starter},Name,Types)"))[0]

        self.pokemon_starter_name = pokemon_info['Name']
        self.pokemon_starter_types = pokemon_info['Types']

        print(f"Player is {self.pokemon_starter_name}, level = {self.pokemon_level}, type = {self.pokemon_starter_types}")
        print(f"Initial position ({self.pos})")

        self.visited_rooms = [self.pos]
        self.game_over = False
        self.number_of_pokemons = 25

    # --------------------------------

    def total_attack(self, attacker_types, defender_types):
        best_effect = 0
        for a_type in attacker_types:
            combined_effect = 1
            for d_type in defender_types:
                result = list(self.prolog.query(f"attack({a_type},{d_type},Effect)"))
                if result:
                    combined_effect *= result[0]['Effect']
            if combined_effect > best_effect:
                best_effect = combined_effect
        return best_effect

    # --------------------------------

    def evaluate_next_rooms(self, pokemon_level, pos):

        list_next_rooms = list(self.prolog.query(f"next_rooms({pos[0]},{pos[1]},L)"))

        best_room = None
        best_prob = -1

        for room in list_next_rooms[0]['L']:

            if (room[3], room[4]) not in self.visited_rooms:

                level_input = pokemon_level - room[2]
                effect_input = self.total_attack(
                    self.pokemon_starter_types, room[5])

                prob_of_win = calculate_prob(level_input, effect_input)
                # print(f"level_input: {level_input} effect_input: {effect_input}")
                # print("Possible Room:", room, "Probability of win:", prob_of_win)

                if prob_of_win > best_prob:
                    best_prob = prob_of_win
                    best_room = room

        return best_room, best_prob

    # --------------------------------

    def compute_damage(self, attacker_types, defender_types):
        damage = self.total_attack(attacker_types, defender_types)
        
        message = ""
        if damage == 0:
            message = "It doesn't affect the opponent..."
        elif damage < 1:
            message = "It's not very effective..."
        elif damage > 1:
            message = "It's super effective!"

        success = random.random()
        if success < 0.05:
            damage = 0
            message = "Oh no! The attack missed!"
        elif success > 0.95:
            damage *= 2
            message = "Critical hit!"

        return damage, message
    
    # --------------------------------

    def it_wins(self, next_room):
        opponent_name = next_room[1]
        opponent_hp = next_room[2]
        opponent_types = next_room[5]
        print(f"A wild {opponent_name.capitalize()} appears! Level: {opponent_hp}, Type: {opponent_types}")
        first = random.random() > 0.5
        print("First attack:", "Player" if first else "Opponent")

        player_hp = self.pokemon_level
        while player_hp > 0 and opponent_hp > 0:
            if first:
                damage, message = self.compute_damage(self.pokemon_starter_types, opponent_types)
                opponent_hp -= damage
                print(f"{self.pokemon_starter_name.capitalize()} attacks! {message}")
                print(f"Damage: {damage}, {opponent_name.capitalize()} HP: {max(0, opponent_hp)}")
            else:
                damage, message = self.compute_damage(opponent_types, self.pokemon_starter_types)
                player_hp -= damage
                print(f"{opponent_name.capitalize()} attacks! {message}")
                print(f"Damage: {damage}, {self.pokemon_starter_name.capitalize()} HP: {max(0, player_hp)}")
            first = not first

        return player_hp > 0

    # --------------------------------

    def update_level(self, defender_level):
        if self.pokemon_level < 10:
            if self.pokemon_level < defender_level:
                    self.pokemon_level += 1
            elif self.pokemon_level > defender_level:
                value = random.random()
                if value <= 0.3:
                    self.pokemon_level += 1
            else: 
                    value = random.random()
                    if value <= 0.5:
                        self.pokemon_level += 1
        print(f"Pokemon level: {self.pokemon_level}")

    # --------------------------------

    def get_random_pos(self, x, y, rows, cols):
        moves = [
            (x-1, y),  # up
            (x+1, y),  # down
            (x, y-1),  # left
            (x, y+1)   # right
        ]
        valid_moves = [
            (nx, ny) for nx, ny in moves
            if 0 <= nx < rows and 0 <= ny < cols
        ]
        return random.choice(valid_moves)
    
    # --------------------------------

    def next_step(self):
        """
        Returns:
            old_pos, new_pos, prob_of_win, game_over
        """
        if self.game_over:
            return None, None, None, True

        next_room, prob = self.evaluate_next_rooms(self.pokemon_level, self.pos)
        
        if next_room == None:
            if len(self.visited_rooms) != self.number_of_pokemons:
                (old_x,old_y) = self.pos
                old_pos = self.pos
                new_x, new_y = self.get_random_pos(old_x,old_y,5,5)
                self.pos = (new_x,new_y)
                return old_pos, self.pos, None, False
            else:
                print("Yeah! You won!")
                return None, None, None, True
        else:
            print(f"Next Room: {next_room}, probability of win: {prob}")
            won = self.it_wins(next_room)
            self.game_over = not won
            
            if won:
                old_pos = self.pos
                new_pos = (next_room[3], next_room[4])

                self.visited_rooms.append(new_pos)
                self.pos = new_pos

                self.update_level(next_room[2])
            else:
                return None, None, None, self.game_over

        return old_pos, new_pos, prob, self.game_over

    
    # --------------------------------

   