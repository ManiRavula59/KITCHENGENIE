% Smart Kitchen Meal Planner Knowledge Base
% Implementing Facts, Rules, Queries, Recursion, Backtracking, Quantifiers,
% Unification, List Operations, Cut Operations, Negation, Dynamic Predicates

% Dynamic predicates for runtime modifications
:- dynamic dish/7.
:- dynamic user_preference/3.
:- dynamic meal_plan/3.
:- dynamic grocery_item/2.

% Facts: 25+ dishes with complete ingredient/recipe data
% dish(Name, MealType, Ingredients, Recipe, IsVegetarian, PrepTime, CostLevel)

% Breakfast dishes
dish('idli_sambar', breakfast, 
     ['idli_rice', 'urad_dal', 'fenugreek_seeds', 'salt', 'toor_dal', 'tamarind', 'turmeric', 'tomato', 'onion', 'curry_leaves'],
     'Soak rice and dal separately for 6 hours. Grind to smooth batter. Ferment overnight. Steam in idli plates for 12 minutes. For sambar: boil toor dal, add tamarind extract, vegetables, and spices.',
     true, 45, medium).

dish('dosa_chutney', breakfast,
     ['dosa_batter', 'coconut', 'green_chili', 'ginger', 'curry_leaves', 'mustard_seeds', 'oil'],
     'Spread dosa batter on hot pan. Cook until golden. For chutney: grind coconut, green chili, ginger with water. Temper with mustard seeds and curry leaves.',
     true, 30, low).

dish('upma', breakfast,
     ['semolina', 'onion', 'green_chili', 'ginger', 'curry_leaves', 'mustard_seeds', 'oil', 'salt'],
     'Roast semolina until aromatic. In another pan, heat oil, add mustard seeds, curry leaves. Add chopped onions, green chili, ginger. Add water, bring to boil. Slowly add semolina while stirring.',
     true, 25, low).

dish('pongal', breakfast,
     ['rice', 'moong_dal', 'ghee', 'black_pepper', 'cumin', 'ginger', 'curry_leaves', 'cashews'],
     'Cook rice and moong dal together until mushy. In separate pan, heat ghee, add pepper, cumin, ginger, curry leaves, cashews. Mix with cooked rice mixture.',
     true, 35, medium).

dish('poori_potato_curry', breakfast,
     ['wheat_flour', 'oil', 'salt', 'potato', 'onion', 'tomato', 'turmeric', 'red_chili_powder', 'coriander_powder'],
     'Make stiff dough with flour and water. Roll small circles and deep fry until puffed. For curry: cook potatoes, make gravy with onions, tomatoes, and spices.',
     true, 40, medium).

% Lunch dishes
dish('chicken_curry_rice', lunch,
     ['chicken', 'rice', 'onion', 'tomato', 'ginger_garlic_paste', 'red_chili_powder', 'turmeric', 'coriander_powder', 'garam_masala', 'oil', 'salt'],
     'Marinate chicken with spices. Cook rice separately. Make curry by sautéing onions, adding tomatoes and spices. Add chicken and cook until tender.',
     false, 60, high).

dish('sambar_rice', lunch,
     ['rice', 'toor_dal', 'tamarind', 'drumstick', 'okra', 'tomato', 'onion', 'turmeric', 'sambar_powder', 'curry_leaves'],
     'Cook rice and toor dal separately. Make sambar by boiling vegetables with tamarind extract, dal, and spices. Serve hot with rice.',
     true, 45, medium).

dish('rasam_rice', lunch,
     ['rice', 'toor_dal', 'tamarind', 'tomato', 'rasam_powder', 'turmeric', 'asafoetida', 'curry_leaves', 'coriander_leaves'],
     'Cook rice and dal. Extract tamarind juice. Boil tomatoes with tamarind, add dal water, rasam powder, and spices. Garnish with coriander.',
     true, 30, low).

