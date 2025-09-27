import logging
import traceback
import random
from typing import List, Dict, Optional, Any
from pyswip import Prolog
import threading
import time

logger = logging.getLogger(__name__)

class PrologInterface:
    """Interface for interacting with SWI-Prolog knowledge base"""
    
    def __init__(self):
        self.prolog = None
        self.lock = threading.Lock()
        self.query_timeout = 10  # seconds
        self._initialize_prolog()
    
    def _initialize_prolog(self):
        """Initialize Prolog engine and load knowledge base"""
        try:
            with self.lock:
                self.prolog = Prolog()
                
                # Load knowledge base
                self.prolog.consult("kb.pl")
                
                logger.info("Prolog knowledge base loaded successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize Prolog: {e}")
            logger.error(traceback.format_exc())
            self.prolog = None
    
    def _execute_query(self, query: str, timeout: Optional[int] = None) -> List[Dict]:
        """Execute Prolog query with timeout protection"""
        if not self.prolog:
            logger.error("Prolog not initialized")
            return []
        
        timeout = timeout if timeout is not None else self.query_timeout
        results = []
        
        try:
            with self.lock:
                start_time = time.time()
                
                for solution in self.prolog.query(query):
                    results.append(dict(solution))
                    
                    # Check timeout
                    if time.time() - start_time > timeout:
                        logger.warning(f"Query timeout: {query}")
                        break
                        
        except Exception as e:
            logger.error(f"Prolog query error: {e}")
            logger.error(f"Query: {query}")
            logger.error(traceback.format_exc())
            
        return results
    
    def get_all_dishes(self) -> List[Dict]:
        """Get all dishes from knowledge base"""
        try:
            query = "dish(Name, MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost)"
            results = self._execute_query(query)
            
            dishes = []
            for result in results:
                dish = {
                    'name': result.get('Name', ''),
                    'meal_type': result.get('MealType', ''),
                    'ingredients': self._parse_list(result.get('Ingredients', [])),
                    'recipe': result.get('Recipe', ''),
                    'is_vegetarian': self._parse_bool(result.get('IsVeg', False)),
                    'prep_time': result.get('PrepTime', 30),
                    'cost_level': result.get('Cost', 'medium')
                }
                dishes.append(dish)
            
            return dishes
            
        except Exception as e:
            logger.error(f"Error getting all dishes: {e}")
            return []

    def _parse_bool(self, value) -> bool:
        """Normalize Prolog booleans/strings to Python bool"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == 'true'
        return str(value).lower() == 'true'
    
    def get_suitable_dishes(self, day: str, meal_type: str, preferences: Dict) -> List[str]:
        """Get dishes suitable for specific day and meal type"""
        try:
            # Update preferences in Prolog
            self.update_user_preferences(preferences)
            
            # Query for suitable dishes
            query = f"suitable_dish(Dish, {day}, {meal_type})"
            results = self._execute_query(query)
            
            dishes = [result.get('Dish', '') for result in results if result.get('Dish')]
            
            # If no suitable dishes found, get all dishes of meal type as fallback
            if not dishes:
                logger.warning(f"No suitable dishes found for {day} {meal_type}, using fallback")
                fallback_query = f"dish(Dish, {meal_type}, _, _, _, _, _)"
                fallback_results = self._execute_query(fallback_query)
                dishes = [result.get('Dish', '') for result in fallback_results if result.get('Dish')]
            
            return dishes[:10]  # Limit to 10 dishes
            
        except Exception as e:
            logger.error(f"Error getting suitable dishes: {e}")
            return self._get_fallback_dishes(meal_type)
    
    def add_dish(self, name: str, meal_type: str, ingredients: List[str], 
                 recipe: str, is_vegetarian: bool, prep_time: int, cost_level: str) -> bool:
        """Add new dish to knowledge base and persist to kb.pl"""
        try:
            # Format ingredients as Prolog list
            ingredients_str = self._format_prolog_list(ingredients)
            recipe_escaped = recipe.replace("'", "\\'")
            veg_atom = 'true' if is_vegetarian else 'false'
            query = f"add_new_dish('{name}', {meal_type}, {ingredients_str}, '{recipe_escaped}', {veg_atom}, {prep_time}, {cost_level})"
            results = self._execute_query(query)
            if results is not None:
                # Persist to kb.pl
                self._append_dish_to_file(name, meal_type, ingredients, recipe, is_vegetarian, prep_time, cost_level)
                logger.info(f"Successfully added dish: {name}")
                return True
            else:
                logger.error(f"Failed to add dish: {name}")
                return False
        except Exception as e:
            logger.error(f"Error adding dish {name}: {e}")
            return False

    def _append_dish_to_file(self, name, meal_type, ingredients, recipe, is_vegetarian, prep_time, cost_level):
        """Append dish fact to kb.pl file"""
        try:
            kb_path = "kb.pl"
            with open(kb_path, "a", encoding="utf-8") as f:
                ingredients_str = '[' + ', '.join([f"'{ing}'" for ing in ingredients]) + ']'
                recipe_escaped = recipe.replace("'", "\\'")
                veg_atom = 'true' if is_vegetarian else 'false'
                fact = f"dish('{name}', {meal_type}, {ingredients_str}, '{recipe_escaped}', {veg_atom}, {prep_time}, {cost_level}).\n"
                f.write(fact)
        except Exception as e:
            logger.error(f"Error writing dish to kb.pl: {e}")


    def delete_dish(self, name: str) -> bool:
        """Remove a dish from the knowledge base and kb.pl"""
        try:
            query = f"delete_dish('{name}')"
            self._execute_query(query)
            self._remove_dish_from_file(name)
            return True
        except Exception as e:
            logger.error(f"Error deleting dish {name}: {e}")
            return False

    def _remove_dish_from_file(self, name):
        """Remove dish fact from kb.pl file"""
        try:
            kb_path = "kb.pl"
            with open(kb_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(kb_path, "w", encoding="utf-8") as f:
                for line in lines:
                    if not (line.strip().startswith(f"dish('{name}',") or line.strip().startswith(f"dish(\"{name}\",")):
                        f.write(line)
        except Exception as e:
            logger.error(f"Error removing dish from kb.pl: {e}")
    
    def update_user_preferences(self, preferences: Dict):
        """Update user preferences in Prolog"""
        try:
            # Clear existing preferences
            self._execute_query("retractall(user_preference(_, _, _))")
            
            # Add vegetarian days
            vegetarian_days = preferences.get('vegetarian_days', [])
            for day in vegetarian_days:
                query = f"update_preference(vegetarian_day, {day}, true)"
                self._execute_query(query)
            
            # Add avoided ingredients
            avoid_ingredients = preferences.get('avoid_ingredients', [])
            for ingredient in avoid_ingredients:
                query = f"update_preference(avoid_ingredient, '{ingredient}', true)"
                self._execute_query(query)
            
            # Add family size
            family_size = preferences.get('family_size', 4)
            query = f"update_preference(family_size, {family_size}, true)"
            self._execute_query(query)
            
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
    
    def generate_weekly_meal_plan(self, start_date: str, preferences: Dict, query_id: str) -> Optional[Dict]:
        """Generate weekly meal plan using Prolog rules"""
        try:
            self.update_user_preferences(preferences)
            
            # Generate meal plan
            query = f"generate_weekly_plan('{start_date}', [], Plan)"
            results = self._execute_query(query, timeout=15)
            
            if results:
                plan_data = results[0].get('Plan', [])
                return self._parse_meal_plan(plan_data)
            else:
                logger.warning("Prolog meal generation failed, using fallback")
                return self._generate_fallback_meal_plan(preferences)
                
        except Exception as e:
            logger.error(f"Error generating meal plan: {e}")
            return self._generate_fallback_meal_plan(preferences)
    
    def generate_grocery_list(self, meal_plan: Dict) -> List[str]:
        """Generate consolidated grocery list from meal plan"""
        try:
            # Extract all dishes from meal plan
            all_dishes = []
            for day_meals in meal_plan.values():
                for dish in day_meals.values():
                    if dish and dish != 'No dish':
                        all_dishes.append(dish)

            # Aggregate ingredients in Python if Prolog fails
            # Try Prolog first
            dishes_str = self._format_prolog_list(all_dishes)
            query = f"generate_grocery_list({dishes_str}, GroceryList)"
            results = self._execute_query(query)
            if results and 'GroceryList' in results[0]:
                grocery_data = results[0].get('GroceryList', [])
                parsed = self._parse_list(grocery_data)
                if parsed:
                    return parsed

            # Fallback: compute by union of ingredients
            ingredients_set = set()
            for dish in all_dishes:
                try:
                    ings = self.get_dish_ingredients(dish)
                    for ing in ings:
                        ingredients_set.add(ing)
                except Exception:
                    continue
            return sorted(list(ingredients_set)) if ingredients_set else self._generate_fallback_grocery_list(all_dishes)
                
        except Exception as e:
            logger.error(f"Error generating grocery list: {e}")
            return self._generate_fallback_grocery_list([])
    
    def get_dish_details(self, dish_name: str) -> Dict:
        """Get detailed information about a specific dish"""
        try:
            # Use direct query approach for better reliability
            return self._get_dish_info_fallback(dish_name)
                
        except Exception as e:
            logger.error(f"Error getting dish details for {dish_name}: {e}")
            return {'error': 'Failed to get dish details'}
    
    def suggest_alternatives(self, day: str, meal_type: str, current_dish: str, preferences: Dict) -> List[str]:
        """Suggest alternative dishes for a meal slot"""
        try:
            self.update_user_preferences(preferences)
            
            query = f"find_alternatives({day}, {meal_type}, '{current_dish}', Alternatives)"
            results = self._execute_query(query)
            
            if results:
                alternatives_data = results[0].get('Alternatives', [])
                return self._parse_list(alternatives_data)
            else:
                # Fallback: get other dishes of same meal type
                return self.get_suitable_dishes(day, meal_type, preferences)
                
        except Exception as e:
            logger.error(f"Error suggesting alternatives: {e}")
            return []
    
    def is_vegetarian_dish(self, dish_name: str) -> bool:
        """Check if a dish is vegetarian"""
        try:
            query = f"dish('{dish_name}', _, _, _, IsVeg, _, _)"
            results = self._execute_query(query)
            
            if results:
                return results[0].get('IsVeg', False) == 'true'
            return False
            
        except Exception as e:
            logger.error(f"Error checking vegetarian status for {dish_name}: {e}")
            return False
    
    def get_dish_cost(self, dish_name: str) -> str:
        """Get cost level of a dish"""
        try:
            query = f"dish('{dish_name}', _, _, _, _, _, Cost)"
            results = self._execute_query(query)
            
            if results:
                return results[0].get('Cost', 'medium')
            return 'medium'
            
        except Exception as e:
            logger.error(f"Error getting dish cost for {dish_name}: {e}")
            return 'medium'
    
    def get_dish_ingredients(self, dish_name: str) -> List[str]:
        """Get ingredients for a specific dish"""
        try:
            query = f"get_dish_ingredients('{dish_name}', Ingredients)"
            results = self._execute_query(query)
            
            if results:
                ingredients_data = results[0].get('Ingredients', [])
                return self._parse_list(ingredients_data)
            return []
            
        except Exception as e:
            logger.error(f"Error getting ingredients for {dish_name}: {e}")
            return []
    
    def _parse_list(self, prolog_list) -> List[str]:
        """Parse Prolog list to Python list"""
        if isinstance(prolog_list, list):
            return [str(item) for item in prolog_list]
        elif hasattr(prolog_list, '__iter__'):
            return [str(item) for item in prolog_list]
        else:
            return []
    
    def _format_prolog_list(self, python_list: List[str]) -> str:
        """Format Python list as Prolog list"""
        if not python_list:
            return "[]"
        
        formatted_items = [f"'{item}'" for item in python_list]
        return f"[{', '.join(formatted_items)}]"
    
    def _parse_meal_plan(self, plan_data) -> Dict:
        """Parse Prolog meal plan to Python dictionary"""
        try:
            meal_plan = {}
            
            if isinstance(plan_data, list):
                for day_entry in plan_data:
                    if hasattr(day_entry, '__iter__') and len(day_entry) >= 2:
                        day_name = str(day_entry[0])
                        day_meals = day_entry[1]
                        
                        meal_plan[day_name] = {}
                        
                        if isinstance(day_meals, list):
                            for meal_entry in day_meals:
                                if hasattr(meal_entry, '__iter__') and len(meal_entry) >= 2:
                                    meal_type = str(meal_entry[0])
                                    dish = str(meal_entry[1])
                                    meal_plan[day_name][meal_type] = dish
            
            return meal_plan if meal_plan else self._get_default_meal_plan()
            
        except Exception as e:
            logger.error(f"Error parsing meal plan: {e}")
            return self._get_default_meal_plan()
    
    def _parse_dish_details(self, details_data) -> Dict:
        """Parse Prolog dish details to Python dictionary"""
        try:
            details = {}
            
            if isinstance(details_data, list):
                for detail_entry in details_data:
                    if hasattr(detail_entry, '__iter__') and len(detail_entry) >= 2:
                        key = str(detail_entry[0])
                        value = detail_entry[1]
                        
                        if key == 'ingredients':
                            details[key] = self._parse_list(value)
                        elif key == 'vegetarian':
                            details[key] = str(value).lower()
                        else:
                            details[key] = str(value)
            
            return details
            
        except Exception as e:
            logger.error(f"Error parsing dish details: {e}")
            return {}
    
    def _generate_fallback_meal_plan(self, preferences: Dict) -> Dict:
        """Generate fallback meal plan when Prolog fails"""
        fallback_dishes = {
            'breakfast': ['idli_sambar', 'dosa_chutney', 'upma', 'pongal'],
            'lunch': ['sambar_rice', 'rasam_rice', 'curd_rice', 'vegetable_biryani'],
            'snacks': ['medu_vada', 'sundal', 'bajji', 'masala_vada'],
            'dinner': ['chapati_dal', 'fried_rice', 'lemon_rice', 'vegetable_pulao']
        }
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meal_plan = {}
        
        for day in days:
            meal_plan[day] = {}
            for meal_type in ['breakfast', 'lunch', 'snacks', 'dinner']:
                available_dishes = fallback_dishes.get(meal_type, ['No dish'])
                meal_plan[day][meal_type] = random.choice(available_dishes)
        
        return meal_plan
    
    def _generate_fallback_grocery_list(self, dishes: List[str]) -> List[str]:
        """Generate fallback grocery list"""
        common_ingredients = [
            'rice', 'dal', 'onion', 'tomato', 'green_chili', 'ginger',
            'curry_leaves', 'mustard_seeds', 'turmeric', 'oil', 'salt'
        ]
        return common_ingredients
    
    def _get_fallback_dishes(self, meal_type: str) -> List[str]:
        """Get fallback dishes for a meal type"""
        fallback_dishes = {
            'breakfast': ['idli_sambar', 'dosa_chutney', 'upma'],
            'lunch': ['sambar_rice', 'rasam_rice', 'curd_rice'],
            'snacks': ['medu_vada', 'sundal', 'bajji'],
            'dinner': ['chapati_dal', 'fried_rice', 'lemon_rice']
        }
        return fallback_dishes.get(meal_type, ['No dish available'])
    
    def _get_default_meal_plan(self) -> Dict:
        """Get default meal plan structure"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meal_plan = {}
        
        for day in days:
            meal_plan[day] = {
                'breakfast': 'idli_sambar',
                'lunch': 'sambar_rice',
                'snacks': 'sundal',
                'dinner': 'chapati_dal'
            }
        
        return meal_plan
    
    def _get_dish_info_fallback(self, dish_name: str) -> Dict:
        """Fallback method to get dish information directly"""
        try:
            query = f"dish('{dish_name}', MealType, Ingredients, Recipe, IsVeg, PrepTime, Cost)"
            results = self._execute_query(query)
            
            if results and len(results) > 0:
                result = results[0]
                logger.info(f"Raw Prolog result for {dish_name}: {result}")
                
                # Extract and clean the data
                meal_type = str(result.get('MealType', ''))
                ingredients_raw = result.get('Ingredients', [])
                recipe = str(result.get('Recipe', ''))
                is_veg = result.get('IsVeg', False)
                prep_time = result.get('PrepTime', 30)
                cost = str(result.get('Cost', 'medium'))
                
                # Parse ingredients properly
                ingredients = self._parse_list(ingredients_raw)
                
                return {
                    'meal_type': meal_type,
                    'ingredients': ingredients,
                    'recipe': recipe,
                    'vegetarian': str(is_veg).lower(),
                    'prep_time': int(prep_time) if isinstance(prep_time, (int, float)) else 30,
                    'cost_level': cost
                }
            else:
                logger.warning(f"No results found for dish: {dish_name}")
                return {'error': 'Dish not found'}
                
        except Exception as e:
            logger.error(f"Error in fallback dish info for {dish_name}: {e}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            return {'error': 'Failed to get dish details'}
