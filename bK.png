import sys
import pygame as p
from engine import GameState, Move
from chessAi import findRandomMoves, findBestMove, CHECKMATE, DEPTH
from multiprocessing import Process, Queue

p.mixer.init()
move_sound = p.mixer.Sound("sounds/move-sound.mp3")
capture_sound = p.mixer.Sound("sounds/capture.mp3")
promote_sound = p.mixer.Sound("sounds/promote.mp3")

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
AB_PANEL_WIDTH = 340
AB_PANEL_HEIGHT = 680
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

SET_WHITE_AS_BOT = False
SET_BLACK_AS_BOT = True

LIGHT_SQUARE_COLOR = (220, 220, 220)
DARK_SQUARE_COLOR = (170, 170, 170)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (164, 184, 196)


def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        original_image = p.image.load("images1/" + piece + ".png")
        IMAGES[piece] = p.transform.smoothscale(original_image, (SQ_SIZE, SQ_SIZE))


def pawnPromotionPopup(screen, gs):
    font = p.font.SysFont("Times New Roman", 30, False, False)
    text = font.render("Choose promotion:", True, p.Color("black"))
    button_width, button_height = 100, 100
    buttons = [
        p.Rect(100, 200, button_width, button_height),
        p.Rect(200, 200, button_width, button_height),
        p.Rect(300, 200, button_width, button_height),
        p.Rect(400, 200, button_width, button_height)
    ]
    color_prefix = 'b' if gs.whiteToMove else 'w'
    button_images = [
        p.transform.smoothscale(p.image.load(f"images1/{color_prefix}Q.png"), (100, 100)),
        p.transform.smoothscale(p.image.load(f"images1/{color_prefix}R.png"), (100, 100)),
        p.transform.smoothscale(p.image.load(f"images1/{color_prefix}B.png"), (100, 100)),
        p.transform.smoothscale(p.image.load(f"images1/{color_prefix}N.png"), (100, 100))
    ]
    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                for i, button in enumerate(buttons):
                    if button.collidepoint(e.pos):
                        return ["Q", "R", "B", "N"][i]
        screen.fill(p.Color(LIGHT_SQUARE_COLOR))
        screen.blit(text, (110, 150))
        for i, button in enumerate(buttons):
            p.draw.rect(screen, p.Color("white"), button)
            screen.blit(button_images[i], button.topleft)
        p.display.flip()


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH + AB_PANEL_WIDTH,
                                   max(BOARD_HEIGHT, AB_PANEL_HEIGHT)))
    p.display.set_caption("PawnHub |  AI Chess Engine")
    clock = p.time.Clock()
    screen.fill(p.Color(LIGHT_SQUARE_COLOR))
    moveLogFont = p.font.SysFont("Times New Roman", 12, False, False)
    gs = GameState()
    if gs.playerWantsToPlayAsBlack:
        gs.board = gs.board1
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    squareSelected = ()
    playerClicks = []
    gameOver = False
    playerWhiteHuman = not SET_WHITE_AS_BOT
    playerBlackHuman = not SET_BLACK_AS_BOT
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    pieceCaptured = False
    positionHistory = ""
    previousPos = ""
    countMovesForDraw = 0
    COUNT_DRAW = 0
    ab_stats = {'nodes_explored': 0, 'nodes_pruned': 0, 'best_score': 0, 'depth_windows': {}, 'vis_nodes': []}
    abQueue = None
    while running:
        humanTurn = (gs.whiteToMove and playerWhiteHuman) or (
            not gs.whiteToMove and playerBlackHuman)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if squareSelected == (row, col) or col >= 8:
                        squareSelected = ()
                        playerClicks = []
                    else:
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if gs.board[validMoves[i].endRow][validMoves[i].endCol] != '--':
                                    pieceCaptured = True
                                gs.makeMove(validMoves[i])
                                if move.isPawnPromotion:
                                    promotion_choice = pawnPromotionPopup(screen, gs)
                                    gs.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotion_choice
                                    promote_sound.play()
                                    pieceCaptured = False
                                if pieceCaptured or move.isEnpassantMove:
                                    capture_sound.play()
                                elif not move.isPawnPromotion:
                                    move_sound.play()
                                pieceCaptured = False
                                moveMade = True
                                animate = True
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()
                abQueue = Queue()
                ab_stats = {'nodes_explored': 0, 'nodes_pruned': 0, 'best_score': 0, 'depth_windows': {}, 'vis_nodes': []}
                moveFinderProcess = Process(target=findBestMove, args=(gs, validMoves, returnQueue, abQueue))
                moveFinderProcess.start()
            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = findRandomMoves(validMoves)
                if gs.board[AIMove.endRow][AIMove.endCol] != '--':
                    pieceCaptured = True
                gs.makeMove(AIMove)
                if AIMove.isPawnPromotion:
                    promotion_choice = pawnPromotionPopup(screen, gs)
                    gs.board[AIMove.endRow][AIMove.endCol] = AIMove.pieceMoved[0] + promotion_choice
                    promote_sound.play()
                    pieceCaptured = False
                if pieceCaptured or AIMove.isEnpassantMove:
                    capture_sound.play()
                elif not AIMove.isPawnPromotion:
                    move_sound.play()
                pieceCaptured = False
                AIThinking = False
                moveMade = True
                animate = True
                squareSelected = ()
                playerClicks = []

        if moveMade:
            if countMovesForDraw < 4:
                countMovesForDraw += 1
            if countMovesForDraw == 4:
                positionHistory += gs.getBoardString()
                if previousPos == positionHistory:
                    COUNT_DRAW += 1
                    positionHistory = ""
                    countMovesForDraw = 0
                else:
                    previousPos = positionHistory
                    positionHistory = ""
                    countMovesForDraw = 0
                    COUNT_DRAW = 0
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        if abQueue is not None:
            try:
                while True:
                    stats = abQueue.get_nowait()
                    ab_stats.update(stats)
            except Exception:
                pass
        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont, ab_stats, AIThinking)

        if COUNT_DRAW == 1:
            gameOver = True
            text = 'Draw due to repetition'
            drawEndGameText(screen, text)
        if gs.stalemate:
            gameOver = True
            text = 'Stalemate'
            drawEndGameText(screen, text)
        elif gs.checkmate:
            gameOver = True
            text = 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont, ab_stats=None, ai_thinking=False):
    drawSquare(screen)
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)
    drawABPanel(screen, ab_stats or {}, ai_thinking)


