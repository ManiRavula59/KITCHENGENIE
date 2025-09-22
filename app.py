import os
import logging
import json
import traceback
import threading
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import matplotlib
matplotlib.use('Agg', force=True)  # Use non-interactive backend
import matplotlib.pyplot as plt
plt.ioff()  # Turn off interactive mode
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import time

from prolog_interface import PrologInterface
from algorithms import AStarMealPlanner, AOStarMealPlanner

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

# Global storage for active queries
active_queries = {}
query_lock = threading.Lock()

# Initialize Prolog interface
prolog = PrologInterface()

# Initialize AI algorithms
astar_planner = AStarMealPlanner(prolog)
aostar_planner = AOStarMealPlanner(prolog)

@app.before_request
def before_request():
    """Initialize session variables"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    if 'preferences' not in session:
        session['preferences'] = {
            'vegetarian_days': [],
            'avoid_ingredients': [],
            'preferred_cuisines': [],
            'family_size': 4
        }

@app.route('/')
def index():
    """Main page with meal planner interface"""
    try:
        # Get available dishes from Prolog
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

@app.route('/add_dish', methods=['POST'])
def add_dish():
    """Add a new dish to the knowledge base"""
    try:
        dish_name = request.form.get('dish_name', '').strip()
        meal_type = request.form.get('meal_type', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        recipe = request.form.get('recipe', '').strip()
        is_vegetarian = request.form.get('is_vegetarian') == 'on'
        prep_time = int(request.form.get('prep_time', 30))
        cost_level = request.form.get('cost_level', 'medium')
        
        if not all([dish_name, meal_type, ingredients]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('index'))
        
        # Parse ingredients
        ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
        
        # Add dish to Prolog knowledge base
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

@app.route('/update_preferences', methods=['POST'])
def update_preferences():
    """Update user dietary preferences"""
    try:
        preferences = session.get('preferences', {})
        
        # Parse form data
        vegetarian_days = request.form.getlist('vegetarian_days')
        avoid_ingredients = [ing.strip() for ing in request.form.get('avoid_ingredients', '').split(',') if ing.strip()]
        preferred_cuisines = request.form.getlist('preferred_cuisines')
        family_size = int(request.form.get('family_size', 4))
        
        # Update preferences
        preferences.update({
            'vegetarian_days': vegetarian_days,
            'avoid_ingredients': avoid_ingredients,
            'preferred_cuisines': preferred_cuisines,
            'family_size': family_size
        })
        
        session['preferences'] = preferences
        logger.info(f"Updated preferences: {preferences}")
        
        # Update Prolog facts
        prolog.update_user_preferences(preferences)
        
        flash('Preferences updated successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        flash('Error updating preferences. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/generate_meal_plan', methods=['POST'])
def generate_meal_plan():
    """Generate weekly meal plan using AI algorithms"""
    query_id = str(uuid.uuid4())
    
    try:
        # Combined strategy: try A*, then AO*, then Prolog rules
        start_date = request.form.get('start_date')
        
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        # Cancel any existing query for this user
        user_id = session['user_id']
        with query_lock:
            for qid, query_info in list(active_queries.items()):
                if query_info.get('user_id') == user_id:
                    query_info['cancelled'] = True
                    del active_queries[qid]
        
        # Register new query
        with query_lock:
            active_queries[query_id] = {
                'user_id': user_id,
                'start_time': time.time(),
                'cancelled': False
            }
        
        # Generate meal plan using combined approach
        algorithm = 'combined'
        current_preferences = session.get('preferences', {})
        logger.info(f"Current preferences for meal plan generation: {current_preferences}")
        meal_plan = astar_planner.generate_meal_plan(start_date, current_preferences, query_id)
        if not meal_plan:
            meal_plan = aostar_planner.generate_meal_plan(start_date, session.get('preferences', {}), query_id)
        if not meal_plan:
            meal_plan = prolog.generate_weekly_meal_plan(start_date, session.get('preferences', {}), query_id)
        
        # Check if query was cancelled
        with query_lock:
            if query_id in active_queries and active_queries[query_id].get('cancelled'):
                del active_queries[query_id]
                flash('Meal plan generation was cancelled.', 'info')
                return redirect(url_for('index'))
        
        # Clean up query tracking
        with query_lock:
            if query_id in active_queries:
                del active_queries[query_id]
        
        if meal_plan:
            # Generate grocery list
            grocery_list = prolog.generate_grocery_list(meal_plan)
            
            # Generate visualizations (with fallback if matplotlib fails)
            try:
                visualizations = generate_visualizations(meal_plan, algorithm)
            except Exception as viz_error:
                logger.warning(f"Visualization generation failed: {viz_error}")
                visualizations = {}
            
            session['current_meal_plan'] = meal_plan
            session['current_grocery_list'] = grocery_list
            session['current_visualizations'] = visualizations
            session['algorithm_used'] = algorithm
            
            return redirect(url_for('results'))
        else:
            flash('Unable to generate meal plan. Please try again or add more dishes.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        # Clean up query tracking
        with query_lock:
            if query_id in active_queries:
                del active_queries[query_id]
        
        logger.error(f"Error generating meal plan: {e}")
        logger.error(traceback.format_exc())
        flash('Error generating meal plan. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/cancel_generation', methods=['POST'])
def cancel_generation():
    """Cancel ongoing meal plan generation"""
    try:
        user_id = session['user_id']
        with query_lock:
            for query_id, query_info in list(active_queries.items()):
                if query_info.get('user_id') == user_id:
                    query_info['cancelled'] = True
                    del active_queries[query_id]
        
        flash('Meal plan generation cancelled.', 'info')
    except Exception as e:
        logger.error(f"Error cancelling generation: {e}")
        flash('Error cancelling generation.', 'error')
    
    return redirect(url_for('index'))

@app.route('/results')
def results():
    """Display meal plan results with visualizations"""
    try:
        meal_plan = session.get('current_meal_plan')
        grocery_list = session.get('current_grocery_list', [])
        visualizations = session.get('current_visualizations', {})
        algorithm_used = session.get('algorithm_used', 'basic')
        
        if not meal_plan:
            flash('No meal plan found. Please generate a meal plan first.', 'error')
            return redirect(url_for('index'))
        
        return render_template('results.html',
                             meal_plan=meal_plan,
                             grocery_list=grocery_list,
                             visualizations=visualizations,
                             algorithm_used=algorithm_used)
                             
    except Exception as e:
        logger.error(f"Error displaying results: {e}")
        flash('Error displaying results. Please try generating a new meal plan.', 'error')
        return redirect(url_for('index'))

@app.route('/get_dish_details/<dish_name>')
def get_dish_details(dish_name):
    """Get detailed information about a specific dish"""
    try:
        dish_details = prolog.get_dish_details(dish_name)
        return jsonify(dish_details)
    except Exception as e:
        logger.error(f"Error getting dish details: {e}")
        return jsonify({'error': 'Failed to get dish details'}), 500

@app.route('/delete_dish', methods=['POST'])
def delete_dish():
    """Delete a dish from the knowledge base and redirect to index"""
    try:
        dish_name = request.form.get('dish_name', '').strip()
        if not dish_name:
            return jsonify({'error': 'Dish name required'}), 400
        success = prolog.delete_dish(dish_name)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to delete dish'}), 500
    except Exception as e:
        logger.error(f"Error deleting dish: {e}")
        return jsonify({'error': 'Failed to delete dish'}), 500

@app.route('/suggest_alternatives', methods=['POST'])
def suggest_alternatives():
    """Suggest alternative dishes for a specific meal slot"""
    try:
        day = request.form.get('day')
        meal_type = request.form.get('meal_type')
        current_dish = request.form.get('current_dish')
        
        alternatives = prolog.suggest_alternatives(day or '', meal_type or '', current_dish or '', session.get('preferences', {}))
        
        return jsonify({'alternatives': alternatives})
    except Exception as e:
        logger.error(f"Error suggesting alternatives: {e}")
        return jsonify({'error': 'Failed to suggest alternatives'}), 500

@app.route('/replace_dish', methods=['POST'])
def replace_dish():
    """Replace a dish in the current session meal plan and refresh grocery list"""
    try:
        day = request.form.get('day')
        meal_type = request.form.get('meal_type')
        new_dish = request.form.get('new_dish')

        if not all([day, meal_type, new_dish]):
            return jsonify({'error': 'Invalid parameters'}), 400

        meal_plan = session.get('current_meal_plan', {})
        if day not in meal_plan:
            return jsonify({'error': 'Day not found in current plan'}), 404

        # Update meal plan
        meal_plan[day][meal_type] = new_dish
        session['current_meal_plan'] = meal_plan

        # Regenerate grocery list to reflect change
        grocery_list = prolog.generate_grocery_list(meal_plan)
        session['current_grocery_list'] = grocery_list

        return jsonify({'success': True, 'meal_plan': meal_plan, 'grocery_list': grocery_list})
    except Exception as e:
        logger.error(f"Error replacing dish: {e}")
        return jsonify({'error': 'Failed to replace dish'}), 500

def generate_visualizations(meal_plan, algorithm):
    """Generate matplotlib visualizations for the meal plan"""
    try:
        visualizations = {}
        
        # Simplified visualization generation to avoid matplotlib issues
        logger.info(f"Generating visualizations for {algorithm} algorithm")
        
        # Return empty visualizations for now to avoid matplotlib crashes
        # You can enable these later by installing proper matplotlib backend
        return visualizations
        
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
        try:
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='#1a1a1a', edgecolor='none', pad_inches=0.1)
            buffer.seek(0)
            visualizations['timetable'] = base64.b64encode(buffer.getvalue()).decode()
        except Exception as save_error:
            logger.warning(f"Failed to save timetable visualization: {save_error}")
        finally:
            plt.close()
            buffer.close()
        
        # 2. Meal Type Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        meal_counts = {}
        for day_meals in meal_plan.values():
            for meal_type, dish in day_meals.items():
                if dish != 'No dish':
                    meal_counts[meal_type] = meal_counts.get(meal_type, 0) + 1
        
        if meal_counts:
            ax.pie(list(meal_counts.values()), labels=list(meal_counts.keys()), autopct='%1.1f%%',
                  colors=colors[:len(meal_counts)], startangle=90)
            ax.set_title('Meal Type Distribution', fontsize=14, fontweight='bold')
        
        buffer = BytesIO()
        plt.tight_layout()
        try:
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='#1a1a1a', edgecolor='none', pad_inches=0.1)
            buffer.seek(0)
            visualizations['distribution'] = base64.b64encode(buffer.getvalue()).decode()
        except Exception as save_error:
            logger.warning(f"Failed to save distribution visualization: {save_error}")
        finally:
            plt.close()
            buffer.close()
        
        # 3. Algorithm Performance Metrics (simulated)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Processing time comparison
        algorithms = ['Basic', 'A*', 'AO*']
        times = [2.3, 1.8, 2.1]  # Simulated processing times
        colors_algo = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        bars = ax1.bar(algorithms, times, color=colors_algo, alpha=0.8)
        ax1.set_ylabel('Processing Time (seconds)')
        ax1.set_title('Algorithm Performance Comparison')
        ax1.set_ylim(0, max(times) * 1.2)
        
        # Add value labels on bars
        for bar, time in zip(bars, times):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{time}s', ha='center', va='bottom', fontweight='bold')
        
        # Solution quality metrics
        metrics = ['Variety Score', 'Nutrition Score', 'Cost Efficiency']
        scores = [85, 92, 78]  # Simulated scores
        
        ax2.bar(metrics, scores, color=['#96CEB4', '#FFEAA7', '#DDA0DD'], alpha=0.8)
        ax2.set_ylabel('Score (%)')
        ax2.set_title(f'{algorithm.upper()} Algorithm Quality Metrics')
        ax2.set_ylim(0, 100)
        
        # Add value labels
        for i, score in enumerate(scores):
            ax2.text(i, score + 2, f'{score}%', ha='center', va='bottom', fontweight='bold')
        
        buffer = BytesIO()
        plt.tight_layout()
        try:
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='#1a1a1a', edgecolor='none', pad_inches=0.1)
            buffer.seek(0)
            visualizations['performance'] = base64.b64encode(buffer.getvalue()).decode()
        except Exception as save_error:
            logger.warning(f"Failed to save performance visualization: {save_error}")
        finally:
            plt.close()
            buffer.close()
        
        return visualizations
        
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")
        return {}

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    flash('Page not found.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("Starting AI Smart Kitchen Meal Planner...")
    print("Server will be available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