dish('curd_rice', lunch,
     ['rice', 'curd', 'salt', 'green_chili', 'ginger', 'curry_leaves', 'mustard_seeds', 'oil'],
     'Cook rice and let it cool. Mix with fresh curd and salt. Temper with mustard seeds, curry leaves, green chili, and ginger.',
     true, 15, low).

dish('fish_curry_rice', lunch,
     ['fish', 'rice', 'coconut', 'red_chili', 'turmeric', 'tamarind', 'onion', 'curry_leaves', 'oil'],
     'Clean fish and marinate with turmeric and salt. Make coconut paste with red chilies. Cook curry with coconut paste, tamarind, and fish.',
     false, 50, high).

dish('vegetable_biryani', lunch,
     ['basmati_rice', 'mixed_vegetables', 'onion', 'tomato', 'yogurt', 'biryani_masala', 'saffron', 'ghee', 'mint_leaves'],
     'Soak rice for 30 minutes. Cook vegetables with spices. Layer rice and vegetables, cook dum style with saffron and ghee.',
     true, 75, high).

dish('mutton_curry_rice', lunch,
     ['mutton', 'rice', 'onion', 'tomato', 'yogurt', 'ginger_garlic_paste', 'red_chili_powder', 'garam_masala', 'oil'],
     'Marinate mutton with yogurt and spices. Cook in pressure cooker until tender. Make rich gravy with onions and tomatoes.',
     false, 90, high).

% Snacks
dish('medu_vada', snacks,
     ['urad_dal', 'green_chili', 'ginger', 'curry_leaves', 'asafoetida', 'salt', 'oil'],
     'Soak urad dal for 4 hours. Grind to smooth batter. Add chopped green chili, ginger, curry leaves. Shape into donuts and deep fry.',
     true, 35, medium).

dish('masala_vada', snacks,
     ['chana_dal', 'onion', 'green_chili', 'ginger', 'coriander_leaves', 'fennel_seeds', 'red_chili_powder', 'oil'],
     'Soak chana dal for 2 hours. Grind coarsely. Mix with chopped onions, chilies, spices. Deep fry small portions until golden.',
     true, 30, medium).

dish('bajji', snacks,
     ['besan', 'rice_flour', 'vegetables', 'green_chili', 'ginger', 'turmeric', 'red_chili_powder', 'oil'],
     'Make batter with besan, rice flour, and spices. Dip vegetable slices in batter and deep fry until crispy.',
     true, 25, medium).

dish('sundal', snacks,
     ['chickpeas', 'coconut', 'green_chili', 'curry_leaves', 'mustard_seeds', 'asafoetida', 'oil', 'salt'],
     'Pressure cook chickpeas. Temper with mustard seeds, curry leaves. Add chickpeas, grated coconut, and spices.',
     true, 20, low).

dish('murukku', snacks,
     ['rice_flour', 'urad_dal_flour', 'sesame_seeds', 'cumin_seeds', 'asafoetida', 'salt', 'oil'],
     'Mix flours with spices and hot oil. Make dough with water. Use murukku press to shape and deep fry until golden.',
     true, 45, medium).

% Dinner dishes
dish('chapati_dal', dinner,
     ['wheat_flour', 'toor_dal', 'turmeric', 'green_chili', 'ginger', 'tomato', 'onion', 'cumin_seeds', 'ghee'],
     'Make soft chapati dough and roll thin. Cook on tawa. For dal: pressure cook toor dal with turmeric. Temper with cumin, add vegetables.',
     true, 40, low).

dish('fried_rice', dinner,
     ['rice', 'mixed_vegetables', 'soy_sauce', 'garlic', 'ginger', 'spring_onion', 'oil', 'salt'],
     'Cook rice and let it cool. Stir fry vegetables with garlic, ginger. Add rice, soy sauce, and spring onions. Toss well.',
     true, 30, medium).

dish('chicken_biryani', dinner,
     ['basmati_rice', 'chicken', 'yogurt', 'onion', 'saffron', 'biryani_masala', 'mint_leaves', 'ghee', 'eggs'],
     'Marinate chicken with yogurt and spices. Cook rice 70%. Layer chicken and rice. Cook dum style with saffron, mint, and ghee.',
     false, 120, high).

