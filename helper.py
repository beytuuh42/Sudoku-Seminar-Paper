import copy


def check_is_valid(block, cells, selected_cell, value):
    is_valid_block = check_in_block(block, value)
    is_valid_xy = check_in_row_and_column(cells, selected_cell, value)

    return True if is_valid_block and is_valid_xy else False


def check_in_block(block, value):
    for cell in block.cells:
        if cell.value == value:
            return False
    return True


def check_in_row_and_column(cells, selected_cell, value):
    for c in cells:
        if c.position_tuple[0] == selected_cell.position_tuple[0] and c.position_tuple[1] != selected_cell.position_tuple[1]:
            if c.value == value:
                return False
        if c.position_tuple[1] == selected_cell.position_tuple[1] and c.position_tuple[0] != selected_cell.position_tuple[0]:
            if c.value == value:
                return False
    return True


def check_is_finished(blocks):
    for b in blocks:
        if not b.is_completed:
            return False
    return True


def show_hint_naked_single(cells):
    hints = []

    for cell in cells:
        candidates = list(filter(lambda x: x.value != 0, cell.candidates))
        if len(candidates) == 1:
            hints.append(f"Naked Single {candidates[0].value} in block {cell.block_no}")

    return hints
    # check all cells if they have single candidate


def show_hint_hidden_single(blocks, cells):
    # Naked singles are shown as hidden when progressed

    # 1 check all cells in block if they have candidate of single occurence
    # 2 check all cells in xy if they have candidate of single occurence

    candidates = [x for x in range(1, 10)]
    position_dict = {}
    hints = []

    for can_value in candidates:
        for block in blocks:
            candidate_counter = 0
            c = None
            for cell in block.cells:
                if cell.value == can_value:
                    break
                for candidate in cell.candidates:
                    if candidate.value == can_value:
                        c = cell
                        candidate_counter += 1
                if candidate_counter > 1:
                    break
            else:
                position_dict[c] = can_value
                #print(
                #    f"Hidden single {can_value} in position {c.position_tuple}")

    # row and column
    for can_value in candidates:
        candidate_counter = 0
        c = None
        for i in range(2):
            for j in range(9):
                candidate_counter = 0
                for cell in cells:
                    if cell.position_tuple[i] == j:
                        for can in cell.candidates:
                            if can.value == can_value:
                                candidate_counter += 1
                                c = cell
                if candidate_counter == 1:
                    position_dict[c] = can_value

                    #print(
                    #    f"Hidden Single for {'row' if  i == 0 else 'column'} in {c.position_tuple}, value {can_value}")
    result = {}
    if position_dict:
        for key,value in position_dict.items():
            if value not in result.values():
                result[key] = value
        for key, val in result.items():
            hints.append(f"Hidden Single {val} in block {key.block_no}")
    return hints


