from itertools import combinations
import numpy as np
import cv2

          
class sudoku_solver:
    #getting image
    def __init__(self, name_image):
        self.name_image = name_image
    
    #turn highlighted cells into white
    def clear_image_and_turn_to_black(self):
        start_img = cv2.imread(self.name_image, 1)
        for i in range(start_img.shape[0]):
            for j in range(start_img.shape[1]):
                B, G, R = start_img[i][j]
                if (B, G, R) in [(243, 235, 226), (251, 222, 187), (234, 215, 195)]:
                    start_img[i][j] = np.array([255, 255, 255])
        self.grey_img = cv2.cvtColor(start_img, cv2.COLOR_BGR2GRAY)
    
    #crop the image
    def cut_image(self):
        cords_of_corners = []
        for i in ['images_to_detect\\left_top_corner.png', 'images_to_detect\\right_bot_corner.png']:
            img_to_check = cv2.imread(i, 0)
            h, w = img_to_check.shape
            img_copy = self.grey_img.copy()
            result = cv2.matchTemplate(img_copy, img_to_check, cv2.TM_CCOEFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            location = max_loc
            bottom_right = (location[0] + w, location[1] + h)
            cords_of_corners.append(bottom_right)
        x1, y1, x2, y2 = *cords_of_corners[0], *cords_of_corners[1]
        cutt_img = self.grey_img[y1 - 15:y2 - 3, x1 - 16:x2 - 3]
        self.cutt_img = cv2.resize(cutt_img, (513, 513))
    
    #create a field
    def get_field(self):
        nums = ['images_to_detect\\1.png', 'images_to_detect\\2.png', 'images_to_detect\\8.png',
                'images_to_detect\\4.png', 'images_to_detect\\5.png', 'images_to_detect\\6.png',
                'images_to_detect\\7.png', 'images_to_detect\\3.png', 'images_to_detect\\9.png',
                'images_to_detect\\0.png']
        
        self.field = []
        for i in range(0, self.cutt_img.shape[0] - 56, 57):
            line = []
            for j in range(0, self.cutt_img.shape[1] - 56, 57):
                square_of_image = self.cutt_img[i:i + 57, j:j + 57]
                for num in nums:
                    square_of_image_copy = square_of_image.copy()
                    img_to_check = cv2.imread(num, 0)
                    h, w = img_to_check.shape
                    result = cv2.matchTemplate(square_of_image_copy, img_to_check, cv2.TM_CCOEFF_NORMED)
                    loc = np.where(result >= 0.895)
                    if loc[0].size > 0:
                        if num == 'images_to_detect\\0.png':
                            line.append('*')
                        else:
                            line.append(num[-5])
                        break
            self.field.append(line)

    #find a square for coordinates
    def square(self, i, j):
        if 0 <= i <= 2 and 0 <= j <= 2:
            x = (0, 0)
            y = (2, 2)
        elif 0 <= i <= 2 and 3 <= j <= 5:
            x = (0, 3)
            y = (2, 5)
        elif 0 <= i <= 2 and 6 <= j <= 8:
            x = (0, 6)
            y = (2, 8)
        elif 3 <= i <= 5 and 0 <= j <= 2:
            x = (3, 0)
            y = (5, 2)
        elif 3 <= i <= 5 and 3 <= j <= 5:
            x = (3, 3)
            y = (5, 5)
        elif 3 <= i <= 5 and 6 <= j <= 8:
            x = (3, 6)
            y = (5, 8)
        elif 6 <= i <= 8 and 0 <= j <= 2:
            x = (6, 0)
            y = (8, 2)
        elif 6 <= i <= 8 and 3 <= j <= 5:
            x = (6, 3)
            y = (8, 5)
        elif 6 <= i <= 8 and 6 <= j <= 8:
            x = (6, 6)
            y = (8, 8)
            
        return x, y

    #find which numbers can be in the cell based on the numbers in the line, column and square
    def nums_for_cords(self, i, j):
        ans = []
        x, y = self.square(i, j)
        ans.extend([x for x in self.field[i] if x.isdigit()])
        ans.extend([self.field[x][j] for x in range(9) if self.field[x][j].isdigit()])
        ans.extend([self.field[a][b] for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if self.field[a][b].isdigit()])
        ans = set([str(i) for i in range(1, 10)]) - set(ans)
        return ans
    
    #remove possible numbers from the cell based on the line, column and square
    def check(self):
        #check_line
        for i in range(9):
            nums_in_line = {(i, j): self.nums_for_all_cell[(i, j)] for j in range(9) if not self.field[i][j].isdigit()}
            ready_nums_for_line = {self.field[i][j] for j in range(9) if self.field[i][j].isdigit()}
            for o in ready_nums_for_line:
                for p in nums_in_line:
                    if o in nums_in_line[p]:
                        self.nums_for_all_cell[p] = self.nums_for_all_cell[p] - set(o)
                    
        #check_column
        for i in range(9):
            nums_in_column = {(j, i): self.nums_for_all_cell[(j, i)] for j in range(9) if not self.field[j][i].isdigit()}
            ready_nums_for_column = {self.field[j][i] for j in range(9) if self.field[j][i].isdigit()}
            for o in ready_nums_for_column:
                for p in nums_in_column:
                    if o in nums_in_column[p]:
                        self.nums_for_all_cell[p] = self.nums_for_all_cell[p] - set(o)
        
        #check_square
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                x, y = self.square(i, j)
                nums_in_square = {(a, b): self.nums_for_all_cell[(a, b)] for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if not self.field[a][b].isdigit()}
                ready_nums_for_square = {self.field[a][b] for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if self.field[a][b].isdigit()}
                for o in ready_nums_for_square:
                    for p in nums_in_square:
                        if o in nums_in_square[p]:
                            self.nums_for_all_cell[p] = self.nums_for_all_cell[p] - set(o)  
    
    #find the "naked pairs" in squares and remove for each "naked pair" the remaining numbers in their cells  
    def find_naked_pairs_for_square(self):
        naked_pairs_for_square = {}
        cnt = 0
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                cnt += 1
                x, y = self.square(i, j)
                a = {(a, b): self.nums_for_all_cell[(a, b)] for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if not self.field[a][b].isdigit()}
                if a:
                    naked_pairs_for_square[cnt] = a
        for i in naked_pairs_for_square.values():
            all_nums_for_square = {y for t in i.values() for y in t}
            combs = list(combinations(''.join(sorted(all_nums_for_square)), 2))
            for x, y in combs:
                list_of_coords = [[(t, o), i[(t, o)], x, y] for t, o in i if x in i[(t, o)] and y in i[(t, o)]]
                if len([i[1] for i in list_of_coords]) == 2:
                    a, _, firtst_naked_pair, second_naked_pair = list_of_coords[0]
                    b = list_of_coords[1][0]
                    x, y = self.square(*a)
                    other_nums_of_square = {(t, p): self.nums_for_all_cell[(t, p)] for t in range(x[0], y[0] + 1) for p in range(x[1], y[1] + 1) if not self.field[t][p].isdigit() and (t, p) not in [a, b]}
                    other_nums_of_square = {j for i in other_nums_of_square.values() for j in i}
                    if firtst_naked_pair not in other_nums_of_square and second_naked_pair not in other_nums_of_square:
                        self.nums_for_all_cell[a] = {firtst_naked_pair, second_naked_pair}
                        self.nums_for_all_cell[b] = {firtst_naked_pair, second_naked_pair}
    
    #remove numbers from the squares based on 'naked pairs'             
    def delete_notes_from_squares(self):
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                x, y = self.square(i, j)
                nums = {(a, b): self.nums_for_all_cell[(a, b)] for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if not self.field[a][b].isdigit()}
                sl = {}
                for n in nums:
                    if len(nums[n]) == 2 and list(nums.values()).count(nums[n]) == 2:
                        sl[n] = nums[n]
                for g in nums:
                    for h in sl:
                        if g not in sl:
                            self.nums_for_all_cell[g] = nums[g] - (nums[g] & sl[h])
    
    #remove numbers from the columns based on 'naked pairs'                      
    def delete_notes_from_columns(self):
        for i in range(9):
            nums = {(a, i): self.nums_for_all_cell[(a, i)] for a in range(9) if not self.field[a][i].isdigit()}
            sl = {}
            for n in nums:
                if len(nums[n]) == 2 and list(nums.values()).count(nums[n]) == 2:
                    sl[n] = nums[n]
            for g in nums:
                for h in sl:
                    if g not in sl:
                        self.nums_for_all_cell[g] = nums[g] - (nums[g] & sl[h])
                    
    #remove numbers from the lines based on 'naked pairs'                   
    def delete_notes_from_lines(self):
        for i in range(9):
            nums = {(i, a): self.nums_for_all_cell[(i, a)] for a in range(9) if not self.field[i][a].isdigit()}
            sl = {}
            for n in nums:
                if len(nums[n]) == 2 and list(nums.values()).count(nums[n]) == 2:
                    sl[n] = nums[n]
            for g in nums:
                for h in sl:
                    if g not in sl:
                        self.nums_for_all_cell[g] = nums[g] - (nums[g] & sl[h])

    #find “indicating pairs” in the squares and remove possible numbers based on them
    def indicating_pairs_for_squares(self):
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                x, y = self.square(i, j)
                nums_for_square = {(a, b): self.nums_for_all_cell[(a, b)] for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if not self.field[a][b].isdigit()}
                for a in set([j for i in nums_for_square.values() for j in i]):
                    if [j for i in nums_for_square.values() for j in i].count(a) == 2:
                        sl = {v for v in nums_for_square if a in nums_for_square[v]}
                        first_cord, second_cord = sl
                        if first_cord[1] == second_cord[1]:
                            b = first_cord[1]
                            if a in {j for i in range(9) if not self.field[i][b].isdigit() and (i, b) not in [first_cord, second_cord] for j in self.nums_for_all_cell[(i, b)]}:
                                for v in range(9):
                                    if not self.field[v][b].isdigit():
                                        if a in self.nums_for_all_cell[(v, b)] and (v, b) not in [first_cord, second_cord]:
                                            self.nums_for_all_cell[(v, b)] = self.nums_for_all_cell[(v, b)] - {a}
                        elif first_cord[0] == second_cord[0]:
                            b = first_cord[0]
                            if a in {j for i in range(9) if not self.field[b][i].isdigit() and (b, i) not in [first_cord, second_cord] for j in self.nums_for_all_cell[(b, i)]}:
                                for v in range(9):
                                    if not self.field[b][v].isdigit():
                                        if a in self.nums_for_all_cell[(b, v)] and (b, v) not in [first_cord, second_cord]:
                                            self.nums_for_all_cell[(b, v)] = self.nums_for_all_cell[(b, v)] - {a}
    
    #find “indicating pairs” in the columns and remove possible numbers based on them                                       
    def indicating_pairs_for_columns(self):
        for i in range(9):
            nums_for_column = {(a, i): self.nums_for_all_cell[(a, i)] for a in range(9) if not self.field[a][i].isdigit()}
            for a in set([j for i in nums_for_column.values() for j in i]):
                if [j for i in nums_for_column.values() for j in i].count(a) == 2:
                    sl = {v for v in nums_for_column if a in nums_for_column[v]}
                    first_cord, second_cord = sl
                    if self.square(*first_cord) == self.square(*second_cord):
                        x, y = self.square(*first_cord)
                        if a in {j for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if not self.field[a][b].isdigit() and (a, b) not in [first_cord ,second_cord] for j in self.nums_for_all_cell[(a, b)]}:
                            for b in range(x[0], y[0] + 1):
                                for v in range(x[1], y[1] + 1):
                                    if not self.field[b][v].isdigit():
                                        if a in self.nums_for_all_cell[(b, v)] and (b, v) not in [first_cord, second_cord]:
                                            self.nums_for_all_cell[(b, v)] = self.nums_for_all_cell[(b, v)] - {a}
                                            
    #find “indicating pairs” in the lines and remove possible numbers based on them                                        
    def indicating_pairs_for_lines(self):
        for i in range(9):
            nums_for_line = {(i, a): self.nums_for_all_cell[(i, a)] for a in range(9) if not self.field[i][a].isdigit()}
            for a in set([j for i in nums_for_line.values() for j in i]):
                if [j for i in nums_for_line.values() for j in i].count(a) == 2:
                    sl = {v for v in nums_for_line if a in nums_for_line[v]}
                    first_cord, second_cord = sl
                    if self.square(*first_cord) == self.square(*second_cord):
                        x, y = self.square(*first_cord)
                        if a in {j for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if not self.field[a][b].isdigit() and (a, b) not in [first_cord ,second_cord] for j in self.nums_for_all_cell[(a, b)]}:
                            for b in range(x[0], y[0] + 1):
                                for v in range(x[1], y[1] + 1):
                                    if not self.field[b][v].isdigit():
                                        if a in self.nums_for_all_cell[(b, v)] and (b, v) not in [first_cord, second_cord]:
                                            self.nums_for_all_cell[(b, v)] = self.nums_for_all_cell[(b, v)] - {a}
                                            
    #find the most recent digit based on lines, columns and squares
    def last_numbers(self):
        for i in range(9):
            for j in range(9):
                if self.field[i][j] == '*':
                    ans = self.nums_for_all_cell[(i, j)]
                    if len(ans) == 1:
                        self.field[i][j] = str(*ans)
                        self.check()
                        del self.nums_for_all_cell[(i, j)]
    
    #find the only possible number in a squares based on other possible numbers in a given square
    def unique_for_square(self):
        for i in range(9):
            for j in range(9):
                if self.field[i][j] == '*':
                    x, y = self.square(i, j)
                    unique_for_square = {(a, b): self.nums_for_all_cell[(a, b)] for a in range(x[0], y[0] + 1) for b in range(x[1], y[1] + 1) if not self.field[a][b].isdigit() and (a, b) != (i, j)}
                    unique_for_square = {j for i in unique_for_square.values() for j in i}
                    if len(self.nums_for_all_cell[(i, j)] - unique_for_square) == 1:
                        self.field[i][j] = str(*(self.nums_for_all_cell[(i, j)] - unique_for_square))
                        self.check()
                        del self.nums_for_all_cell[(i, j)]

    #find the only possible number in a columns based on other possible numbers in a given square
    def unique_for_column(self):
        for i in range(9):
            for j in range(9):
                if self.field[i][j] == '*':
                    unique_for_column = {(t, j): self.nums_for_all_cell[(t, j)] for t in range(9) if not self.field[t][j].isdigit() and (t, j) != (i, j)}
                    unique_for_column = {j for i in unique_for_column.values() for j in i}
                    if len(self.nums_for_all_cell[(i, j)] - unique_for_column) == 1:
                        self.field[i][j] = str(*(self.nums_for_all_cell[(i, j)] - unique_for_column))
                        self.check()
                        del self.nums_for_all_cell[(i, j)]
    
    #find the only possible number in a lines based on other possible numbers in a given square  
    def unique_for_line(self):
        for i in range(9):
            for j in range(9):
                if self.field[i][j] == '*':
                    unique_for_line = {(i, t): self.nums_for_all_cell[(i, t)] for t in range(9) if not self.field[i][t].isdigit()}
                    unique_for_line = {j for i in unique_for_line.values() for j in i}
                    if len(self.nums_for_all_cell[(i, j)] - unique_for_line) == 1:
                        self.field[i][j] = str(*(self.nums_for_all_cell[(i, j)] - unique_for_line))
                        self.check()
                        del self.nums_for_all_cell[(i, j)]
    
    #check for solution
    def check_solution(self):
        if '*' not in ''.join([j for i in self.field for j in i]):
            print('found solution!')
            print()
            for i in self.field:
                print(' '.join(i))
            self.cycle = False
        elif self.nums_for_all_cell == self.nums_for_all_cell_copy:
            print('no solution')
            print()
            for i in self.field:
                print(' '.join(i))
            self.cycle = False        
    
    #the main function in which a field is constructed from the resulting image. next, solve Sudoku                  
    def sudoku_complete(self):
        self.clear_image_and_turn_to_black()
        self.cut_image()
        self.get_field()
        self.nums_for_all_cell = {(i, j): self.nums_for_cords(i, j) for i in range(9) for j in range(9) if not self.field[i][j].isdigit()}
        self.cycle = True
        while self.cycle:
            self.nums_for_all_cell_copy = {i: self.nums_for_all_cell[i] for i in self.nums_for_all_cell}        
            self.find_naked_pairs_for_square()
            self.delete_notes_from_squares()
            self.delete_notes_from_columns()
            self.delete_notes_from_lines()
            self.indicating_pairs_for_squares()
            self.indicating_pairs_for_columns()
            self.indicating_pairs_for_lines()
                        
            self.last_numbers()
            self.unique_for_square()
            self.unique_for_column()
            self.unique_for_line()        

            self.check_solution()
            


sudoku = sudoku_solver('test_image.png')
sudoku.sudoku_complete()