import math
import os
import pyautogui
import numpy as np
import tile
from groupObj import Group, Cluster
from math import floor
from PIL import ImageGrab
import random
import sys
import time
import argparse
import keyboard
import logging
from operator import attrgetter

pyautogui.PAUSE = 0.001


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.perf_counter()
        ret = f(*args, **kwargs)
        time2 = time.perf_counter()
        print(
            f'\033[92m{f.__name__} function took {(time2-time1)*1000:.2f} ms.\x1b[0m')

        return ret
    return wrap


def dump(f):
    def wrap(*args, **kwargs):
        time1 = time.perf_counter()
        ret = f(*args, **kwargs)
        time2 = time.perf_counter()
        with open('output.log', 'a') as file:
            file.write(
                f'{f.__name__} function took {(time2-time1)*1000:.2f} ms.\n')

        return ret
    return wrap


def generate_all_posistion(count, mines):

    def search(current_comb, mines):

        if mines == 0:
            result.add(tuple(current_comb))
            return

        for pos, item in enumerate(current_comb):
            if not item:
                curr_copy = current_comb.copy()
                curr_copy[pos] = True
                search(curr_copy, mines - 1)

    result = set()
    default = [False for _ in range(count)]
    search(default, mines)
    # with open('output.log', 'a') as f:
    #     f.write(str(result))
    return result


