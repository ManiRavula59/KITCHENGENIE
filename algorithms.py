import heapq
import logging
import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class MealPlanState:
    """Represents a state in the meal planning search space"""
    day: int
    meal_type: str
    assigned_meals: Dict[Tuple[int, str], str]
    cost: float
    heuristic: float
    
    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

@dataclass
class AONode:
    """Represents a node in the AO* search tree"""
    state: Dict
    node_type: str  # 'AND' or 'OR'
    children: List['AONode']
    value: float
    solved: bool
    
class AStarMealPlanner:
    """A* Algorithm implementation for optimal meal planning"""
    
    def __init__(self, prolog_interface):
        self.prolog = prolog_interface
        self.meal_types = ['breakfast', 'lunch', 'snacks', 'dinner']
        self.search_metrics = {
            'nodes_explored': 0,
            'total_time': 0.0,
            'path_length': 0
        }
    
    def generate_meal_plan(self, start_date: str, preferences: Dict, query_id: str) -> Optional[Dict]:
        """
        Generate optimal weekly meal plan using A* algorithm
        
        Heuristic function considers:
        - Nutritional balance score
        - Cost efficiency
        - Variety score
        - Constraint satisfaction
        """
        start_time = time.time()
        self.search_metrics['nodes_explored'] = 0
        
        try:
            logger.info(f"Starting A* meal planning for query {query_id}")
            
            # Initialize search
            initial_state = MealPlanState(
                day=0,
                meal_type=self.meal_types[0],
                assigned_meals={},
                cost=0.0,
                heuristic=self.calculate_heuristic({}, preferences)
            )
            
            # Priority queue for A* search
            open_set = [initial_state]
            closed_set = set()
            
            # Search for optimal solution
            while open_set:
                # Check if query was cancelled
                if self._is_query_cancelled(query_id):
                    logger.info(f"A* search cancelled for query {query_id}")
                    return None
                
                current_state = heapq.heappop(open_set)
                self.search_metrics['nodes_explored'] += 1
                
                # Check if goal state reached (7 days * 4 meals = 28 assignments)
                if len(current_state.assigned_meals) >= 28:
                    self.search_metrics['total_time'] = time.time() - start_time
                    self.search_metrics['path_length'] = len(current_state.assigned_meals)
                    logger.info(f"A* found solution in {self.search_metrics['total_time']:.2f}s")
                    return self._format_meal_plan(current_state.assigned_meals)
                
                # Skip if already explored
                state_key = self._get_state_key(current_state)
                if state_key in closed_set:
                    continue
                closed_set.add(state_key)
                
                # Generate successor states
                successors = self._generate_successors(current_state, preferences)
                
                for successor in successors:
                    if self._get_state_key(successor) not in closed_set:
                        heapq.heappush(open_set, successor)
                
                # Timeout protection
                if time.time() - start_time > 10:  # reduce timeout for responsiveness
                    logger.warning("A* search timeout, completing plan greedily")
                    break
            
            # If no complete solution found, complete plan greedily and return
            best_partial = None
            if open_set:
                best_partial = min(open_set, key=lambda x: x.cost + x.heuristic)
            partial_assignments = best_partial.assigned_meals if best_partial else {}
            completed_assignments = self._complete_plan(partial_assignments, preferences)
            return self._format_meal_plan(completed_assignments)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in A* meal planning: {e}")
            return None
    
    def _generate_successors(self, state: MealPlanState, preferences: Dict) -> List[MealPlanState]:
        """Generate successor states by assigning next meal"""
        successors = []
        
        # Determine next meal slot
        current_day = state.day
        current_meal_idx = self.meal_types.index(state.meal_type)
        
        if current_meal_idx < len(self.meal_types) - 1:
            next_day = current_day
            next_meal_type = self.meal_types[current_meal_idx + 1]
        else:
            next_day = current_day + 1
            next_meal_type = self.meal_types[0]
        
        # Don't exceed 7 days
        if next_day >= 7:
            return successors
        
        # Get suitable dishes for next meal
        day_name = self._get_day_name(next_day)
        suitable_dishes = self.prolog.get_suitable_dishes(day_name, next_meal_type, preferences)
        # Encourage variety by exploring in random order
        random.shuffle(suitable_dishes)
        
        for dish in suitable_dishes[:5]:  # Limit branching factor
            new_assigned = state.assigned_meals.copy()
            meal_key = (next_day, next_meal_type)
            new_assigned[meal_key] = dish
            
            # Calculate costs
            meal_cost = self._calculate_meal_cost(dish, new_assigned, preferences)
            total_cost = state.cost + meal_cost
            heuristic = self.calculate_heuristic(new_assigned, preferences)
            
            successor = MealPlanState(
                day=next_day,
                meal_type=next_meal_type,
                assigned_meals=new_assigned,
                cost=total_cost,
                heuristic=heuristic
            )
            
            successors.append(successor)
        
        return successors
    
    def calculate_heuristic(self, assigned_meals: Dict, preferences: Dict) -> float:
        """
        Heuristic function for A* algorithm
        
        Lower values indicate better states (minimization problem)
        """
        if not assigned_meals:
            return 50.0  # Initial heuristic estimate
        
        # Calculate various metrics
        variety_score = self._calculate_variety_score(assigned_meals)
        nutrition_score = self._calculate_nutrition_score(assigned_meals)
        cost_score = self._calculate_cost_score(assigned_meals)
        constraint_penalty = self._calculate_constraint_penalty(assigned_meals, preferences)
        
        # Weighted combination (lower is better)
        heuristic = (
            (1.0 - variety_score) * 20 +
            (1.0 - nutrition_score) * 15 +
            cost_score * 10 +
            constraint_penalty * 25
        )
        
        return max(0.0, heuristic)
    
    def _calculate_variety_score(self, assigned_meals: Dict) -> float:
        """Calculate variety score (0-1, higher is better)"""
        if not assigned_meals:
            return 0.0
        
        dishes = list(assigned_meals.values())
        unique_dishes = len(set(dishes))
        total_dishes = len(dishes)
        
        return unique_dishes / max(total_dishes, 1)
    
    def _calculate_nutrition_score(self, assigned_meals: Dict) -> float:
        """Calculate nutritional balance score (0-1, higher is better)"""
        if not assigned_meals:
            return 0.0
        
        # Count vegetarian vs non-vegetarian meals
        veg_count = 0
        total_count = len(assigned_meals)
        
        for dish in assigned_meals.values():
            if self.prolog.is_vegetarian_dish(dish):
                veg_count += 1
        
        # Balanced nutrition (roughly 60% vegetarian)
        ideal_veg_ratio = 0.6
        actual_veg_ratio = veg_count / max(total_count, 1)
        
        # Score based on how close to ideal ratio
        ratio_diff = abs(ideal_veg_ratio - actual_veg_ratio)
        return max(0.0, 1.0 - ratio_diff * 2)
    
    def _calculate_cost_score(self, assigned_meals: Dict) -> float:
        """Calculate cost efficiency score (0-1, lower is better)"""
        if not assigned_meals:
            return 0.0
        
        total_cost = 0
        cost_mapping = {'low': 1, 'medium': 2, 'high': 3}
        
        for dish in assigned_meals.values():
            dish_cost = self.prolog.get_dish_cost(dish)
            total_cost += cost_mapping.get(dish_cost, 2)
        
        # Normalize cost score
        max_possible_cost = len(assigned_meals) * 3
        return total_cost / max(max_possible_cost, 1)
    
    def _calculate_constraint_penalty(self, assigned_meals: Dict, preferences: Dict) -> float:
        """Calculate penalty for constraint violations"""
        penalty = 0.0
        
        vegetarian_days = preferences.get('vegetarian_days', [])
        avoid_ingredients = preferences.get('avoid_ingredients', [])
        
        for (day, meal_type), dish in assigned_meals.items():
            day_name = self._get_day_name(day)
            
            # Vegetarian day violation
            if day_name in vegetarian_days and not self.prolog.is_vegetarian_dish(dish):
                penalty += 5.0
            
            # Avoided ingredient violation
            dish_ingredients = self.prolog.get_dish_ingredients(dish)
            for ingredient in avoid_ingredients:
                if ingredient.lower() in [ing.lower() for ing in dish_ingredients]:
                    penalty += 3.0
        
        return penalty
    
    def _calculate_meal_cost(self, dish: str, assigned_meals: Dict, preferences: Dict) -> float:
        """Calculate cost of adding a specific meal"""
        base_cost = 1.0
        
        # Repetition penalty
        dish_count = sum(1 for d in assigned_meals.values() if d == dish)
        repetition_penalty = dish_count * 2.0
        
        # Cost level penalty
        cost_mapping = {'low': 0.5, 'medium': 1.0, 'high': 2.0}
        dish_cost = self.prolog.get_dish_cost(dish)
        cost_penalty = cost_mapping.get(dish_cost, 1.0)
        
        return base_cost + repetition_penalty + cost_penalty
    
    def _get_state_key(self, state: MealPlanState) -> str:
        """Generate unique key for state"""
        meals_str = '_'.join(f"{k[0]}-{k[1]}-{v}" for k, v in sorted(state.assigned_meals.items()))
        return f"{state.day}_{state.meal_type}_{meals_str}"

    def _complete_plan(self, assigned_meals: Dict, preferences: Dict) -> Dict:
        """Greedily complete any missing assignments to ensure a full 7x4 plan."""
        completed = dict(assigned_meals)
        # Track already used dishes to encourage variety
        used_dishes = set(completed.values())
        for day_idx in range(7):
            day_name = self._get_day_name(day_idx)
            for meal_type in self.meal_types:
                key = (day_idx, meal_type)
                if key in completed:
                    continue
                # get suitable dishes with fallback
                dishes = self.prolog.get_suitable_dishes(day_name, meal_type, preferences)
                random.shuffle(dishes)
                # prefer a dish not already used this week
                selected = None
                for d in dishes:
                    if d not in used_dishes:
                        selected = d
                        break
                if not selected:
                    selected = dishes[0] if dishes else 'idli_sambar'  # safe default
                completed[key] = selected
                used_dishes.add(selected)
        return completed
    
    def _get_day_name(self, day_index: int) -> str:
        """Convert day index to day name"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        return days[day_index % 7]
    
    def _format_meal_plan(self, assigned_meals: Dict) -> Dict:
        """Format meal plan for frontend"""
        meal_plan = {}
        
        for day_idx in range(7):
            day_name = self._get_day_name(day_idx)
            meal_plan[day_name] = {}
            
            for meal_type in self.meal_types:
                meal_key = (day_idx, meal_type)
                dish = assigned_meals.get(meal_key, 'No dish assigned')
                meal_plan[day_name][meal_type] = dish
        
        return meal_plan
    
    def _is_query_cancelled(self, query_id: str) -> bool:
        """Check if query was cancelled"""
        from app import active_queries, query_lock
        with query_lock:
            return query_id in active_queries and active_queries[query_id].get('cancelled', False)

class AOStarMealPlanner:
    """AO* Algorithm implementation for meal planning with multiple objectives"""
    
    def __init__(self, prolog_interface):
        self.prolog = prolog_interface
        self.meal_types = ['breakfast', 'lunch', 'snacks', 'dinner']
        self.search_metrics = {
            'nodes_created': 0,
            'total_time': 0.0,
            'tree_depth': 0
        }
    
    def generate_meal_plan(self, start_date: str, preferences: Dict, query_id: str) -> Optional[Dict]:
        """
        Generate meal plan using AO* algorithm with AND-OR tree
        
        AND nodes: Days that require all meal types
        OR nodes: Meal types that can have alternative dishes
        """
        start_time = time.time()
        self.search_metrics['nodes_created'] = 0
        
        try:
            logger.info(f"Starting AO* meal planning for query {query_id}")
            
            # Create root AND-OR tree
            root_state = {'week_plan': {}, 'current_day': 0}
            root_node = AONode(
                state=root_state,
                node_type='AND',  # Week planning requires all days
                children=[],
                value=float('inf'),
                solved=False
            )
            
            # Build AND-OR tree and solve
            solution = self._ao_star_search(root_node, preferences, query_id)
            
            self.search_metrics['total_time'] = time.time() - start_time
            logger.info(f"AO* completed in {self.search_metrics['total_time']:.2f}s")
            
            if solution:
                return self._extract_meal_plan(solution)
            else:
                return self._generate_fallback_plan(preferences)
                
        except Exception as e:
            logger.error(f"Error in AO* meal planning: {e}")
            return None
    
    def _ao_star_search(self, node: AONode, preferences: Dict, query_id: str) -> Optional[AONode]:
        """Main AO* search algorithm"""
        max_iterations = 1000
        iteration = 0
        
        while not node.solved and iteration < max_iterations:
            iteration += 1
            
            # Check if query was cancelled
            if self._is_query_cancelled(query_id):
                return None
            
            # Expand and evaluate node
            self._expand_node(node, preferences)
            self._update_node_values(node)
            
            # Check if solved
            if self._is_goal_state(node.state):
                node.solved = True
                return node
        
        return node if node.children else None
    
    def _expand_node(self, node: AONode, preferences: Dict):
        """Expand AND-OR node based on type"""
        if node.children:  # Already expanded
            return
        
        self.search_metrics['nodes_created'] += 1
        
        if node.node_type == 'AND':
            # AND node: expand to day planning
            self._expand_and_node(node, preferences)
        else:
            # OR node: expand to meal alternatives
            self._expand_or_node(node, preferences)
    
    def _expand_and_node(self, node: AONode, preferences: Dict):
        """Expand AND node for day planning"""
        current_day = node.state.get('current_day', 0)
        
        if current_day >= 7:  # Week complete
            return
        
        # Create OR node for each meal type of the day
        day_name = self._get_day_name(current_day)
        
        for meal_type in self.meal_types:
            meal_state = {
                'day': current_day,
                'day_name': day_name,
                'meal_type': meal_type,
                'parent_plan': node.state.get('week_plan', {})
            }
            
            or_node = AONode(
                state=meal_state,
                node_type='OR',
                children=[],
                value=float('inf'),
                solved=False
            )
            
            node.children.append(or_node)
    
    def _expand_or_node(self, node: AONode, preferences: Dict):
        """Expand OR node for meal alternatives"""
        day_name = node.state['day_name']
        meal_type = node.state['meal_type']
        
        # Get suitable dishes for this meal slot
        suitable_dishes = self.prolog.get_suitable_dishes(day_name, meal_type, preferences)
        
        for dish in suitable_dishes[:3]:  # Limit alternatives
            dish_state = node.state.copy()
            dish_state['selected_dish'] = dish
            dish_state['dish_cost'] = self._evaluate_dish_cost(dish, node.state, preferences)
            
            # Create child node for next day if this is last meal of day
            if meal_type == 'dinner':
                next_day = node.state['day'] + 1
                child_state = {
                    'week_plan': self._update_plan(node.state['parent_plan'], dish_state),
                    'current_day': next_day
                }
                child_node = AONode(
                    state=child_state,
                    node_type='AND',
                    children=[],
                    value=dish_state['dish_cost'],
                    solved=(next_day >= 7)
                )
            else:
                # Continue with next meal of same day
                child_state = dish_state.copy()
                child_node = AONode(
                    state=child_state,
                    node_type='OR',
                    children=[],
                    value=dish_state['dish_cost'],
                    solved=False
                )
            
            node.children.append(child_node)
    
    def _update_node_values(self, node: AONode):
        """Update node values using minimax with AND-OR semantics"""
        if not node.children:
            return
        
        if node.node_type == 'AND':
            # AND node: sum of all children (all must be satisfied)
            total_value = 0
            all_solved = True
            
            for child in node.children:
                self._update_node_values(child)
                total_value += child.value
                if not child.solved:
                    all_solved = False
            
            node.value = total_value
            node.solved = all_solved
            
        else:
            # OR node: minimum of children (best alternative)
            min_value = float('inf')
            any_solved = False
            
            for child in node.children:
                self._update_node_values(child)
                if child.value < min_value:
                    min_value = child.value
                if child.solved:
                    any_solved = True
            
            node.value = min_value if min_value != float('inf') else 0
            node.solved = any_solved
    
    def _evaluate_dish_cost(self, dish: str, state: Dict, preferences: Dict) -> float:
        """Evaluate cost of selecting a dish"""
        base_cost = 1.0
        
        # Get dish properties
        dish_cost_level = self.prolog.get_dish_cost(dish)
        cost_mapping = {'low': 0.5, 'medium': 1.0, 'high': 2.0}
        cost_penalty = cost_mapping.get(dish_cost_level, 1.0)
        
        # Repetition penalty
        parent_plan = state.get('parent_plan', {})
        repetition_count = 0
        for day_meals in parent_plan.values():
            for meal_dish in day_meals.values():
                if meal_dish == dish:
                    repetition_count += 1
        
        repetition_penalty = repetition_count * 1.5
        
        # Constraint violations
        constraint_penalty = 0
        vegetarian_days = preferences.get('vegetarian_days', [])
        day_name = state.get('day_name', '')
        
        if day_name in vegetarian_days and not self.prolog.is_vegetarian_dish(dish):
            constraint_penalty += 5.0
        
        return base_cost + cost_penalty + repetition_penalty + constraint_penalty
    
    def _update_plan(self, current_plan: Dict, dish_state: Dict) -> Dict:
        """Update meal plan with new dish selection"""
        updated_plan = current_plan.copy()
        day_name = dish_state['day_name']
        meal_type = dish_state['meal_type']
        dish = dish_state['selected_dish']
        
        if day_name not in updated_plan:
            updated_plan[day_name] = {}
        
        updated_plan[day_name][meal_type] = dish
        return updated_plan
    
    def _is_goal_state(self, state: Dict) -> bool:
        """Check if state represents a complete week plan"""
        week_plan = state.get('week_plan', {})
        current_day = state.get('current_day', 0)
        
        return current_day >= 7 and len(week_plan) == 7
    
    def _extract_meal_plan(self, solution_node: AONode) -> Dict:
        """Extract meal plan from solution node"""
        if 'week_plan' in solution_node.state:
            return solution_node.state['week_plan']
        
        # Reconstruct plan from tree structure
        meal_plan = {}
        self._reconstruct_plan(solution_node, meal_plan)
        return meal_plan
    
    def _reconstruct_plan(self, node: AONode, meal_plan: Dict):
        """Recursively reconstruct meal plan from AO* tree"""
        if 'selected_dish' in node.state:
            day_name = node.state['day_name']
            meal_type = node.state['meal_type']
            dish = node.state['selected_dish']
            
            if day_name not in meal_plan:
                meal_plan[day_name] = {}
            meal_plan[day_name][meal_type] = dish
        
        for child in node.children:
            if child.solved:
                self._reconstruct_plan(child, meal_plan)
                break  # For OR nodes, take first solved child
    
    def _generate_fallback_plan(self, preferences: Dict) -> Dict:
        """Generate simple fallback meal plan if AO* fails"""
        meal_plan = {}
        
        for day_idx in range(7):
            day_name = self._get_day_name(day_idx)
            meal_plan[day_name] = {}
            
            for meal_type in self.meal_types:
                dishes = self.prolog.get_suitable_dishes(day_name, meal_type, preferences)
                if dishes:
                    meal_plan[day_name][meal_type] = random.choice(dishes[:3])
                else:
                    meal_plan[day_name][meal_type] = 'No dish available'
        
        return meal_plan
    
    def _get_day_name(self, day_index: int) -> str:
        """Convert day index to day name"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        return days[day_index % 7]
    
    def _is_query_cancelled(self, query_id: str) -> bool:
        """Check if query was cancelled"""
        from app import active_queries, query_lock
        with query_lock:
            return query_id in active_queries and active_queries[query_id].get('cancelled', False)
