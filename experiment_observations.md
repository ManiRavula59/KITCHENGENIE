# AI Smart Kitchen Meal Planner - Experiment Observations

## 3. Flask-based Web Application

### Aim
To implement a web-based meal planning system using Flask framework that provides user interface for meal planning, dish management, and AI-powered meal generation with real-time interaction capabilities.

### Definition
Flask is a lightweight Python web framework that provides tools, libraries, and technologies to build web applications. It allows developers to create web services and APIs with minimal boilerplate code.

### Syntax
```python
from flask import Flask, render_template, request, jsonify, session
app = Flask(__name__)
app.secret_key = "your-secret-key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def api_endpoint():
    data = request.get_json()
    return jsonify({'result': data})
```

### Procedure
1. **Initialize Flask App**: Create Flask instance with secret key for user sessions
2. **Create Main Routes**: 
   - `/` route loads index.html with available dishes from Prolog
   - `/generate_meal_plan` route processes form data and calls AI algorithms
   - `/results` route displays generated meal plan with visualizations
3. **Handle User Input**: Process dish addition forms and preference updates
4. **Integrate AI Algorithms**: Call A* → AO* → Prolog fallback chain for meal planning
5. **Store Session Data**: Save meal plans and grocery lists in Flask sessions
6. **Render Templates**: Use Jinja2 to display dynamic data (dishes, meal plans, preferences)
7. **Handle AJAX Requests**: Process dish swapping and alternative suggestions without page reload

### Code Snippet
```python
# From app.py - Main Flask application setup
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

@app.route('/')
def index():
    """Main page with meal planner interface"""
    try:
        dishes = prolog.get_all_dishes()
        meal_types = ['breakfast', 'lunch', 'snacks', 'dinner']
        return render_template('index.html', 
                             dishes=dishes, 
                             meal_types=meal_types,
                             preferences=session.get('preferences', {}))
    except Exception as e:
        logger.error(f"Error loading index page: {e}")
        flash('Error loading meal planner. Please try again.', 'error')
        return render_template('index.html', dishes=[], meal_types=[], preferences={})

@app.route('/generate_meal_plan', methods=['POST'])
def generate_meal_plan():
    """Generate weekly meal plan using AI algorithms"""
    start_date = request.form.get('start_date')
    meal_plan = astar_planner.generate_meal_plan(start_date, session.get('preferences', {}), query_id)
    session['current_meal_plan'] = meal_plan
    return redirect(url_for('results'))
```

### Sample Input and Output
**Input**: User submits meal plan generation form with start date "2024-01-15"
**Output**: Redirects to results page showing generated weekly meal plan with breakfast, lunch, snacks, and dinner for each day

---

## 4. Prolog Concepts

### 4a. Queries

### Aim
To retrieve specific information from the Prolog knowledge base using structured queries that find dishes, ingredients, and meal planning data based on various criteria.

### Definition
A query in Prolog is a question asked to the knowledge base to find facts or combinations of facts that satisfy certain conditions. Queries use variables and predicates to search for matching data.

### Syntax
```prolog
?- predicate_name(argument1, argument2, Result).
?- findall(Variable, condition(Variable), List).
?- member(Element, List).
```

### Procedure
1. **Query Dish Data**: Use `get_dishes_by_meal_type(MealType, Dishes)` to find all breakfast/lunch/dinner/snacks dishes
2. **Filter Vegetarian**: Use `get_vegetarian_dishes(VegDishes)` to find only vegetarian options
3. **Get Ingredients**: Use `get_dish_ingredients(Dish, Ingredients)` to retrieve ingredient lists
4. **Analyze Statistics**: Use `analyze_meal_distribution(MealType, Count, AvgPrepTime)` for meal type analysis
5. **Execute in Python**: Call these queries through `prolog_interface.py` to get data for web display

### Code Snippet
```prolog
% From kb.pl - Query examples
% Query 1: Get all dishes of a specific meal type
get_dishes_by_meal_type(MealType, Dishes) :-
    findall(Dish, dish(Dish, MealType, _, _, _, _, _), Dishes).

% Query 2: Get ingredients for a specific dish
get_dish_ingredients(Dish, Ingredients) :-
    dish(Dish, _, Ingredients, _, _, _, _).

% Query 3: Find vegetarian dishes only (Quantifiers with findall)
get_vegetarian_dishes(VegDishes) :-
    findall(Dish, dish(Dish, _, _, _, true, _, _), VegDishes).
```

### Sample Input and Output
**Input**: `?- get_dishes_by_meal_type(breakfast, Dishes).`
**Output**: `Dishes = [idli_sambar, dosa_chutney, upma, pongal, poori_potato_curry]`

---

### 4b. Unification

### Aim
To match patterns and bind variables by finding common structures between terms, enabling flexible data retrieval and pattern matching in meal planning constraints.

### Definition
Unification is the process of making two terms identical by finding substitutions for variables. It's the fundamental operation in Prolog that allows pattern matching and variable binding.

### Syntax
```prolog
unify_pattern([], []).
unify_pattern([H|T], [H|Rest]) :-
    unify_pattern(T, Rest).
unify_pattern([_|T], [_|Rest]) :-
    unify_pattern(T, Rest).
```