class Solver():

    def __init__(self, mode="B", width=8, height=8, mines=99) -> None:

        self.mark_list = []
        self.clean_list = []
        if mode == "B":
            self.width = 8
            self.height = 8
        if mode == "E":
            self.width = 30
            self.height = 16
        elif mode == "I":
            self.width = 16
            self.height = 16
        elif mode == "C":
            self.width = width
            self.height = height
        self.width_pixel = self.width * 20
        self.height_pixel = self.height * 20
        self.board = np.ndarray((self.height, self.width), dtype=object)
        self.groups = []
        self.subgroups = []
        if mode == "E":
            self.MINES = 99
        elif mode == "I":
            self.MINES = 40
        elif mode == "B":
            self.MINES = 10
        elif mode == "C":
            self.MINES = mines
        self.remaining = 0
        self.isDead = False
        self.isComplete = False
        self.mode = mode
        self.covered_list = set()
        self.finished_clusters = []
        self.corners = set()

    def defineBoard(self):
        origin = pyautogui.locateOnScreen("covered.png", confidence=0.97)
        self.origin = origin
        return origin

    def detectNumber(self, RGB):
        if RGB[2] > 200 and RGB[0] < 100 and RGB[1] < 100:
            return 1
        elif RGB[1] > 120 and RGB[1] < 140 and RGB[0] < 50 and RGB[2] < 50:
            return 2
        elif RGB[0] > 220 and RGB[1] < 50 and RGB[2] < 50:
            return 3
        elif RGB[2] > 120 and RGB[2] < 140 and RGB[1] < 50 and RGB[0] < 50:
            return 4
        elif RGB[0] > 120 and RGB[0] < 140 and RGB[1] < 50 and RGB[2] < 50:
            return 5
        elif RGB[1] > 120 and RGB[1] < 140 and RGB[2] > 120 and RGB[2] < 140 and RGB[0] < 50:
            return 6
        elif RGB[0] < 10 and RGB[1] < 10 and RGB[2] < 10:
            return 7
        elif RGB[0] > 120 and RGB[0] < 140 and RGB[1] > 120 and RGB[1] < 140 and RGB[2] > 120 and RGB[2] < 140:
            return 8
        elif RGB[0] == RGB[1] == RGB[2] == 192:
            return 0
        elif RGB[0] > 200 and RGB[1] > 200 and RGB[2] > 200:
            return "white"

    def generateCoveredList(self):
        self.covered_list = set(
            [col for row in self.board for col in row if col.state == None])

    # @timing
    def fastReadBoard(self, origin):

        pyautogui.moveTo(0, 100)

        remaining = self.MINES
        img_np = np.array(ImageGrab.grab(bbox=(
            origin[0], origin[1], origin[0]+self.width_pixel, origin[1]+self.height_pixel)))

        for row in range(0, self.height_pixel, 20):

            for col in range(0, self.width_pixel, 20):
                pixel = img_np[row+5][col+9]
                pixel2 = img_np[row+14][col+9]
                pixel_topleft = img_np[row][col]
                dead_checker1 = self.detectNumber(img_np[row+2][col+18])
                dead_checker2 = self.detectNumber(img_np[row+9][col+13])
                num = self.detectNumber(pixel)
                checker = self.detectNumber(pixel2)
                checker_topleft = self.detectNumber(pixel_topleft)
                state = num
                if num == 3 and checker == 7:
                    num = "\033[91m" + "X" + "\x1b[0m"  # flaged
                    state = "Flaged"
                    remaining -= 1
                elif num == 0 and checker_topleft == "white":
                    num = "\033[1m" + "#" + "\x1b[0m"  # covered
                    state = None
                    # self.board[0][0], self.board[0][self.width - 1],
                    #    self.board[self.height - 1][0], self.board[self.height - 1][self.width - 1]

                    # if it is a corner
                    if any([all([row == 0, col == 0]), all([row == 0, col == self.width_pixel-20]), all([row == self.height_pixel-20, col == 0]), all([row == self.height_pixel-20, col == self.width_pixel - 20])]):
                        c = tile.Tile(
                            state, (origin[0] + col, origin[1] + row))
                        self.corners.add(c)
                elif num == 0 and checker_topleft == 8:
                    num = 0
                    state = 0
                elif dead_checker1 == 3 and dead_checker2 == 7:
                    os.system('cls')
                    print("Game is dead")
                    self.isDead = True
                    return
                t = tile.Tile(state, (origin[0] + col, origin[1] + row), flaged=True) if state == "Flaged" else tile.Tile(
                    state, (origin[0] + col, origin[1] + row))
                r, c = floor(row/20), floor(col/20)
                self.board[r][c] = t
                print(num, end=" ") if num else print(" ", end=" ")
            print("")

        self.generateCoveredList()

        self.remaining = remaining

    def cleanNeighbor(self, row, index):
        for i in range(-1, 2, 1):
            if (row+i) < 0 or (row+i) > self.height - 1:
                continue
            for j in range(-1, 2, 1):
                if (index+j) < 0 or (index+j) > self.width - 1:
                    continue
                if self.board[row+i][index+j].state == None and not self.board[row+i][index+j].isMarked() and not self.board[row+i][index+j].isCleaned():
                    self.board[row+i][index+j].clean()
                    # print("cleaned mine at", row+i, index+j)
                    self.clean_list.append(self.board[row+i][index+j])

    def checkNeighbor(self, row, index) -> tuple:
        covered_count = 0
        flag_count = 0
        for i in range(-1, 2, 1):
            if (row+i) < 0 or (row+i) > self.height - 1:
                continue
            for j in range(-1, 2, 1):
                if (index+j) < 0 or (index+j) > self.width - 1:
                    continue
                elif row+i == row and index+j == index:
                    continue
                if self.board[row+i][index+j].state == None:
                    covered_count += 1
                elif self.board[row+i][index+j].isFlaged():
                    flag_count += 1

        return covered_count, flag_count

    def markNeighbor(self, row, index):
        for i in range(-1, 2, 1):
            if (row+i) < 0 or (row+i) > self.height - 1:
                continue
            for j in range(-1, 2, 1):
                if (index+j) < 0 or (index+j) > self.width - 1:
                    continue
                if self.board[row+i][index+j].state == None and not self.board[row+i][index+j].isMarked():
                    self.board[row+i][index+j].mark()
                    # print("marked mine at", row+i, index+j)
                    self.mark_list.append(self.board[row+i][index+j])

    def findNeighbors(self, row, index):
        neighbors = []
        for i in range(-1, 2, 1):
            if (row+i) < 0 or (row+i) > self.height - 1:
                continue
            for j in range(-1, 2, 1):
                if (index+j) < 0 or (index+j) > self.width - 1:
                    continue
                neighbors.append(self.board[row+i][index+j])

        return neighbors

    def generateGroup(self, rindex, index, t):
        active_mines = t.state
        covered_neighbors = []
        if t.state:
            neighbors = self.findNeighbors(rindex, index)
            for neighbor in neighbors:
                if neighbor.isCovered() and not neighbor.isMarked() and not neighbor.isCleaned():
                    covered_neighbors.append(neighbor)
                elif neighbor.isFlaged() or neighbor.isMarked():
                    active_mines -= 1
        if active_mines:  # exclude ones with no mines around
            self.groups.append(Group(covered_neighbors, active_mines))

    def generateSubGroup_AL(self):  # "at least" subgroup
        for group in self.groups:

            if len(group.cells) > 7:
                continue

            if len(group.cells) > 2 and group.mines > 1 and group.type in ("exactly", "at least"):

                for cell in group.cells:
                    new = Group(group.diff(cell),
                                group.mines - 1, "at least")
                    self.subgroups.append(new)

    def generateSubGroup_NMT(self):  # "no more than" subgroup
        for group in self.groups:

            if len(group.cells) > 7:
                continue

            if len(group.cells) > 2 and group.mines > 0 and group.type in ("exactly", "no more than"):

                for cell in group.cells:
                    new = Group(group.diff(cell),
                                group.mines, "no more than")
                    self.subgroups.append(new)

    def deduce_safes(self, group_a, group_b):
        if group_a.cells.issubset(group_b.cells):
            if group_a.mines == group_b.mines:
                return list(group_b.cells - group_a.cells)

    def deduce_mines(self, group_a, group_b):
        if group_a.cells.issubset(group_b.cells):
            if (len(group_b.cells) - len(group_a.cells)) == (group_b.mines - group_a.mines):
                return list(group_b.cells - group_a.cells)

    def doTrivial(self, rindex, index, t):
        covered_count, flag_count = self.checkNeighbor(rindex, index)
        # print("covered count at ", rindex, index, covered_count)
        # print("t.state at", rindex, index, t.state)
        if covered_count == t.state - flag_count and not flag_count == t.state:
            self.markNeighbor(rindex, index)
        elif flag_count == t.state:
            self.cleanNeighbor(rindex, index)

    # @timing
    def doGroup(self):
        for group_a in self.groups:
            for group_b in self.groups:
                if group_a == group_b:
                    continue

                safes, mines = self.deduce_safes(
                    group_a, group_b), self.deduce_mines(group_a, group_b)
                if safes:
                    for safe in safes:
                        self.clean_list.append(safe)
                if mines:
                    for mine in mines:
                        self.mark_list.append(mine)

                if group_a.cells.issubset(group_b.cells) and group_b.mines - group_a.mines > 0:
                    # for cell in group_a.cells:
                    #     logging.info(
                    #         f'Cells positions of group a cells: {cell.position}')
                    # for cell in group_b.cells:
                    #     logging.info(
                    #         f'Cells positions of group b cells: {cell.position}')
                    new = Group(group_b.cells - group_a.cells,
                                group_b.mines - group_a.mines)
                    if new not in self.groups:

                        self.groups.append(new)

    # @timing
    def doSubGroup(self):

        self.generateSubGroup_AL()
        self.generateSubGroup_NMT()

        for group_a in self.subgroups:

            for group_b in self.groups:

                if group_a.type == "at least":

                    safes = self.deduce_safes(group_a, group_b)
                    if safes:
                        for safe in safes:
                            self.clean_list.append(safe)

                if group_a.type == "no more than":

                    mines = self.deduce_mines(group_a, group_b)
                    if mines:
                        for mine in mines:
                            self.mark_list.append(mine)

    # @timing
    def doDeduceRemain(self):
        unique = set()
        mineCount = 0
        for group in self.groups:
            added = False
            for cell in group.cells:
                if cell not in unique:
                    added = True
                    unique.add(cell)
            if added:
                mineCount += group.mines

        if mineCount == self.remaining:
            os.system('cls')
            logging.debug('Deduce remain is triggered.')
            # sys.exit()
            safes = list(self.covered_list - unique)
            for safe in safes:
                self.clean_list.append(safe)

    # @dump
    def init_cluster_CSP(self):

        try:
            first_group_cells = list(self.groups[0].cells)
            first_constraint = self.groups[0].mines
        except IndexError:  # no group
            self.clusters = []
            return
        # Set cluster with a default of first group
        first = Cluster(first_group_cells, first_constraint)
        first.add_group(self.groups[0])
        clusters = [first]
        for group in self.groups:

            if group == self.groups[0]:
                continue

            for cluster in clusters:
                if cluster.contains_all(group.cells):
                    break
            else:
                for cell in group.cells:
                    added = False
                    for cluster in clusters:

                        if cluster.contains(cell):
                            added = True
                            cells = list(group.cells)
                            cluster.add(cells)
                            break
                    if added:
                        cluster.add_constraint(group.mines)
                        cluster.add_group(group)
                        break
                else:  # means this is an alone group
                    new = Cluster(list(group.cells), group.mines)
                    new.add_group(group)
                    clusters.append(new)

        self.clusters = clusters

        remove_list = []
        for cluster in self.clusters:
            if cluster in self.finished_clusters:
                remove_list.append(cluster)
                continue
            for cell in cluster.get_cells():
                added = False
                for other in self.clusters:
                    if other is cluster:
                        continue
                    if other.contains(cell) and other.constraint >= cluster.constraint:
                        added = True
                        remove_list.append(cluster)
                        break
                if added:
                    other.add(cluster.get_cells())
                    other.add_constraint(cluster.constraint)
                    other.add_groups(cluster.groups)
                    break

        for item in remove_list:
            self.clusters.remove(item)

        # with open('output.log', 'a') as file:
        #     for cluster in self.clusters:
        #         file.write(f'{cluster=}\n')
        #         file.write(f'{len(cluster.get_cells())=}\n')
        #         file.write(f'{cluster.constraint=}\n')
        #         for cell in cluster.get_cells():
        #             file.write(f'{cell.position}\n')
    # @dump
    def search_cluster_CSP(self):

        def search(current_comb: list, position):

            # When it's already a valid solution
            for group in chosen_cluster.groups:
                count = 0
                for cell in group.cells:
                    if current_comb[cells_pos[cell]]:
                        count += 1

                if count != group.mines:
                    break
            else:
                if current_comb.count(True) <= self.remaining and current_comb.count(True) != 0:
                    result.add(tuple(current_comb))
                    return

            if position == len(current_comb):
                # result.add(tuple(current_comb))
                return

            for pos, item in enumerate(current_comb):
                if not item:
                    curr_comb = current_comb.copy()
                    curr_comb[pos] = True
                    for group in chosen_cluster.groups:

                        for cell in group.cells:
                            if cells_pos[cell] <= pos:
                                break
                        else:
                            continue

                        count = 0
                        for cell in group.cells:
                            if curr_comb[cells_pos[cell]]:
                                count += 1

                        if count > group.mines:
                            break
                    else:
                        search(curr_comb, pos+1)

        chosen_cluster = min(self.clusters, key=attrgetter('weight'))
        if len(chosen_cluster.get_cells()) > 12:
            return None

        cells_pos = {cell: pos for pos, cell in enumerate(
            chosen_cluster.get_cells())}

        result = set()
        default = [False for _ in range(len(chosen_cluster.get_cells()))]
        search(default, 0)
        self.cluster_solutions = list(result)
        return chosen_cluster
        # self.cluster = clusters

    # Not sure yet
    # @dump
    def do_cluster_CSP(self):

        self.init_cluster_CSP()
        if not self.clusters:
            return

        chosen_cluster = self.search_cluster_CSP()
        if chosen_cluster == None:
            return

        # with open('output.log', 'a') as file:
        #     file.write(f'{len(chosen_cluster.get_cells())=}\n')
        #     file.write(f'{self.cluster_solutions=}\n')

        has_solution = False
        for pos, cell in enumerate(chosen_cluster.get_cells()):

            mines_in_solution = 0
            for sol in self.cluster_solutions:
                if sol[pos]:
                    mines_in_solution += 1

            if mines_in_solution == 0:
                # with open('output.log', 'a') as file:
                #     col = (cell.position[0]-self.origin[0]) // 20 + 1
                #     row = (cell.position[1]-self.origin[1]) // 20 + 1
                #     file.write(
                #         f'[CLUSTER] Appended {(col, row)} to clean list.\n')
                self.clean_list.append(cell)
                has_solution = True
            elif mines_in_solution == len(self.cluster_solutions):
                # with open('output.log', 'a') as file:
                #     col = (cell.position[0]-self.origin[0]) // 20 + 1
                #     row = (cell.position[1]-self.origin[1]) // 20 + 1
                #     file.write(
                #         f'[CLUSTER] Appended {(col, row)} to mark list.\n')
                self.mark_list.append(cell)
                has_solution = True
            else:
                cell.set_probability(mines_in_solution /
                                     len(self.cluster_solutions))

        if not has_solution:
            self.finished_clusters.append(chosen_cluster)
            # with open('output.log', 'a') as file:
            #     file.write('Finished clusters: \n\n')
            #     for cluster in self.finished_clusters:
            #         file.write(f'{cluster=}\n')
            #         total = 0
            #         for cell in cluster.get_cells():
            #             col = (cell.position[0]-self.origin[0]) // 20 + 1
            #             row = (cell.position[1]-self.origin[1]) // 20 + 1
            #             file.write(
            #                 f'{(col, row)} has probability: {cell.probability}\n')
            #             total += cell.probability
            #         file.write(
            #             f'This finished cluster has a average of {total} mines.\n')

    def generate_bruteforce(self):

        cells_pos = {cell: pos for pos, cell in enumerate(self.covered_list)}

        permutations = generate_all_posistion(
            len(self.covered_list), self.remaining)

        filtered = []
        for permutation in permutations:
            for group in self.groups:
                count = 0
                for cell in group.cells:
                    if permutation[cells_pos[cell]]:
                        count += 1

                if count != group.mines:
                    break

            else:
                filtered.append(permutation)

        self.bruteforce_solutions = filtered

    # @dump
    def do_bruteforce(self):

        if len(self.covered_list) > 25 or math.comb(len(self.covered_list), self.remaining) > 3060:
            return

        self.generate_bruteforce()

        for pos, cell in enumerate(self.covered_list):

            mines_in_solution = 0
            for sol in self.bruteforce_solutions:
                if sol[pos]:
                    mines_in_solution += 1

            if mines_in_solution == 0:
                # with open('output.log', 'a') as file:
                #     file.write(
                #         f'[BRUTEFORCE] Appended {cell.position} to clean list.\n')
                self.clean_list.append(cell)
                for cluster in self.finished_clusters:
                    if cell in cluster.get_cells():
                        self.finished_clusters.remove(cluster)
                        break
            elif mines_in_solution == len(self.bruteforce_solutions):
                # with open('output.log', 'a') as file:
                #     file.write(
                #         f'[BRUTEFORCE] Appended {cell.position} to mark list.\n')
                self.mark_list.append(cell)
                for cluster in self.finished_clusters:
                    if cell in cluster.get_cells():
                        self.finished_clusters.remove(cluster)
                        break

    # @dump
    def do_probability(self):

        def choose_from_cluster():
            choice = min(cells, key=attrgetter('probability'))
            self.clean_list.append(choice)
            # with open('output.log', 'a') as file:
            #     col = (choice.position[0]-self.origin[0]) // 20 + 1
            #     row = (choice.position[1]-self.origin[1]) // 20 + 1
            #     file.write(
            #         f'{(col, row)} has been chosen with prob of {choice.probability}\n')
            #     file.write(f'wasteland length: {len(wasteland)}\n')
            for cluster in self.finished_clusters:
                if choice in cluster.get_cells():
                    self.finished_clusters.remove(cluster)
                    break

        def guess():
            if self.corners:
                self.select_corner()
                return

            choice = wasteland.pop()
            # with open('output.log', 'a') as file:
            #     col = (choice.position[0]-self.origin[0]) // 20 + 1
            #     row = (choice.position[1]-self.origin[1]) // 20 + 1
            #     file.write(
            #         f'[GUESS] {(col, row)} has been chosen with prob of {prob_wasteland}\n')
            #     file.write(f'wasteland length: {len(wasteland)}\n')
            self.clean_list.append(choice)

        wasteland = self.covered_list.copy()  # covered list but minus cluster cells
        for cluster in self.clusters:
            for cell in cluster.get_cells():
                try:
                    wasteland.remove(cell)
                except KeyError:
                    continue

        try:
            remaining = self.remaining
            cells = []
            for cluster in self.finished_clusters:
                approx_mines = cluster.approximate_mines()
                remaining -= approx_mines
                for cell in cluster.get_cells():
                    cells.append(cell)

            cells = np.array(cells)
            prob_wasteland = remaining / len(wasteland)
            if all(cell.probability > prob_wasteland for cell in cells):
                guess()
            else:
                choose_from_cluster()
        except ZeroDivisionError:
            choose_from_cluster()

    def do_random_move(self):
        if self.covered_list:
            choice = random.choice(list(self.covered_list))
            self.clean_list.append(choice)
            # with open('output.log', 'a') as file:
            #     col = (choice.position[0]-self.origin[0]) // 20 + 1
            #     row = (choice.position[1]-self.origin[1]) // 20 + 1
            #     file.write(
            #         f'[RANDOM] {(col, row)} has been click, {len(self.covered_list)=}\n')
        else:
            # os.system('cls')
            print("[RANDOM] Game is completed!")
            self.isComplete = True
            return

    @timing
    def analyze(self):

        # try:
        for rindex, row in enumerate(self.board):
            for index, t in enumerate(row):
                if t.state == 0 or t.state == None or t.isFlaged():
                    continue
                self.doTrivial(rindex, index, t)

        for rindex, row in enumerate(self.board):
            for index, t in enumerate(row):
                if t.state == 0 or t.state == None or t.isFlaged():
                    continue
                self.generateGroup(rindex, index, t)

        self.doGroup()
        self.doSubGroup()

        if not self.clean_list and not self.mark_list and len(self.covered_list) < self.width * self.height:
            self.do_cluster_CSP()
        if not self.clean_list and not self.mark_list and len(self.covered_list) < self.width * self.height:
            self.do_bruteforce()
        if not self.clean_list and not self.mark_list and len(self.covered_list) < self.width * self.height and self.finished_clusters:
            self.do_probability()
        if not self.clean_list and not self.mark_list:
            self.do_random_move()
        #     self.doDeduceRemain()
        # except Exception as e:
        #     print("Something went wrong: ")
        #     sys.exit()

    def select_corner(self):
        random_tile = self.corners.pop()
        self.clean_list.append(random_tile)
        # with open('output.log', 'a') as file:
        #     file.write('corner has been clicked\n')

    def click(self):

        mark_list = set(self.mark_list)
        clean_list = set(self.clean_list)
        print("\033[92mMines remaining: " + str(self.remaining) + "\x1b[0m")
        logging.info(f"Corners remaining: {len(self.corners)}    ")
        logging.info(f'Covered remaining: {len(self.covered_list)}    ')
        logging.info(f'Groups remaining: {len(self.groups)}    ')

        if not len(mark_list) == 0 or not len(clean_list) == 0:

            if len(mark_list) == len(self.covered_list) or self.remaining == len(self.covered_list):
                os.system('cls')
                print("Game is completed")
                self.isComplete = True
                return

            for m in mark_list:
                if m == None:
                    continue
                x, y = m.position[0], m.position[1]
                pyautogui.click(x, y, button="right")

            for c in clean_list:
                if c == None:
                    continue
                x, y = c.position[0], c.position[1]
                pyautogui.click(x, y, button="left")

            self.mark_list.clear()
            self.clean_list.clear()
            self.groups.clear()
            self.subgroups.clear()
        else:
            if self.remaining == len(self.covered_list):
                os.system('cls')
                print("Game is completed")
                self.isComplete = True
                return

    def make_first_move(self):
        self.fastReadBoard(self.origin)
        self.select_corner()

    def restart(self):
        pyautogui.press("enter")
        pyautogui.press("esc")
        if self.mode == "B":
            key = "1"
        elif self.mode == "I":
            key = "2"
        else:
            key = "3"
        pyautogui.press(key)


