:-ensure_loaded("pokemon_list.pl").
:-ensure_loaded("pokemon_info_attacks.pl").
:-ensure_loaded("pokemon_route.pl").

player_starts(0,0).

% TO DO

% percorre a matrix para encontrar o elemento (x,y)
nth0_element(0, [H|_], H).
nth0_element(N, [_|T], E) :-
    N > 0,
    N1 is N - 1,
    nth0_element(N1, T, E).

% indica qual as coordnada para a função nth0_element
get_cell(X, Y, Id, Level) :-
    route(M),
    nth0_element(Y, M, Row),
    nth0_element(X, Row, (Id, Level)).

% verifica se a posição está dentro dos limites
in_bounds(X, Y) :-
    X >= 0, X < 5, Y >= 0, Y < 5.

% obtem as imformlções sobre o vizinho
neighbor_info(NX, NY, [Id, Name, Level, NX, NY, Types]) :-
    in_bounds(NX, NY),
    get_cell(NX, NY, Id, Level),
    Id \= 0,
    pokemon(Id, Name, Types).

% obtem os elementos adjacentes
next_rooms(X, Y, Rooms) :-
    findall(Info,
        (   (NX is X - 1, NY is Y ;
             NX is X + 1, NY is Y ;
             NX is X, NY is Y - 1 ;
             NX is X, NY is Y + 1),
            neighbor_info(NX, NY, Info)
        ),
        Rooms).