### Procedure
1. **Create Pattern Matching**: Use `match_dish_pattern(Pattern, Dish)` to find dishes matching specific criteria
2. **Define Unification Rules**: Implement `unify_pattern` to match dish characteristics (meal type, ingredients, etc.)
3. **Handle Empty Patterns**: Base case `unify_pattern([], [])` for empty pattern matching
4. **Recursive Matching**: Match head elements and recursively match tail elements
5. **Variable Binding**: Use `_` wildcards to match any dish attribute (meal type, cost, etc.)

### Code Snippet
```prolog
% From kb.pl - Unification for dish pattern matching
% Pattern matching for dish characteristics
match_dish_pattern(Pattern, Dish) :-
    dish(Dish, MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost),
    unify_pattern(Pattern, [MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost]).

unify_pattern([], []).
unify_pattern([H|T], [H|Rest]) :-
    unify_pattern(T, Rest).
unify_pattern([_|T], [_|Rest]) :-
    unify_pattern(T, Rest).
```

### Sample Input and Output
**Input**: `?- match_dish_pattern([breakfast, _, _, true, _, _], Dish).`
**Output**: `Dish = idli_sambar ; Dish = dosa_chutney ; Dish = upma ; ...`

---

### 4c. Visualization

### Aim
To create graphical representations of meal plans and algorithm performance using matplotlib to display weekly timetables, meal distributions, and AI algorithm metrics.

### Definition
Visualization is the graphical representation of data to make complex information more accessible and understandable through charts, graphs, and visual elements.

### Syntax
```python
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

fig, ax = plt.subplots(figsize=(14, 8))
ax.barh(y_pos, values, color=colors, alpha=0.7)
plt.savefig(buffer, format='png')
```

### Procedure
1. **Initialize Matplotlib**: Set non-interactive backend and import required modules
2. **Create Weekly Timetable**: Generate horizontal bar chart showing 7 days × 4 meal types
3. **Prepare Meal Data**: Extract dishes from meal_plan dictionary for each day and meal type
4. **Apply Color Coding**: Use different colors for breakfast (yellow), lunch (blue), snacks (cyan), dinner (gray)
5. **Add Dish Labels**: Display dish names on each bar with truncation for long names
6. **Generate Performance Charts**: Create algorithm comparison charts and quality metrics
7. **Convert to Base64**: Save PNG images to BytesIO buffer and encode for HTML display

### Code Snippet
```python
# From app.py - Visualization generation
def generate_visualizations(meal_plan, algorithm):
    """Generate matplotlib visualizations for the meal plan"""
    try:
        visualizations = {}
        
        # 1. Weekly Meal Timetable
        fig, ax = plt.subplots(figsize=(14, 8))
        days = list(meal_plan.keys())
        meal_types = ['breakfast', 'lunch', 'snacks', 'dinner']
        
        # Create a grid for the timetable
        y_pos = np.arange(len(days))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, meal_type in enumerate(meal_types):
            dishes = [meal_plan[day].get(meal_type, 'No dish') for day in days]
            ax.barh(y_pos, [1]*len(days), left=i, height=0.8, 
                   color=colors[i], alpha=0.7, label=meal_type.capitalize())
            
            # Add dish names
            for j, dish in enumerate(dishes):
                ax.text(i + 0.5, j, dish[:15] + ('...' if len(dish) > 15 else ''), 
                       ha='center', va='center', fontsize=8, fontweight='bold')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(days)
        ax.set_xlabel('Meal Types')
        ax.set_title(f'Weekly Meal Plan - {algorithm.upper()} Algorithm', fontsize=16, fontweight='bold')
        ax.legend(loc='upper right')
        ax.set_xlim(0, 4)
        
        # Save to base64
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        visualizations['timetable'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return visualizations
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")
        return {}
```

### Sample Input and Output
**Input**: Meal plan dictionary with 7 days and 4 meal types each
**Output**: Base64-encoded PNG image showing weekly meal timetable with colored bars for each meal type

---

### 4d. Recursion

### Aim
To process lists of dishes and ingredients recursively, collecting all ingredients from multiple dishes and removing duplicates to create comprehensive grocery lists.

### Definition
Recursion is a programming technique where a function calls itself to solve smaller instances of the same problem, continuing until a base case is reached.

### Syntax
```prolog
recursive_predicate([], []).
recursive_predicate([H|T], Result) :-
    process_element(H, ProcessedH),
    recursive_predicate(T, RestResult),
    combine(ProcessedH, RestResult, Result).
```

### Procedure
1. **Base Case**: `collect_ingredients([], [])` handles empty dish list
2. **Recursive Case**: Take first dish, get its ingredients, recurse on remaining dishes
3. **Combine Ingredients**: Use `append` to merge current dish ingredients with recursive result
4. **Remove Duplicates**: Apply `remove_duplicates` recursively to eliminate repeated ingredients
5. **Termination**: Each recursive call reduces the dish list until empty list is reached

### Code Snippet
```prolog
% From kb.pl - Recursive ingredient collection
% Recursive ingredient collection for multiple dishes
collect_ingredients([], []).
collect_ingredients([Dish|RestDishes], AllIngredients) :-
    get_dish_ingredients(Dish, DishIngredients),
    collect_ingredients(RestDishes, RestIngredients),
    append(DishIngredients, RestIngredients, TempIngredients),
    remove_duplicates(TempIngredients, AllIngredients).

% Recursive duplicate removal
remove_duplicates([], []).
remove_duplicates([H|T], Result) :-
    member(H, T), !,
    remove_duplicates(T, Result).
remove_duplicates([H|T], [H|Result]) :-
    remove_duplicates(T, Result).
```