dish('prawn_curry_rice', dinner,
     ['prawns', 'rice', 'coconut_milk', 'red_chili', 'turmeric', 'ginger_garlic_paste', 'curry_leaves', 'oil'],
     'Clean prawns and marinate. Make curry with coconut milk, spices, and curry leaves. Add prawns and cook until done.',
     false, 45, high).

dish('paneer_butter_masala', dinner,
     ['paneer', 'tomato', 'onion', 'cashews', 'cream', 'butter', 'garam_masala', 'red_chili_powder', 'ginger_garlic_paste'],
     'Make rich tomato gravy with cashews and cream. Add cubed paneer and simmer. Finish with butter and garam masala.',
     true, 35, high).

dish('egg_curry_rice', dinner,
     ['eggs', 'rice', 'onion', 'tomato', 'coconut', 'red_chili_powder', 'turmeric', 'curry_leaves', 'oil'],
     'Boil eggs and keep aside. Make curry with onions, tomatoes, coconut paste. Add eggs and simmer. Serve with rice.',
     false, 35, medium).

dish('vegetable_pulao', dinner,
     ['basmati_rice', 'mixed_vegetables', 'whole_spices', 'onion', 'ghee', 'mint_leaves', 'saffron'],
     'Sauté vegetables and whole spices. Add rice and water. Cook until rice is done. Garnish with mint and saffron.',
     true, 40, medium).

dish('lemon_rice', dinner,
     ['rice', 'lemon', 'turmeric', 'mustard_seeds', 'curry_leaves', 'peanuts', 'green_chili', 'oil'],
     'Cook rice and let it cool. Heat oil, add mustard seeds, curry leaves, green chili, peanuts. Mix with rice and lemon juice.',
     true, 20, low).

dish('tamarind_rice', dinner,
     ['rice', 'tamarind', 'red_chili', 'coriander_seeds', 'fenugreek_seeds', 'turmeric', 'peanuts', 'sesame_oil'],
     'Cook rice. Make tamarind paste. Prepare spice powder. Mix everything together with sesame oil and serve.',
     true, 30, medium).

dish('tomato_rice', dinner,
     ['rice', 'tomato', 'onion', 'green_chili', 'ginger', 'curry_leaves', 'mustard_seeds', 'turmeric', 'oil'],
     'Cook rice separately. Make tomato gravy with onions and spices. Mix with rice and garnish with curry leaves.',
     true, 25, low).

% Rules: Complex meal planning logic with constraints

% Rule 1: Check if a dish is suitable for a specific day based on preferences
suitable_dish(Dish, Day, MealType) :-
    dish(Dish, MealType, _, _, IsVeg, _, _),
    \+ avoid_dish_today(Dish, Day),
    check_vegetarian_constraint(Dish, Day, IsVeg).

% Rule 2: Vegetarian constraint checking (Negation used here)
check_vegetarian_constraint(_, Day, IsVeg) :-
    user_preference(vegetarian_day, Day, true), !,
    IsVeg = true.
check_vegetarian_constraint(_, Day, _) :-
    \+ user_preference(vegetarian_day, Day, true), !.

% Rule 3: Avoid ingredient constraints
avoid_dish_today(Dish, _) :-
    dish(Dish, _, Ingredients, _, _, _, _),
    user_preference(avoid_ingredient, Ingredient, true),
    member(Ingredient, Ingredients), !.

% Rule 4: Meal variety constraint - avoid repetition within 3 days
avoid_repetition(Dish, Day) :-
    meal_plan(PrevDay, _, Dish),
    days_between(PrevDay, Day, Diff),
    Diff < 3, !.

% Rule 5: Cost balancing rule
balance_cost(Day, MealType) :-
    findall(Cost, (meal_plan(Day, MT, D), dish(D, MT, _, _, _, _, Cost)), Costs),
    length(Costs, N),
    N > 0,
    count_high_cost(Costs, HighCount),
    HighCount =< 1.

