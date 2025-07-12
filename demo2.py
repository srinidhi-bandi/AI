import streamlit as st
import numpy as np
import pandas as pd

import heapq

def get_neighbors(pos, grid):
    i, j = pos
    neighbors = []
    for x, y in [(-1,0), (1,0), (0,-1), (0,1)]:
        ni, nj = i + x, j + y
        if 0 <= ni < grid.shape[0] and 0 <= nj < grid.shape[1]:
            if grid[ni][nj] != -1:
                neighbors.append((ni, nj))
    return neighbors

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def ucs(grid, start, goal):
    visited = set()
    pq = [(0, start)]
    came_from = {}

    while pq:
        cost, current = heapq.heappop(pq)
        if current == goal:
            return reconstruct_path(came_from, current)
        if current in visited:
            continue
        visited.add(current)

        for neighbor in get_neighbors(current, grid):
            ni, nj = neighbor
            if grid[ni][nj] == 5:  # "slow terrain"
                move_cost = 5
            else:
                move_cost = 1

    if neighbor not in visited:
        heapq.heappush(pq, (cost + move_cost, neighbor))
        if neighbor not in came_from:
            came_from[neighbor] = current

    return []

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid, start, goal):
    open_set = [(heuristic(start, goal), 0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, cost, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, grid):
            ni, nj = neighbor
            move_cost = 5 if grid[ni][nj] == 5 else 1
            tentative_g = g_score[current] + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f, tentative_g, neighbor))
    return []


st.set_page_config(page_title="Pathfinding Grid", layout="wide")
st.title("🤖 Pathfinding Robot Simulator - Grid Setup")

# Get user input for rows and columns
num_rows = st.number_input("Enter number of rows", min_value=5, max_value=30, value=10, step=1)
num_cols = st.number_input("Enter number of columns", min_value=5, max_value=30, value=10, step=1)

# Initialize session state
grid_shape_changed = False
if "grid_shape" not in st.session_state or st.session_state.grid_shape != (num_rows, num_cols):
    st.session_state.grid = np.zeros((num_rows, num_cols), dtype=int)
    st.session_state.grid_shape = (num_rows, num_cols)
    st.session_state.start_set = False
    st.session_state.goal_set = False
    grid_shape_changed = True

if "mode" not in st.session_state:
    st.session_state.mode = "Start"

# Color mapping: 0-free, 1-start, 2-goal, -1-obstacle
def cell_color(val):
    if val == 1:
        return "background-color: orange"  # Start
    elif val == 2:
        return "background-color: darkgreen"   # Goal
    elif val == -1:
        return "background-color: black"      # Obstacle
    elif val == 3:
        return "background-color: violet"  # Path taken
    else:
        return "background-color: aqua"       # Free space


# Select mode
st.markdown("### 🖱️ Select what you want to place:")
mode = st.radio("", ["Start", "Goal", "Obstacle", "Erase"], horizontal=True)
st.session_state.mode = mode

# Instructions
st.markdown("""
**Instructions**:
- Click on a cell to place the selected item (Start / Goal / Obstacle).
- Only one Start and one Goal can be placed.
- Obstacles can be placed/removed freely.
""")

# Click event handler
def click_cell(i, j):
    grid = st.session_state.grid
    mode = st.session_state.mode

    if mode == "Start":
        if not st.session_state.start_set:
            grid[i][j] = 1
            st.session_state.start_set = True
    elif mode == "Goal":
        if not st.session_state.goal_set:
            grid[i][j] = 2
            st.session_state.goal_set = True
    elif mode == "Obstacle":
        if grid[i][j] == 0:
            grid[i][j] = -1
    elif mode == "Erase":
        if grid[i][j] == 1:
            st.session_state.start_set = False
        elif grid[i][j] == 2:
            st.session_state.goal_set = False
        grid[i][j] = 0

# Display grid with interactive buttons
for i in range(num_rows):
    cols = st.columns(num_cols)
    for j in range(num_cols):
        label = ""
        val = st.session_state.grid[i][j]
        if val == 1:
            label = "S"
        elif val == 2:
            label = "G"
        elif val == -1:
            label = "O"
        cols[j].button(label, key=f"{i}-{j}", on_click=click_cell, args=(i, j))

# Show styled dataframe
styled_df = pd.DataFrame(st.session_state.grid)
st.dataframe(styled_df.style.applymap(cell_color), use_container_width=True)

# 🧠 Detect Start and Goal
grid = st.session_state.grid
start_cells = np.argwhere(grid == 1)
goal_cells = np.argwhere(grid == 2)
start = tuple(start_cells[0]) if start_cells.size > 0 else None
goal = tuple(goal_cells[0]) if goal_cells.size > 0 else None

# 🧭 A* or UCS pathfinding result
if "path_algorithm" not in st.session_state:
    st.session_state.path_algorithm = None

# Button Row
st.markdown("---")
st.markdown("### 🚀 Choose an action")
st.markdown("<br>", unsafe_allow_html=True)

spacer, col1, col2, col3 = st.columns([1, 2, 2, 2], gap="large")

# A* Button
with col1:
    if st.button("A*", key="a_star_button"):
        if start and goal:
            path = a_star(grid.copy(), start, goal)
            for cell in path:
                if grid[cell] == 0:
                    grid[cell] = 3
            st.session_state.path_algorithm = "A*"
            st.rerun()
        else:
            st.warning("Please set both Start and Goal.")

# Reset Button
with col2:
    if st.button("Reset Grid", key="reset_button"):
        st.session_state.grid = np.zeros((num_rows, num_cols), dtype=int)
        st.session_state.start_set = False
        st.session_state.goal_set = False
        st.session_state.path_algorithm = None
        st.rerun()

# UCS Button
with col3:
    if st.button("UCS", key="ucs_button"):
        if start and goal:
            path = ucs(grid.copy(), start, goal)
            for cell in path:
                if grid[cell] == 0:
                    grid[cell] = 3
            st.session_state.path_algorithm = "UCS"
            st.rerun()
        else:
            st.warning("Please set both Start and Goal.")

# Show path info (optional)
if st.session_state.path_algorithm:
    st.markdown(f"### ✅ Path found using **{st.session_state.path_algorithm}** algorithm.")