def drawSquare(screen):
    global colors
    colors = [p.Color(LIGHT_SQUARE_COLOR), p.Color(DARK_SQUARE_COLOR)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():  # make sure there is a square to select
        row, col = squareSelected
        # make sure they click there own piece
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected piece square
            # Surface in pygame used to add images or transperency feature
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            # set_alpha --> transperancy value (0 transparent)
            s.set_alpha(100)
            s.fill(p.Color(MOVE_HIGHLIGHT_COLOR))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
            # highlighting valid square
            s.fill(p.Color(POSSIBLE_MOVE_COLOR))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color(LIGHT_SQUARE_COLOR), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = " " + str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1])
        moveTexts.append(moveString)
    movesPerRow = 3
    padding = 10
    lineSpacing = 5
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('black'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


def animateMove(move, screen, board, clock):
    global colors
    deltaRow = move.endRow - move.startRow
    deltaCol = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = (abs(deltaRow) + abs(deltaCol)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, col = (move.startRow + deltaRow*frame/frameCount, move.startCol + deltaCol*frame/frameCount)
        drawSquare(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(240)


def drawABPanel(screen, ab_stats, ai_thinking):
    # ── colour palette (soft, not cave-dark) ─────────────────
    C_BG      = (34, 38, 54)       # panel background
    C_DIV     = (62, 68, 95)       # divider line
    C_TITLE   = (232, 192, 52)     # section title (warm gold)
    C_LABEL   = (175, 180, 210)    # regular body text
    C_MUTED   = (118, 124, 158)    # secondary/muted text
    C_ALPHA   = (108, 168, 248)    # alpha values (blue)
    C_BETA    = (245, 110, 110)    # beta values  (red-pink)
    C_SCORE   = (105, 228, 122)    # positive score
    C_PRUNED  = (248, 82,  82)     # pruned text / X
    C_BEST    = (248, 208, 42)     # best node highlight
    C_CONN    = (72,  78, 108)     # connector lines

    panel_x = BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH
    p.draw.rect(screen, p.Color(*C_BG), p.Rect(panel_x, 0, AB_PANEL_WIDTH, AB_PANEL_HEIGHT))

    TF  = p.font.SysFont("Consolas", 13, True,  False)  # section title
    LF  = p.font.SysFont("Consolas", 11, False, False)  # body
    LBF = p.font.SysFont("Consolas", 11, True,  False)  # bold body
    NF  = p.font.SysFont("Consolas", 10, True,  False)  # node text
    SF  = p.font.SysFont("Consolas",  9, False, False)  # tiny caption
    pad = 10                                             # left/right padding
    IW  = AB_PANEL_WIDTH - pad * 2                      # inner width = 320
    y   = 6

    def divider():
        nonlocal y
        p.draw.line(screen, p.Color(*C_DIV),
                    (panel_x + pad, y), (panel_x + AB_PANEL_WIDTH - pad, y))
        y += 6

    def txt(font, text, col, x=None):
        nonlocal y
        s = font.render(text, True, p.Color(*col))
        screen.blit(s, (panel_x + (x if x is not None else pad), y))
        y += s.get_height() + 2

    def kv(label, value, vc):
        nonlocal y
        ls = LF.render(label,       True, p.Color(*C_MUTED))
        vs = LBF.render(str(value), True, p.Color(*vc))
        screen.blit(ls, (panel_x + pad, y))
        screen.blit(vs, (panel_x + AB_PANEL_WIDTH - vs.get_width() - pad, y))
        y += ls.get_height() + 2

    def ab_fmt(v):
        if v >= 999:  return "+\u221e"
        if v <= -999: return "-\u221e"
        return f"{v:.0f}"

    # ─── Title & status ──────────────────────────────────────
    txt(TF, "Alpha-Beta Pruning", C_TITLE)
    dot_c = (75, 205, 98) if ai_thinking else (108, 112, 145)
    txt(LF, "  \u25cf  SEARCHING..." if ai_thinking else "  \u25cf  IDLE", dot_c)
    y += 2; divider()

    # ─── Live stats ──────────────────────────────────────────
    txt(TF, "Live Stats", C_TITLE)
    nodes_e = ab_stats.get('nodes_explored', 0)
    nodes_p = ab_stats.get('nodes_pruned', 0)
    best_sc = ab_stats.get('best_score', 0)
    kv("Nodes Explored:", f"{nodes_e:,}",   C_ALPHA)
    kv("Nodes Pruned:",   f"{nodes_p:,}",   C_BETA)
    kv("Best Score:",     f"{best_sc:+.2f}", C_SCORE)
    y += 2; divider()

    # ─── How it works ────────────────────────────────────────
    txt(TF, "How Alpha-Beta Works", C_TITLE)
    txt(LF, "\u03b1  =  best score AI is guaranteed",       C_LABEL)
    txt(LF, "\u03b2  =  best score opponent can limit AI to", C_LABEL)
    # Pruning rule box
    rh = 19
    p.draw.rect(screen, p.Color(72, 24, 24),
                p.Rect(panel_x + pad, y, IW, rh), border_radius=4)
    p.draw.rect(screen, p.Color(185, 55, 55),
                p.Rect(panel_x + pad, y, IW, rh), 1, border_radius=4)
    rule = LBF.render("If  \u03b1 \u2265 \u03b2  \u2192  PRUNE (skip branch!)", True, p.Color(*C_PRUNED))
    screen.blit(rule, (panel_x + pad + (IW - rule.get_width()) // 2, y + 3))
    y += rh + 4; divider()

    # ─── α/β windows table ───────────────────────────────────
    txt(TF, "\u03b1 / \u03b2 Search Windows", C_TITLE)
    txt(SF, "Live bounds at each depth level", C_MUTED)
    # Column positions: Depth=0, Alpha=col1, Beta=col2
    col1 = pad + 105
    col2 = pad + 210
    # Header
    screen.blit(LF.render("Depth",    True, p.Color(*C_MUTED)),  (panel_x + pad,  y))
    screen.blit(LF.render("Alpha \u03b1", True, p.Color(*C_ALPHA)), (panel_x + col1, y))
    screen.blit(LF.render("Beta \u03b2",  True, p.Color(*C_BETA)),  (panel_x + col2, y))
    y += LF.size("X")[1] + 3
    depth_windows = ab_stats.get('depth_windows', {})
    for d in sorted(depth_windows.keys(), reverse=True):
        a_val, b_val = depth_windows[d]
        role = "AI"  if d == DEPTH else "Opp"
        screen.blit(LF.render(f"  {d}  ({role})", True, p.Color(*C_LABEL)),  (panel_x + pad,  y))
        screen.blit(LBF.render(ab_fmt(a_val),      True, p.Color(*C_ALPHA)),  (panel_x + col1, y))
        screen.blit(LBF.render(ab_fmt(b_val),      True, p.Color(*C_BETA)),   (panel_x + col2, y))
        y += LF.size("X")[1] + 2
    y += 2; divider()

    # ─── Search tree ─────────────────────────────────────────
    txt(TF, "\u03b1-\u03b2 Search Tree", C_TITLE)

    # Legend  (fixed x positions, no concatenation)
    lx_e, lx_p, lx_b = pad, pad + 90, pad + 175
    screen.blit(SF.render("\u25a0 Explored", True, p.Color(75, 128, 215)),   (panel_x + lx_e, y))
    screen.blit(SF.render("\u25a0 Pruned",   True, p.Color(215, 72, 72)),    (panel_x + lx_p, y))
    screen.blit(SF.render("\u25a0 Best move", True, p.Color(215, 172, 38)),  (panel_x + lx_b, y))
    y += SF.size("X")[1] + 4

    # Role labels  (short, guaranteed to fit in 320px at 11px bold)
    screen.blit(LBF.render("\u25b6 Depth 2  AI   (MAX \u2191 wants HIGH)", True, p.Color(98, 158, 240)), (panel_x + pad, y))
    y += LBF.size("X")[1] + 2
    screen.blit(LBF.render("\u25b7 Depth 1  Opp  (MIN \u2193 wants LOW)",  True, p.Color(240, 128, 62)), (panel_x + pad, y))
    y += LBF.size("X")[1] + 6

    vis_nodes = ab_stats.get('vis_nodes', [])
    tree_y    = y

    # Root box  (centered)
    rcx     = panel_x + pad + IW // 2
    RW, RH  = 170, 26
    rbox    = p.Rect(rcx - RW // 2, tree_y, RW, RH)
    p.draw.rect(screen, p.Color(48, 54, 80), rbox, border_radius=4)
    p.draw.rect(screen, p.Color(88, 96, 135), rbox, 1, border_radius=4)
    rt_s = NF.render("SEARCH ROOT (current position)", True, p.Color(*C_LABEL))
    if rt_s.get_width() > RW - 4:
        rt_s = SF.render("SEARCH ROOT (current position)", True, p.Color(*C_LABEL))
    screen.blit(rt_s, (rbox.x + (RW - rt_s.get_width()) // 2,
                        rbox.y + (RH - rt_s.get_height()) // 2))
    root_bot = (rcx, tree_y + RH)

    # L1 nodes — AI / Maximizer  (4 slots × 80px each = 320px)
    l1_nodes = [n for n in vis_nodes if n['parent'] == -1]
    N1       = 4
    slw      = IW // N1   # 80 px per slot
    B1W, B1H = 72, 60
    l1_y     = tree_y + RH + 22

    for i, nd in enumerate(l1_nodes[:N1]):
        cx = panel_x + pad + slw * i + slw // 2
        p.draw.aaline(screen, p.Color(*C_CONN), root_bot, (cx, l1_y))

        if nd.get('best'):
            fc, bc = (148, 118, 18), (218, 178, 42)
        elif nd.get('pruned'):
            fc, bc = (148, 40, 40),  (205, 72,  72)
        else:
            fc, bc = (42,  88, 175), (72, 128, 222)

        box = p.Rect(cx - B1W // 2, l1_y, B1W, B1H)
        p.draw.rect(screen, p.Color(*fc), box, border_radius=4)
        p.draw.rect(screen, p.Color(*bc), box, 1, border_radius=4)

        # Move name  (row 1)
        mv = LBF.render(nd['move'][:6], True, p.Color(225, 232, 255))
        screen.blit(mv, (box.x + (B1W - mv.get_width()) // 2, box.y + 4))

        # Score / best / pending  (row 2)
        if nd.get('best'):
            sc_lbl = NF.render("\u2605 BEST", True, p.Color(*C_BEST))
            screen.blit(sc_lbl, (box.x + (B1W - sc_lbl.get_width()) // 2, box.y + 21))
            sc_str = f"{nd['score']:+.1f}" if nd['score'] is not None else "..."
            sc = NF.render(sc_str, True, p.Color(*C_SCORE))
            screen.blit(sc, (box.x + (B1W - sc.get_width()) // 2, box.y + 37))
        else:
            sc_str = f"{nd['score']:+.1f}" if nd['score'] is not None else "\u00b7 \u00b7 \u00b7"
            sc_col = C_SCORE if not nd.get('pruned') else C_PRUNED
            sc = NF.render(sc_str, True, p.Color(*sc_col))
            screen.blit(sc, (box.x + (B1W - sc.get_width()) // 2, box.y + 21))
            # α/β row  (row 3)
            ab_s = SF.render(f"\u03b1{ab_fmt(nd['alpha'])} \u03b2{ab_fmt(nd['beta'])}", True, p.Color(*C_MUTED))
            screen.blit(ab_s, (box.x + (B1W - ab_s.get_width()) // 2, box.y + 37))

        # Prune X overlay
        if nd.get('pruned'):
            p.draw.line(screen, p.Color(*C_PRUNED), box.topleft,  (box.right, box.bottom), 2)
            p.draw.line(screen, p.Color(*C_PRUNED), box.topright, (box.left,  box.bottom), 2)

        # Tag below box — pruned nodes only
        if nd.get('pruned'):
            tag = SF.render("\u2718 \u03b1\u2265\u03b2 pruned", True, p.Color(*C_PRUNED))
            tx  = max(panel_x + pad, min(cx - tag.get_width() // 2,
                                         panel_x + AB_PANEL_WIDTH - pad - tag.get_width()))
            screen.blit(tag, (tx, box.bottom + 2))

        # L2 nodes — Opponent / Minimizer  (3 sub-slots per slot)
        l2_nodes = [n for n in vis_nodes if n['parent'] == nd['id']]
        N2       = 3
        ssw      = slw // N2   # 26 px per sub-slot
        B2       = 22
        l2_y     = l1_y + B1H + 28

        for j, ch in enumerate(l2_nodes[:N2]):
            scx = panel_x + pad + slw * i + ssw * j + ssw // 2
            p.draw.aaline(screen, p.Color(*C_CONN), (cx, box.bottom), (scx, l2_y))

            if ch.get('pruned'):
                cc, brc = (148, 40, 40), (200, 68, 68)
            elif ch['score'] is None:
                cc, brc = (50, 56, 80),  (72, 78, 108)
            else:
                cc, brc = (42, 88, 175), (72, 128, 222)

            cb = p.Rect(scx - B2 // 2, l2_y, B2, B2)
            p.draw.rect(screen, p.Color(*cc),  cb, border_radius=3)
            p.draw.rect(screen, p.Color(*brc), cb, 1, border_radius=3)

            # Move name above L2 box
            mv2 = SF.render(ch['move'][:5], True, p.Color(*C_MUTED))
            screen.blit(mv2, (scx - mv2.get_width() // 2, l2_y - mv2.get_height() - 1))

            if ch.get('pruned'):
                p.draw.line(screen, p.Color(*C_PRUNED), cb.topleft,  (cb.right, cb.bottom), 2)
                p.draw.line(screen, p.Color(*C_PRUNED), cb.topright, (cb.left,  cb.bottom), 2)
                xl = SF.render("\u2718", True, p.Color(*C_PRUNED))
                screen.blit(xl, (scx - xl.get_width() // 2, cb.bottom + 2))
            elif ch['score'] is not None:
                sc2 = NF.render(f"{ch['score']:.1f}", True, p.Color(*C_MUTED))
                screen.blit(sc2, (scx - sc2.get_width() // 2, cb.bottom + 2))

    if not l1_nodes:
        ln1 = LF.render("Make a move to trigger AI search.", True, p.Color(*C_MUTED))
        ln2 = SF.render("Tree will appear here after AI responds.", True, p.Color(*C_MUTED))
        screen.blit(ln1, (panel_x + pad + (IW - ln1.get_width()) // 2, tree_y + 28))
        screen.blit(ln2, (panel_x + pad + (IW - ln2.get_width()) // 2, tree_y + 46))

    # ─── Footer (pinned) ─────────────────────────────────────
    fy = AB_PANEL_HEIGHT - 24
    p.draw.line(screen, p.Color(*C_DIV),
                (panel_x + pad, fy), (panel_x + AB_PANEL_WIDTH - pad, fy))
    fy += 4
    screen.blit(SF.render(f"NegaMax + \u03b1-\u03b2 pruning   depth: {DEPTH}", True, p.Color(*C_MUTED)),
                (panel_x + pad, fy))
    fy += 12
    screen.blit(SF.render("Pruned = redundant branches skipped", True, p.Color(72, 178, 95)),
                (panel_x + pad, fy))


def drawEndGameText(screen, text):
    font = p.font.SysFont("Times New Roman", 30, False, False)
    textObject = font.render(text, True, p.Color('black'))
    text_width = textObject.get_width()
    text_height = textObject.get_height()
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH/2 - text_width/2, BOARD_HEIGHT/2 - text_height/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(1, 1))


if __name__ == "__main__":
    main()