### Recursion Tree Visualization
```
remove_duplicates([rice, salt, rice, oil], Result)
│
├─ remove_duplicates([rice, salt, rice, oil], Result)
│  │
│  ├─ H = rice, T = [salt, rice, oil]
│  │
│  ├─ member(rice, [salt, rice, oil]) ✓ (rice found in tail)
│  │
│  ├─ ! (cut operator - commit to this choice)
│  │
│  ├─ remove_duplicates([salt, rice, oil], Result)
│  │  │
│  │  ├─ H = salt, T = [rice, oil]
│  │  │
│  │  ├─ member(salt, [rice, oil]) ✗ (salt not found in tail)
│  │  │
│  │  ├─ remove_duplicates([rice, oil], RestResult)
│  │  │  │
│  │  │  ├─ H = rice, T = [oil]
│  │  │  │
│  │  │  ├─ member(rice, [oil]) ✗ (rice not found in tail)
│  │  │  │
│  │  │  ├─ remove_duplicates([oil], RestResult2)
│  │  │  │  │
│  │  │  │  ├─ H = oil, T = []
│  │  │  │  │
│  │  │  │  ├─ member(oil, []) ✗ (oil not found in empty list)
│  │  │  │  │
│  │  │  │  ├─ remove_duplicates([], [])
│  │  │  │  │  └─ Base Case: [] → []
│  │  │  │  │
│  │  │  │  └─ RestResult2 = [oil]
│  │  │  │
│  │  │  └─ RestResult = [rice, oil]
│  │  │
│  │  └─ Result = [salt, rice, oil]
│  │
│  └─ Final Result: [salt, rice, oil]
│
└─ Final Result: [salt, rice, oil]
```

### Recursion Explanation in Your Project
**Step-by-Step Implementation:**

1. **Base Case**: `remove_duplicates([], [])` - Empty list returns empty list
2. **Duplicate Check**: Check if head element exists in tail using `member(H, T)`
3. **Cut Operator**: Use `!` to commit to choice and prevent backtracking
4. **Two Paths**: 
   - If duplicate found: Skip head, recurse on tail only
   - If no duplicate: Keep head, recurse on tail and add head to result
5. **Recursive Processing**: `remove_duplicates(Tail, Result)` processes remaining elements
6. **Termination**: Each recursive call reduces the list until empty list is reached

**Real Example**: When removing duplicates from [rice, salt, rice, oil], the recursion tree shows: first rice is removed (duplicate), salt is kept, second rice is kept (no duplicate in remaining), oil is kept, resulting in [salt, rice, oil]. This is used in your project to create unique grocery lists.

### Sample Input and Output
**Input**: `?- remove_duplicates([rice, salt, rice, oil], Result).`
**Output**: `Result = [salt, rice, oil]`

---

### 4e. Backtracking

### Aim
To find alternative dishes when the current selection doesn't meet constraints, allowing the system to explore different possibilities and suggest suitable replacements.

### Definition
Backtracking is a systematic way to explore all possible solutions by trying different choices and undoing them if they don't lead to a solution, allowing Prolog to find alternative answers.

### Syntax
```prolog
backtracking_predicate(Input, Output) :-
    condition1(Input),
    condition2(Input),
    generate_alternative(Input, Output).

generate_alternative(Input, Alt) :-
    member(Alt, Alternatives),
    satisfies_constraints(Alt, Input).
```

### Procedure
1. **Find Alternative Dishes**: Use `suggest_alternative` to find dishes of same meal type
2. **Apply Constraints**: Check `suitable_dish` and `avoid_repetition` conditions
3. **Generate Multiple Options**: Use `findall` to collect all valid alternatives
4. **Filter Current Dish**: Exclude the currently selected dish from alternatives
5. **Return Alternatives**: Provide list of suitable replacement dishes for user selection

### Code Snippet
```prolog
% From kb.pl - Backtracking for alternative suggestions
% Find alternative dishes with backtracking
suggest_alternative(Day, MealType, CurrentDish, Alternative) :-
    dish(Alternative, MealType, _, _, _, _, _),
    Alternative \= CurrentDish,
    suitable_dish(Alternative, Day, MealType),
    \+ avoid_repetition(Alternative, Day).

% Generate multiple alternatives using backtracking
find_alternatives(Day, MealType, CurrentDish, Alternatives) :-
    findall(Alt, suggest_alternative(Day, MealType, CurrentDish, Alt), Alternatives).
```

### Backtracking Tree Visualization

A visually structured backtracking tree for `find_alternatives(monday, breakfast, idli_sambar, Alternatives)` is shown below. Each branch represents a candidate dish, and each level shows constraint checks. Success (✓) and failure (✗) are marked at each step. This diagram demonstrates how Prolog systematically explores and backtracks through alternatives:

