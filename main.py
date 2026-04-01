import random
pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 2, 1, 1, 2, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]


piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores,
                       "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores}


CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
SET_WHITE_AS_BOT = -1

_ab_data = {'vis_nodes': [], 'nodes_explored': 0, 'nodes_pruned': 0, 'best_score': 0.0, 'depth_windows': {}}
MAX_VIS_TOP = 4
MAX_VIS_CHILDREN = 3


def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def _vis_add(parent_id, depth, move_str, alpha, beta):
    nodes = _ab_data['vis_nodes']
    if depth == DEPTH:
        if sum(1 for n in nodes if n['parent'] == -1) >= MAX_VIS_TOP:
            return -1
    elif depth == DEPTH - 1:
        if parent_id < 0:
            return -1
        if sum(1 for n in nodes if n['parent'] == parent_id) >= MAX_VIS_CHILDREN:
            return -1
    else:
        return -1
    nid = len(nodes)
    nodes.append({'id': nid, 'parent': parent_id, 'depth': depth,
                  'move': str(move_str)[:5], 'alpha': round(alpha, 1), 'beta': round(beta, 1),
                  'score': None, 'pruned': False, 'best': False})
    return nid


def findBestMove(gs, validMoves, returnQueue, abQueue=None):
    global nextMove, whitePawnScores, blackPawnScores, _ab_data
    nextMove = None
    _ab_data = {'vis_nodes': [], 'nodes_explored': 0, 'nodes_pruned': 0, 'best_score': 0.0, 'depth_windows': {}}
    random.shuffle(validMoves)
    if gs.playerWantsToPlayAsBlack:
        whitePawnScores, blackPawnScores = blackPawnScores, whitePawnScores
    SET_WHITE_AS_BOT = 1 if gs.whiteToMove else -1
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, SET_WHITE_AS_BOT, abQueue, -1)
    if abQueue:
        abQueue.put({**_ab_data, 'done': True})
    returnQueue.put(nextMove)


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, abQueue=None, parent_id=-1):
    global nextMove, _ab_data
    _ab_data['nodes_explored'] += 1
    _ab_data['depth_windows'][depth] = (round(alpha, 1), round(beta, 1))
    if abQueue and _ab_data['nodes_explored'] % 30 == 0:
        abQueue.put(dict(_ab_data))
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        nid = _vis_add(parent_id, depth, str(move), alpha, beta)
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier, abQueue, nid)
        if nid >= 0:
            _ab_data['vis_nodes'][nid]['score'] = round(score, 1)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                _ab_data['best_score'] = round(score, 2)
                for n in _ab_data['vis_nodes']:
                    if n['depth'] == DEPTH:
                        n['best'] = False
                if nid >= 0:
                    _ab_data['vis_nodes'][nid]['best'] = True
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            _ab_data['nodes_pruned'] += 1
            if nid >= 0:
                _ab_data['vis_nodes'][nid]['pruned'] = True
            break
    return maxScore


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            gs.checkmate = False
            return -CHECKMATE
        else:
            gs.checkmate = False
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]
                if SET_WHITE_AS_BOT:
                    if square[0] == 'w':
                        score += pieceScore[square[1]] + piecePositionScore * .1
                    elif square[0] == 'b':
                        score -= pieceScore[square[1]] + piecePositionScore * .1
                else:
                    if square[0] == 'w':
                        score -= pieceScore[square[1]] + piecePositionScore * .1
                    elif square[0] == 'b':
                        score += pieceScore[square[1]] + piecePositionScore * .1
    return score