def show_hint_hidden_pair(blocks, cells):
    pair_hints = []

    for block in blocks:
        candidates = []

        for cell in block.cells:
            values = []
            for candidate in cell.candidates:
                if candidate.value:
                    values.append(candidate.value)
            if values:
                candidates.append(sorted(values))

        new_candidates = copy.deepcopy(candidates)

        for i in range(1, 10):
            can_counter = 0
            for can in new_candidates:
                if i in can:
                    can_counter += 1
                if can_counter > 2:
                    for can in new_candidates:
                        if i in can:
                            can.remove(i)
                    break
        new_candidates = list(filter(lambda x: len(x) != 1, new_candidates))
        for idx, c in enumerate(new_candidates):
            if c:
                if len(candidates[idx]) <= 2:
                    new_candidates.remove(c)

        new_candidates = [can for can in new_candidates if can]

        """ if len(new_candidates) == 2 and new_candidates[0][0] == new_candidates[1][0] and new_candidates[0][1] == new_candidates[1][1]:
            print(f"Hidden pair {new_candidates[0]} in Block {block.number}") """

    for q in range(2):
        for j in range(9):
            candidates = []
            for cell in cells:
                if cell.position_tuple[q] == j:
                    values = []
                    for candidate in cell.candidates:
                        if candidate.value:
                            values.append(candidate.value)
                    if values:
                        candidates.append(sorted(values))

            new_candidates = copy.deepcopy(candidates)

            # löschen kandidaten die mehr als 2x vorkommen
            for i in range(1, 10):
                can_counter = 0
                for can in new_candidates:
                    if i in can:
                        can_counter += 1
                    if can_counter > 2:
                        for can in new_candidates:
                            if i in can:
                                can.remove(i)
                        break

            # filter liste nach pairs
            new_candidates = list(
                filter(lambda x: len(x) != 1, new_candidates))

            new_candidates = list(filter(lambda x: x, new_candidates))

            # momentan beide pairs
            # logik, wenn eines der paare in candidates andere candidates hat, dann hidden pair, ansonsten naked pair

            if len(new_candidates) == 2 and new_candidates[0] == new_candidates[1] and len(candidates) >= 2:
                if candidates.count(new_candidates[0]) > 1:
                    pair_hints.append(f"Naked Pair {new_candidates[0]} in {'column' if q == 0 else 'row'} {j+1}")
                else:
                    pair_hints.append(f"Hidden Pair {new_candidates[0]} in {'column' if q == 0 else 'row'} {j+1}")

    return pair_hints


def show_hint_x_wing(cells):
    # for first pair
    candidates = [x for x in range(1, 10)]
    hints = []

    for can_value in candidates:
        for i in range(2):
            c = []
            black_list = []
            for j in range(9):
                if black_list:
                    for p in black_list:
                        if p[0].position_tuple[i] == j:
                            break
                    else:
                        break
                candidate_counter = 0
                c = []
                for cell in cells:
                    if cell.position_tuple[i] == j:
                        for can in cell.candidates:
                            if can.value == can_value:
                                candidate_counter += 1
                                c.append(cell)
                if candidate_counter == 2:
                    pair2 = has_x_wing(c, cells, can_value,
                                       False if i == 0 else True)
                    if pair2:
                        y = 0 if i == 0 else 1
                        hints.append(f"X-Wing at {'column' if  i == 0 else 'row'} {j+1} and {pair2[0].position_tuple[y]+1}\nfor value {can_value}")
                        #print(
                        #    f"Pair1 in {'column' if  i == 0 else 'row'} {j+1} for value {can_value}")
                        black_list.append(pair2)
    
    return hints


def has_x_wing(pair, cells, can_value, is_in_row):
    # for second pair
    x = 1 if is_in_row else 0
    y = 0 if is_in_row else 1
    pair1, pair2 = pair
    
    for j in range(9):
        candidate_counter = 0
        c = []
        for cell in cells:
            if cell.position_tuple[x] == j and (cell != pair1 and cell != pair2):
                for can in cell.candidates:
                    if can.value == can_value:
                        candidate_counter += 1
                        c.append(cell)

        if candidate_counter == 2:
            pair3, pair4 = c
            if pair1.position_tuple[y] == pair3.position_tuple[y] and pair2.position_tuple[y] == pair4.position_tuple[y]:
                group1, group2 = pair1.position_tuple[y], pair2.position_tuple[y]
                #print(
                #    f"Pair2 in {'column' if  x == 0 else 'row'} {j+1} for value {can_value} | {pair1.position_tuple[y]}, {pair2.position_tuple[y]}")
                # print(f"The candidate {can_value} can be removed from {} due to xwing from ")
                for cell in cells:
                    if (cell.position_tuple[y] == group1 or cell.position_tuple[y] == group2) and can_value in [can.value for can in cell.candidates]:
                        if cell not in pair and cell not in c:
                            print(f"To be deleted {cell.position_tuple}")
                return c
            break


def check_candidates(block, cells, cell, value):
    # res = check_is_valid(block, cells, cell, value)
    # print(f"Checking candidate value {value} in position {cell.position_tuple} in block {block.position_tuple} - {res}")
    return check_is_valid(block, cells, cell, value)


def is_int(string):
    try:
        int(string)
        return True
    except Exception:
        return False