```
find_alternatives(monday, breakfast, idli_sambar, Alternatives)
│
├── dosa_chutney
│   ├── is breakfast? ............ ✓
│   ├── ≠ idli_sambar? .......... ✓
│   ├── suitable? ............... ✓
│   └── not repeated? ........... ✓   → ACCEPT
│
├── upma
│   ├── is breakfast? ............ ✓
│   ├── ≠ idli_sambar? .......... ✓
│   ├── suitable? ............... ✗   → REJECT
│
├── chicken_biryani
│   └── is breakfast? ............ ✗   → REJECT
│
├── pongal
│   ├── is breakfast? ............ ✓
│   ├── ≠ idli_sambar? .......... ✓
│   ├── suitable? ............... ✓
│   └── not repeated? ........... ✓   → ACCEPT
│
├── poori_potato_curry
│   ├── is breakfast? ............ ✓
│   ├── ≠ idli_sambar? .......... ✓
│   ├── suitable? ............... ✓
│   └── not repeated? ........... ✓   → ACCEPT
│
├── idli_sambar
│   ├── is breakfast? ............ ✓
│   └── ≠ idli_sambar? .......... ✗   → REJECT
│
└── ... (other dishes)
```

**Explanation:**
- The system tries each dish as a possible alternative.
- For each, it checks: (1) meal type, (2) not the current dish, (3) suitability for the day, (4) not recently repeated.
- If all checks pass, the dish is accepted as an alternative; otherwise, Prolog backtracks and tries the next.
- This tree structure makes the backtracking process and constraint filtering visually clear.

### Backtracking Explanation in Your Project
**Step-by-Step Implementation:**

1. **Initial Query**: `find_alternatives(monday, breakfast, idli_sambar, Alternatives)` starts the search
2. **Dish Enumeration**: `findall` systematically tries each dish in the knowledge base
3. **Constraint Checking**: Each alternative must pass multiple conditions:
   - Must be a breakfast dish (`dish(Alternative, breakfast, ...)`)
   - Must be different from current dish (`Alternative \= CurrentDish`)
   - Must be suitable for the day (`suitable_dish(Alternative, Day, MealType)`)
   - Must not violate repetition rules (`\+ avoid_repetition(Alternative, Day)`)
4. **Backtracking Points**: When any condition fails, Prolog backtracks to try the next dish
5. **Solution Collection**: Successful alternatives are collected into the final list
6. **Result**: Returns all valid alternatives that meet all constraints

**Real Example**: When user clicks "Suggest Alternatives" for idli_sambar on Monday breakfast, the backtracking tree shows how Prolog systematically explores all breakfast dishes, rejecting those that don't meet constraints (wrong meal type, same dish, expensive preferences, etc.) and collecting valid alternatives.

### Sample Input and Output
**Input**: `?- find_alternatives(monday, breakfast, idli_sambar, Alternatives).`
**Output**: `Alternatives = [dosa_chutney, upma, pongal, poori_potato_curry]`

---

### 4f. List Operations

### Aim
To manipulate lists of dishes, ingredients, and meal plans using various list operations like grouping, filtering, and transforming data for meal planning analysis.

### Definition
List operations are functions that manipulate lists by transforming, filtering, grouping, or combining elements to extract meaningful information or reorganize data structures.

### Syntax
```prolog
% List operations
append(List1, List2, CombinedList).
member(Element, List).
length(List, Length).
findall(Template, Goal, List).
```

### Procedure
1. **Rotate Meal Lists**: Use `rotate_meals` to shift dish order for variety
2. **Group by Cost**: Use `group_dishes_by_cost` to categorize dishes as low/medium/high cost
3. **Filter Lists**: Use `findall` with `member` to extract specific dish types
4. **Combine Results**: Use `append` to merge multiple ingredient lists
5. **Create Associations**: Use `CostLevel-Dishes` pairs to organize grouped results

### Code Snippet
```prolog
% From kb.pl - Advanced list operations
% Advanced list operation: meal rotation
rotate_meals([], []).
rotate_meals([H|T], RotatedMeals) :-
    append(T, [H], RotatedMeals).

% List operation: grouping dishes by characteristics
group_dishes_by_cost(Dishes, GroupedDishes) :-
    group_by_cost(Dishes, low, LowCost),
    group_by_cost(Dishes, medium, MediumCost),
    group_by_cost(Dishes, high, HighCost),
    GroupedDishes = [low-LowCost, medium-MediumCost, high-HighCost].

group_by_cost(Dishes, CostLevel, FilteredDishes) :-
    findall(Dish, (member(Dish, Dishes), dish(Dish, _, _, _, _, _, CostLevel)), FilteredDishes).
```

### Sample Input and Output
**Input**: `?- group_dishes_by_cost([idli_sambar, chicken_curry_rice, upma], Grouped).`
**Output**: `Grouped = [low-[upma], medium-[idli_sambar], high-[chicken_curry_rice]]`

---

### 4g. Cut Operations

### Aim
To control backtracking and improve efficiency by preventing unnecessary exploration of alternative solutions once a suitable dish or condition is found.

### Definition
The cut operator (!) in Prolog prevents backtracking past that point, committing to the current choice and improving efficiency by eliminating unnecessary search paths.

### Syntax
```prolog
predicate_with_cut(Input, Output) :-
    condition1(Input),
    !,  % Cut operator - commits to this choice
    condition2(Input, Output).
```