@timing
def solve(mode, width=None, height=None, mines=None):
    solver = Solver(mode=mode, width=width, height=height, mines=mines)
    os.system('cls')
    origin = solver.defineBoard()
    solver.make_first_move()
    while 1:
        try:
            print('\x1b[H')
            solver.fastReadBoard(origin)
            if solver.isDead or solver.isComplete:
                sys.exit()
            solver.analyze()
            solver.click()
        except pyautogui.FailSafeException:
            os.system('cls')
            print('Game is stopped.')
            sys.exit()


def testsolve(mode):
    solver = Solver(mode=mode)
    origin = solver.defineBoard()
    os.system('cls')

    print('\x1b[H')
    solver.fastReadBoard(origin)
    if solver.isDead or solver.isComplete:
        sys.exit()
    solver.analyze()
    solver.click()


@timing
def solveNTimes(mode, N):

    def print_result():
        print(f"Played {N} times.")
        print(f"Completed {complete_count} times.")
        print(f"Failed {dead_count} times.")
        print(f"Success rate: {(complete_count/N*100)}%")

    dead_count = 0
    complete_count = 0
    error_count = 0
    for i in range(N):

        solver = Solver(mode=mode)
        origin = solver.defineBoard()
        solver.make_first_move()
        os.system('cls')
        while 1:
            try:
                print('\x1b[H', end="")
                print(f"Solving game {i+1}/{N}.")
                print(f"Wins: {complete_count}")
                print(f"Loses: {dead_count}")
                print(f"Errors: {error_count}")
                solver.fastReadBoard(origin)
                if solver.isDead:
                    dead_count += 1
                    break
                elif solver.isComplete:
                    complete_count += 1
                    break
                elif keyboard.is_pressed('esc'):
                    os.system('cls')
                    print('Game is stopped.')
                    print_result()
                    sys.exit()
                solver.analyze()
                solver.click()
            except pyautogui.FailSafeException:
                os.system('cls')
                print('Game is stopped.')
                print_result()
                sys.exit()
            except TypeError:
                error_count += 1
                break
        solver.restart()
        time.sleep(0.05)

    print_result()


def main():
    open('output.log', 'w').close()

    level = logging.DEBUG
    fmt = '[%(levelname)s] %(message)s'
    logging.basicConfig(level=level, format=fmt)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--mode", help="mode of minesweeper game (B: beginner, I: Intermediate, E: Expert).", type=str, default="E", required=False)
    parser.add_argument(
        "-t", "--times", help="how many times to solve", type=int, required=False)
    args = parser.parse_args()

    if args.times:
        solveNTimes(args.mode, args.times)
    else:
        solve(args.mode)


if __name__ == "__main__":

    main()
