:-ensure_loaded("pokemon_list.pl").
:-ensure_loaded("pokemon_info_attacks.pl").
:-ensure_loaded("pokemon_route.pl").

player_starts(0,0).

% percorre a matrix para encontrar o elemento (x,y)
n_element(0, [H|_], H).
n_element(N, [_|T], E) :-
    N > 0,
    N1 is N - 1,
    n_element(N1, T, E).

% indica qual as coordnada para a função n_lement
get_cell(X, Y, Id, Level) :-
    route(M),
    n_element(Y, M, Row),
    n_element(X, Row, (Id, Level)).

% verifica se a posição está dentro dos limites
in_bounds(X, Y) :-
    X >= 0, X < 5, Y >= 0, Y < 5.

% obtem as informações sobre o vizinho
neighbor_info(NX, NY, [Id, Name, Level, NX, NY, Types]) :-
    in_bounds(NX, NY),
    get_cell(NX, NY, Id, Level),
    Id \= 0,
    pokemon(Id, Name, Types).
    
% as quatro direções possíveis (esquerda, direita, baixo, cima)
direction(X, Y, NX, NY) :- NX is X - 1, NY is Y.
direction(X, Y, NX, NY) :- NX is X + 1, NY is Y.
direction(X, Y, NX, NY) :- NX is X,     NY is Y - 1.
direction(X, Y, NX, NY) :- NX is X,     NY is Y + 1.

% obtem os elementos adjacentes
next_rooms(X, Y, Rooms) :-
    findall(Info,
        (   direction(X, Y, NX, NY),
            neighbor_info(NX, NY, Info)
        ),
        Rooms).