### Procedure
1. **Find First Suitable Dish**: Use `find_first_suitable_dish` with cut to stop after first match
2. **Check Expensive Meals**: Use `has_expensive_meal_today` with cut to find any high-cost meal
3. **Place Cut After Condition**: Insert `!` after `suitable_dish` condition to commit to choice
4. **Prevent Backtracking**: Stop Prolog from exploring alternative dishes once suitable one found
5. **Improve Performance**: Reduce search time by eliminating unnecessary dish exploration

### Code Snippet
```prolog
% From kb.pl - Cut operations for efficient search
% Cut operation: find first suitable dish (prevents backtracking)
find_first_suitable_dish(Day, MealType, Dish) :-
    dish(Dish, MealType, _, _, _, _, _),
    suitable_dish(Dish, Day, MealType), !.

% Cut operation: check if any high-cost meal exists today
has_expensive_meal_today(Day) :-
    meal_plan(Day, _, Dish),
    dish(Dish, _, _, _, _, _, high), !.
```

### Sample Input and Output
**Input**: `?- find_first_suitable_dish(monday, breakfast, Dish).`
**Output**: `Dish = idli_sambar` (stops after finding first suitable dish, doesn't explore alternatives)

---

### 4h. Negation

### Aim
To implement constraint checking by negating certain conditions, ensuring dishes don't violate dietary restrictions or preferences in meal planning.

### Definition
Negation in Prolog uses the \+ operator to express "not" conditions, allowing the system to exclude solutions that satisfy certain predicates and implement constraint checking.

### Syntax
```prolog
predicate_with_negation(Input, Output) :-
    condition1(Input),
    \+ unwanted_condition(Input),  % Negation
    condition2(Input, Output).
```

### Procedure
1. **Check Dish Suitability**: Use `suitable_dish` with `\+ avoid_dish_today` to exclude unwanted dishes
2. **Apply Vegetarian Constraints**: Use `\+ user_preference(vegetarian_day, Day, true)` to check non-vegetarian days
3. **Negate Avoid Conditions**: Use `\+ avoid_dish_today` to exclude dishes with unwanted ingredients
4. **Implement Constraint Logic**: Structure rules so negation prevents invalid dish selection
5. **Handle Constraint Failures**: Provide fallback when negation conditions fail

### Code Snippet
```prolog
% From kb.pl - Negation for constraint checking
% Rule 1: Check if a dish is suitable for a specific day based on preferences
suitable_dish(Dish, Day, MealType) :-
    dish(Dish, MealType, _, _, IsVeg, _, _),
    \+ avoid_dish_today(Dish, Day),  % Negation: don't avoid this dish
    check_vegetarian_constraint(Dish, Day, IsVeg).

% Rule 2: Vegetarian constraint checking (Negation used here)
check_vegetarian_constraint(_, Day, _) :-
    \+ user_preference(vegetarian_day, Day, true), !.  % Negation: not a vegetarian day
check_vegetarian_constraint(_, Day, true) :-
    user_preference(vegetarian_day, Day, true), !.  % It is a vegetarian day
```

### Sample Input and Output
**Input**: `?- suitable_dish(Dish, monday, breakfast).`
**Output**: `Dish = idli_sambar` (only if idli_sambar doesn't violate any constraints)

---

### 4i. Arithmetic Operations

### Aim
To perform mathematical calculations for meal planning metrics like average preparation time, cost analysis, and statistical computations for algorithm evaluation.

### Definition
Arithmetic operations in Prolog perform mathematical calculations using built-in operators and functions to compute numerical results for data analysis and metrics.

### Syntax
```prolog
arithmetic_predicate(Input, Result) :-
    calculation(Input, Temp),
    Result is Temp + 1.
```

### Procedure
1. **Calculate Meal Statistics**: Use `analyze_meal_distribution` to compute average prep times
2. **Count List Length**: Use `length(PrepTimes, Count)` to count dishes per meal type
3. **Sum Preparation Times**: Use `sum_list(PrepTimes, Total)` to add all prep times
4. **Compute Average**: Use `AvgPrepTime is Total / Count` for arithmetic division
5. **Balance Cost**: Use `HighCount =< 1` to limit expensive meals per day

### Code Snippet
```prolog
% From kb.pl - Arithmetic operations for analysis
% Query 4: Statistical analysis using quantifiers
analyze_meal_distribution(MealType, Count, AvgPrepTime) :-
    findall(PrepTime, dish(_, MealType, _, _, _, PrepTime, _), PrepTimes),
    length(PrepTimes, Count),
    sum_list(PrepTimes, Total),
    (Count > 0 -> AvgPrepTime is Total / Count; AvgPrepTime = 0).

% Cost balancing rule with arithmetic
balance_cost(Day, MealType) :-
    findall(Cost, (meal_plan(Day, MT, D), dish(D, MT, _, _, _, _, Cost)), Costs),
    length(Costs, N),
    N > 0,
    count_high_cost(Costs, HighCount),
    HighCount =< 1.  % Arithmetic comparison
```

### Sample Input and Output
**Input**: `?- analyze_meal_distribution(breakfast, Count, AvgTime).`
**Output**: `Count = 5, AvgTime = 35.0` (5 breakfast dishes with average prep time of 35 minutes)

---

### 4j. Input & Output

### Aim
To handle data exchange between the Prolog knowledge base and Python interface, managing input from users and output of meal plans and grocery lists.

### Definition
Input/Output operations manage the flow of data into and out of the system, including reading user preferences, processing form data, and generating structured output for display.

### Syntax
```python
# Python I/O operations
def get_user_input():
    data = request.form.get('field_name')
    return data

def format_output(data):
    return jsonify({'result': data})
```

### Procedure
1. **Capture Form Data**: Use `request.form.get()` to get dish name, meal type, ingredients from HTML forms
2. **Parse Ingredients**: Split comma-separated ingredient string into list format
3. **Validate Input**: Check required fields (dish_name, meal_type, ingredients) are not empty
4. **Call Prolog Interface**: Use `prolog.add_dish()` to add new dish to knowledge base
5. **Handle Success/Error**: Display flash messages for successful addition or error cases
6. **Redirect Response**: Return to index page with updated dish list

### Code Snippet
```python
# From app.py - Input/Output handling
@app.route('/add_dish', methods=['POST'])
def add_dish():
    """Add a new dish to the knowledge base"""
    try:
        # INPUT: Get form data
        dish_name = request.form.get('dish_name', '').strip()
        meal_type = request.form.get('meal_type', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        recipe = request.form.get('recipe', '').strip()
        is_vegetarian = request.form.get('is_vegetarian') == 'on'
        prep_time = int(request.form.get('prep_time', 30))
        cost_level = request.form.get('cost_level', 'medium')
        
        # PROCESS: Parse ingredients
        ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
        
        # OUTPUT: Add dish to Prolog knowledge base
        success = prolog.add_dish(
            dish_name, meal_type, ingredient_list, recipe, 
            is_vegetarian, prep_time, cost_level
        )
        
        if success:
            flash(f'Successfully added {dish_name}!', 'success')
        else:
            flash('Error adding dish. Please try again.', 'error')
            
    except Exception as e:
        logger.error(f"Error adding dish: {e}")
        flash('Error adding dish. Please check your input and try again.', 'error')
    
    return redirect(url_for('index'))
```

### Sample Input and Output
**Input**: Form data with dish_name="Paneer Tikka", meal_type="dinner", ingredients="paneer, yogurt, spices"
**Output**: Success message "Successfully added Paneer Tikka!" and redirect to index page

---

### 4k. Dynamic Predicates

### Aim
To modify the Prolog knowledge base at runtime by adding new dishes, deleting existing ones, and updating user preferences dynamically without restarting the system.

### Definition
Dynamic predicates in Prolog can be modified during program execution using assert/retract operations, allowing the knowledge base to be updated with new facts or rules at runtime.

### Syntax
```prolog
:- dynamic predicate_name/arity.

add_fact(Args) :-
    assertz(predicate_name(Args)).

remove_fact(Args) :-
    retractall(predicate_name(Args)).
```

### Procedure
1. **Declare Dynamic Predicates**: Use `:- dynamic dish/7` to allow runtime modifications
2. **Add New Dishes**: Use `assertz(dish(...))` in `add_new_dish` to insert new dish facts
3. **Delete Dishes**: Use `retractall(dish(Name, _, _, _, _, _, _))` in `delete_dish` to remove dish facts
4. **Update Preferences**: Use `retractall` + `assertz` in `update_preference` to modify user settings
5. **Handle Duplicates**: Check `\+ dish(Name, _, _, _, _, _, _)` before adding to prevent duplicates

### Code Snippet
```prolog
% From kb.pl - Dynamic predicates for runtime modifications
% Dynamic predicates for runtime modifications
:- dynamic dish/7.
:- dynamic user_preference/3.
:- dynamic meal_plan/3.
:- dynamic grocery_item/2.

% Add new dish dynamically
add_new_dish(Name, MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost) :-
    \+ dish(Name, _, _, _, _, _, _),
    assertz(dish(Name, MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost)).

% Delete a dish dynamically
delete_dish(Name) :-
    retractall(dish(Name, _, _, _, _, _, _)).

% Update user preferences dynamically
update_preference(Type, Value, Setting) :-
    retractall(user_preference(Type, Value, _)),
    assertz(user_preference(Type, Value, Setting)).
```

### Sample Input and Output
**Input**: `?- add_new_dish('biryani', dinner, [rice, chicken, spices], 'Cook rice and chicken together', false, 90, high).`
**Output**: `true` (new dish added to knowledge base)

---

## 5. AI Algorithms

### 5a. A* Algorithm

### Aim
To find optimal meal plans by searching through possible dish combinations using heuristic evaluation, minimizing cost while maximizing variety and nutritional balance.

### Definition
A* is an informed search algorithm that finds the shortest path in a graph by using both the actual cost from the start and a heuristic estimate to the goal, ensuring optimal solutions.

### Syntax
```python
def a_star_search(start_state, goal_test, heuristic_func):
    open_set = PriorityQueue()
    open_set.put((0, start_state))
    closed_set = set()
    
    while not open_set.empty():
        current_cost, current_state = open_set.get()
        if goal_test(current_state):
            return current_state
        closed_set.add(current_state)
        for neighbor in get_neighbors(current_state):
            if neighbor not in closed_set:
                f_cost = current_cost + heuristic_func(neighbor)
                open_set.put((f_cost, neighbor))
```

### Procedure
1. **Initialize A* Search**: Create `MealPlanState` with start date and preferences
2. **Setup Priority Queue**: Use `open_set` with (f_cost, state) tuples for best-first search
3. **Calculate Heuristic**: Use `_calculate_heuristic` to evaluate variety, nutrition, and cost balance
4. **Generate Successors**: Use `_generate_successors` to create new meal plan states
5. **Compute F-Cost**: Calculate `f_cost = g_cost + h_cost` for each successor state
6. **Check Completion**: Use `_is_complete_plan` to verify all 7 days × 4 meals are assigned
7. **Handle Timeout**: Use `_greedy_complete_plan` fallback if A* search times out
8. **Return Optimal Plan**: Format and return the best meal plan found

### Code Snippet
```python
# From algorithms.py - A* meal planning implementation
class AStarMealPlanner:
    def __init__(self, prolog_interface):
        self.prolog = prolog_interface
        self.max_iterations = 1000
        self.timeout = 30  # seconds
    
    def generate_meal_plan(self, start_date, preferences, query_id):
        """Generate meal plan using A* algorithm"""
        try:
            # Initialize search
            initial_state = MealPlanState(start_date, preferences)
            open_set = [(0, initial_state)]
            closed_set = set()
            iterations = 0
            
            while open_set and iterations < self.max_iterations:
                iterations += 1
                
                # Check for cancellation
                if self._is_cancelled(query_id):
                    return None
                
                # Get best state from open set
                current_cost, current_state = heapq.heappop(open_set)
                
                # Check if complete plan
                if self._is_complete_plan(current_state):
                    return self._format_meal_plan(current_state.assigned_meals)
                
                # Add to closed set
                closed_set.add(current_state.get_state_key())
                
                # Generate successors
                successors = self._generate_successors(current_state, preferences)
                
                for successor in successors:
                    if successor.get_state_key() not in closed_set:
                        # Calculate f-cost = g-cost + h-cost
                        g_cost = current_cost + 1
                        h_cost = self._calculate_heuristic(successor, preferences)
                        f_cost = g_cost + h_cost
                        
                        heapq.heappush(open_set, (f_cost, successor))
            
            # Fallback: return best partial solution
            if open_set:
                best_partial = min(open_set, key=lambda x: x[0])
                final_plan = self._format_meal_plan(best_partial[1].assigned_meals)
                return self._greedy_complete_plan(final_plan, preferences)
            
            return None
            
        except Exception as e:
            logger.error(f"A* planning error: {e}")
            return None
    
    def _calculate_heuristic(self, state, preferences):
        """Calculate heuristic cost for A* algorithm"""
        cost = 0
        
        # Variety penalty (encourage different dishes)
        used_dishes = set()
        for day_meals in state.assigned_meals.values():
            for dish in day_meals.values():
                if dish != 'No dish available':
                    if dish in used_dishes:
                        cost += 2  # Penalty for repetition
                    used_dishes.add(dish)
        
        # Nutritional balance (simplified)
        veg_count = sum(1 for day_meals in state.assigned_meals.values() 
                       for dish in day_meals.values() 
                       if self._is_vegetarian_dish(dish))
        cost += abs(veg_count - 14)  # Prefer balanced vegetarian/non-veg
        
        # Cost balance
        high_cost_days = sum(1 for day_meals in state.assigned_meals.values()
                             if any(self._is_high_cost_dish(dish) 
                                   for dish in day_meals.values()))
        cost += high_cost_days * 3  # Penalty for too many expensive meals
        
        return cost
```

### Sample Input and Output
**Input**: Start date "2024-01-15", preferences with vegetarian days [monday, wednesday]
**Output**: Complete 7-day meal plan with optimal dish selection minimizing repetition and cost while respecting constraints

---

### 5b. AO* Algorithm

### Aim
To solve complex meal planning problems by decomposing them into AND-OR trees, handling multiple constraints simultaneously and finding solutions that satisfy all requirements.

### Definition
AO* (AND-OR search) is an algorithm that searches AND-OR graphs where nodes can be either AND nodes (all children must be solved) or OR nodes (any child can be solved), handling complex constraint satisfaction.

### Syntax
```python
def ao_star_search(problem_graph):
    while True:
        # Mark best path
        mark_best_path(problem_graph)
        
        # Expand marked nodes
        expand_marked_nodes(problem_graph)
        
        # Update costs
        update_costs(problem_graph)
        
        if no_marked_nodes():
            break
    
    return extract_solution(problem_graph)
```

### Procedure
1. **Initialize AND-OR Tree**: Create `ANDNode` root for weekly plan with day and meal constraints
2. **Mark Best Path**: Use `_mark_best_path` to identify optimal solution path through tree
3. **Expand Day Nodes**: Convert day nodes into breakfast/lunch/snacks/dinner meal nodes
4. **Expand Meal Nodes**: Generate dish options for each meal slot based on constraints
5. **Update Costs**: Recalculate costs throughout tree using `_update_costs`
6. **Check Solution**: Use `is_solved()` to verify all AND conditions are satisfied
7. **Extract Solution**: Use `_extract_solution` to build final meal plan from solved tree
8. **Handle Fallback**: Use `_greedy_fallback` if AO* search fails to find complete solution

### Code Snippet
```python
# From algorithms.py - AO* meal planning implementation
class AOStarMealPlanner:
    def __init__(self, prolog_interface):
        self.prolog = prolog_interface
        self.max_iterations = 500
        self.timeout = 20  # seconds
    
    def generate_meal_plan(self, start_date, preferences, query_id):
        """Generate meal plan using AO* algorithm"""
        try:
            # Initialize AND-OR tree
            root_node = ANDNode("weekly_plan", start_date, preferences)
            problem_graph = {root_node.id: root_node}
            
            iterations = 0
            while iterations < self.max_iterations:
                iterations += 1
                
                # Check for cancellation
                if self._is_cancelled(query_id):
                    return None
                
                # Mark best path
                self._mark_best_path(problem_graph, root_node.id)
                
                # Expand marked nodes
                expanded = self._expand_marked_nodes(problem_graph, preferences)
                
                # Update costs
                self._update_costs(problem_graph, root_node.id)
                
                # Check if solution found
                if root_node.is_solved():
                    return self._extract_solution(problem_graph, root_node.id)
                
                if not expanded:
                    break
            
            # Fallback to greedy completion
            return self._greedy_fallback(start_date, preferences)
            
        except Exception as e:
            logger.error(f"AO* planning error: {e}")
            return None
    
    def _mark_best_path(self, graph, node_id):
        """Mark the best path in the AND-OR tree"""
        node = graph[node_id]
        
        if isinstance(node, ORNode):
            # Choose best child
            best_child = min(node.children, key=lambda c: graph[c].cost)
            graph[best_child].marked = True
            self._mark_best_path(graph, best_child)
            
        elif isinstance(node, ANDNode):
            # Mark all children
            for child_id in node.children:
                graph[child_id].marked = True
                self._mark_best_path(graph, child_id)
    
    def _expand_marked_nodes(self, graph, preferences):
        """Expand marked nodes in the AND-OR tree"""
        expanded = False
        
        for node_id, node in list(graph.items()):
            if node.marked and not node.expanded:
                if isinstance(node, DayNode):
                    # Expand day into meal slots
                    self._expand_day_node(graph, node, preferences)
                    expanded = True
                elif isinstance(node, MealNode):
                    # Expand meal into dish options
                    self._expand_meal_node(graph, node, preferences)
                    expanded = True
                
                node.expanded = True
        
        return expanded
    
    def _expand_day_node(self, graph, day_node, preferences):
        """Expand a day node into meal nodes"""
        meal_types = ['breakfast', 'lunch', 'snacks', 'dinner']
        
        for meal_type in meal_types:
            meal_id = f"{day_node.day}_{meal_type}"
            meal_node = MealNode(meal_id, day_node.day, meal_type, preferences)
            graph[meal_id] = meal_node
            day_node.children.append(meal_id)
    
    def _expand_meal_node(self, graph, meal_node, preferences):
        """Expand a meal node into dish options"""
        # Get suitable dishes for this meal
        suitable_dishes = self.prolog.get_dishes_by_meal_type(meal_node.meal_type)
        
        # Filter by constraints
        for dish in suitable_dishes:
            if self._is_dish_suitable(dish, meal_node.day, meal_node.meal_type, preferences):
                dish_id = f"{meal_node.id}_{dish}"
                dish_node = DishNode(dish_id, dish, meal_node.day, meal_node.meal_type)
                graph[dish_id] = dish_node
                meal_node.children.append(dish_id)
```

### Sample Input and Output
**Input**: Complex preferences with multiple constraints (vegetarian days, avoid ingredients, cost limits)
**Output**: Complete meal plan satisfying all AND-OR constraints with optimal cost and variety balance

---

### AND-OR Graph Diagram (AO* Search Structure)
```
Root: weekly_plan (AND)
│
├─ Day1 (AND)
│   ├─ D1.breakfast (OR)
│   │   ├─ idli_sambar (cost c1)   ┐
│   │   ├─ dosa_chutney (cost c2)  ├─ choose best OR child by updated cost
│   │   └─ upma (cost c3)          ┘
│   │
│   ├─ D1.lunch (OR)
│   │   ├─ sambar_rice (cost c4)
│   │   ├─ curd_rice (cost c5)
│   │   └─ veg_biryani (cost c6)
│   │
│   ├─ D1.snacks (OR)
│   │   └─ ... dish options ...
│   │
│   └─ D1.dinner (OR)
│       └─ ... dish options ...
│
├─ Day2 (AND)
│   └─ (same 4 meal OR nodes)
│
└─ ... Day7 (AND)

AO* Iteration Cycle:
1) Mark best path from root using current costs
2) Expand marked nodes only (AND → add all children; OR → add feasible dish options)
3) Update costs bottom-up:
   • AND node cost = sum(children costs)
   • OR node cost = min(children costs)
4) If root is solved (all AND branches solved), extract solution; else repeat

Annotations:
- Constraints (veg day, avoid ingredients, repetition, cost balance) prune OR options
- If expansion stalls, planner falls back to greedy completion in code
```

## Summary

This comprehensive meal planning system demonstrates the integration of multiple AI concepts:

- **Flask Web Application**: Provides user interface and API endpoints
- **Prolog Logic Programming**: Implements knowledge base with facts, rules, queries, recursion, backtracking, unification, list operations, cut operations, negation, arithmetic operations, I/O, and dynamic predicates
- **AI Algorithms**: Uses A* for optimal search and AO* for complex constraint satisfaction
- **Visualization**: Creates graphical representations of meal plans and algorithm performance

Each concept works together to create an intelligent meal planning system that generates optimal weekly meal plans while respecting user preferences and constraints.