count_high_cost([], 0).
count_high_cost([high|Rest], Count) :-
    count_high_cost(Rest, RestCount),
    Count is RestCount + 1.
count_high_cost([_|Rest], Count) :-
    count_high_cost(Rest, Count).

% Queries: Dynamic data retrieval and manipulation

% Query 1: Get all dishes of a specific meal type
get_dishes_by_meal_type(MealType, Dishes) :-
    findall(Dish, dish(Dish, MealType, _, _, _, _, _), Dishes).

% Query 2: Get ingredients for a specific dish
get_dish_ingredients(Dish, Ingredients) :-
    dish(Dish, _, Ingredients, _, _, _, _).

% Query 3: Find vegetarian dishes only (Quantifiers with findall)
get_vegetarian_dishes(VegDishes) :-
    findall(Dish, dish(Dish, _, _, _, true, _, _), VegDishes).

% Query 4: Statistical analysis using quantifiers
analyze_meal_distribution(MealType, Count, AvgPrepTime) :-
    findall(PrepTime, dish(_, MealType, _, _, _, PrepTime, _), PrepTimes),
    length(PrepTimes, Count),
    sum_list(PrepTimes, Total),
    (Count > 0 -> AvgPrepTime is Total / Count; AvgPrepTime = 0).

% Recursion: Ingredient collection and duplicate removal

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

% Backtracking: Alternative dish suggestions

% Find alternative dishes with backtracking
suggest_alternative(Day, MealType, CurrentDish, Alternative) :-
    dish(Alternative, MealType, _, _, _, _, _),
    Alternative \= CurrentDish,
    suitable_dish(Alternative, Day, MealType),
    \+ avoid_repetition(Alternative, Day).

% Generate multiple alternatives using backtracking
find_alternatives(Day, MealType, CurrentDish, Alternatives) :-
    findall(Alt, suggest_alternative(Day, MealType, CurrentDish, Alt), Alternatives).

% Unification: Pattern matching for dish selection

% Pattern matching for dish characteristics
match_dish_pattern(Pattern, Dish) :-
    dish(Dish, MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost),
    unify_pattern(Pattern, [MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost]).

unify_pattern([], []).
unify_pattern([H|T], [H|Rest]) :-
    unify_pattern(T, Rest).
unify_pattern([_|T], [_|Rest]) :-
    unify_pattern(T, Rest).

% List Operations: Advanced list processing

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

% Cut Operations: Efficient search termination

% Cut operation: find first suitable dish (prevents backtracking)
find_first_suitable_dish(Day, MealType, Dish) :-
    dish(Dish, MealType, _, _, _, _, _),
    suitable_dish(Dish, Day, MealType), !.

% Cut operation: check if any high-cost meal exists today
has_expensive_meal_today(Day) :-
    meal_plan(Day, _, Dish),
    dish(Dish, _, _, _, _, _, high), !.

% Dynamic Predicates: Runtime modifications

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

% Add meal to plan dynamically
add_to_meal_plan(Day, MealType, Dish) :-
    retractall(meal_plan(Day, MealType, _)),
    assertz(meal_plan(Day, MealType, Dish)).

% Meal Plan Generation with AI Logic

% Main predicate for generating weekly meal plan
generate_weekly_plan(StartDate, Preferences, Plan) :-
    setup_preferences(Preferences),
    generate_days_list(StartDate, 7, Days),
    generate_plan_for_days(Days, [], Plan),
    validate_plan(Plan).

% Generate list of days from start date
generate_days_list(_, 0, []).
generate_days_list(StartDate, N, [StartDate|RestDays]) :-
    N > 0,
    N1 is N - 1,
    next_date(StartDate, NextDate),
    generate_days_list(NextDate, N1, RestDays).

% Generate plan for each day
generate_plan_for_days([], Plan, Plan).
generate_plan_for_days([Day|RestDays], AccPlan, FinalPlan) :-
    generate_day_plan(Day, DayMeals),
    append(AccPlan, [Day-DayMeals], NewAccPlan),
    generate_plan_for_days(RestDays, NewAccPlan, FinalPlan).

% Generate meals for a single day
generate_day_plan(Day, DayMeals) :-
    select_meal(Day, breakfast, Breakfast),
    select_meal(Day, lunch, Lunch),
    select_meal(Day, snacks, Snacks),
    select_meal(Day, dinner, Dinner),
    DayMeals = [breakfast-Breakfast, lunch-Lunch, snacks-Snacks, dinner-Dinner].

% Select appropriate meal with constraints
select_meal(Day, MealType, SelectedDish) :-
    findall(Dish, suitable_dish(Dish, Day, MealType), SuitableDishes),
    ( SuitableDishes \= [] ->
        random_member(SelectedDish, SuitableDishes)
    ;   % Fallback: pick any dish of the meal type
        findall(Dish2, dish(Dish2, MealType, _, _, _, _, _), AllDishes),
        ( AllDishes \= [] ->
            random_member(SelectedDish, AllDishes)
        ;   % Last resort: assign a placeholder
            SelectedDish = 'fallback_dish'
        )
    ),
    add_to_meal_plan(Day, MealType, SelectedDish).

% Validate the generated plan
validate_plan(Plan) :-
    length(Plan, 7),  % Ensure 7 days
    forall(member(_-DayMeals, Plan), 
           (member(breakfast-_, DayMeals),
            member(lunch-_, DayMeals),
            member(snacks-_, DayMeals),
            member(dinner-_, DayMeals))).

% Setup user preferences from input
setup_preferences(Preferences) :-
    retractall(user_preference(_, _, _)),
    setup_vegetarian_days(Preferences),
    setup_avoid_ingredients(Preferences).

setup_vegetarian_days(Preferences) :-
    (member(vegetarian_days-VegDays, Preferences) ->
        forall(member(Day, VegDays), 
               assertz(user_preference(vegetarian_day, Day, true)));
        true).

setup_avoid_ingredients(Preferences) :-
    (member(avoid_ingredients-AvoidList, Preferences) ->
        forall(member(Ingredient, AvoidList),
               assertz(user_preference(avoid_ingredient, Ingredient, true)));
        true).

% Utility predicates
days_between(Day1, Day2, Diff) :-
    % Simplified day difference calculation
    atom_chars(Day1, Chars1),
    atom_chars(Day2, Chars2),
    length(Chars1, L1),
    length(Chars2, L2),
    Diff is abs(L1 - L2).  % Simplified for demo

next_date(Date, NextDate) :-
    % Simplified date increment
    atom_concat(Date, '_next', NextDate).

% Generate grocery list from meal plan
generate_grocery_list(Plan, GroceryList) :-
    extract_all_dishes(Plan, AllDishes),
    collect_ingredients(AllDishes, AllIngredients),
    remove_duplicates(AllIngredients, GroceryList).

extract_all_dishes([], []).
extract_all_dishes([_-DayMeals|RestPlan], AllDishes) :-
    extract_day_dishes(DayMeals, DayDishes),
    extract_all_dishes(RestPlan, RestDishes),
    append(DayDishes, RestDishes, AllDishes).

extract_day_dishes([], []).
extract_day_dishes([_-Dish|RestMeals], [Dish|RestDishes]) :-
    extract_day_dishes(RestMeals, RestDishes).

% Get dish details for frontend
get_dish_details(DishName, Details) :-
    dish(DishName, MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost),
    Details = [
        meal_type-MealType,
        ingredients-Ingredients,
        recipe-Recipe,
        vegetarian-IsVeg,
        prep_time-PrepTime,
        cost_level-Cost
    ].

% Initialize default preferences
init_default_preferences :-
    assertz(user_preference(vegetarian_day, sunday, false)),
    assertz(user_preference(family_size, 4, true)).

% Startup initialization
:- init_default_preferences.
