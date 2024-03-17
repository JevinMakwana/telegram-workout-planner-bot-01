import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the bot token from the environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# State definitions
AGE, WEIGHT, GENDER, GOAL, WORKOUT_DAYS, WORKOUT_PLACE, END = range(7)

# Define constants
(
    FAT_LOSS,
    MUSCLE_BUILDING,
    SIMPLE_FITNESS,
    HOME,
    GYM,
) = map(chr, range(10, 15))


# Global variable to store user inputs
user_inputs = {}

workout_plans = [
    [
        # 4 days-a-week workout
        [
            # Home workout
            [
                ["Day 1: Full Body",
                    [
                        "1) Bodyweight Squats: 3 sets of 15 reps",
                        "2) Push-ups: 3 sets of 12 reps",
                        "3) Bent-over Dumbbell Rows (using water bottles/weighted-bags): 3 sets of 12 reps",
                        "4) Mountain Climbers: 3 sets of 20 reps (10 per leg)",
                        "5) Plank: 3 sets, hold for 30-45 seconds"
                    ]
                ],
                ["Day 2: HIIT Cardio",
                    [
                        "1) Jumping Jacks: 4 sets of 30 seconds",
                        "2) Burpees: 4 sets of 12 reps",
                        "3) High Knees: 4 sets of 30 seconds",
                        "4) Jump Squats: 4 sets of 15 reps",
                        "5) Bicycle Crunches: 3 sets of 20 reps per side"
                    ]
                ],
                ["Day 3: Upper Body Focus",
                    [
                        "1) Tricep Dips (using a chair or elevated surface): 3 sets of 12 reps",
                        "2) Push-ups (wide grip): 3 sets of 10 reps",
                        "3) Bicep Curls (using water bottles or resistance bands): 3 sets of 12 reps",
                        "4) Superman: 3 sets of 12 reps",
                        "5) Russian Twists: 3 sets of 20 reps (10 per side)"
                    ]
                ],
                ["Day 4: Lower Body Focus",
                    [
                        "1) Lunges: 3 sets of 12 reps per leg",
                        "2) Glute Bridges: 3 sets of 15 reps",
                        "3) Wall Sit: 3 sets, hold for 30-60 seconds",
                        "4) Calf Raises: 3 sets of 15 reps",
                        "5) Leg Raises: 3 sets of 12 reps"
                    ]
                ]
            ],
            # Gym workout
            [
                ["Day 1: Strength Training",
                    [
                        "1) Barbell Squats: 4 sets of 8-10 reps",
                        "2) Bench Press: 4 sets of 8-10 reps",
                        "3) Bent-over Barbell Rows: 4 sets of 8-10 reps",
                        "4) Dumbbell Shoulder Press: 3 sets of 10 reps",
                        "5) Plank: 3 sets, hold for 45-60 seconds"
                    ]
                ],
                ["Day 2: HIIT Cardio",
                    [
                        "1) Treadmill Sprints: 8 sets of 30 seconds sprint, 60 seconds rest",
                        "2) Rowing Machine: 4 sets of 250 meters with 1-minute rest between sets",
                        "3) Battle Ropes: 4 sets of 30 seconds",
                        "4) Jump Rope: 4 sets of 1 minute",
                        "5) Bicycle Crunches: 3 sets of 20 reps per side"
                    ]
                ],
                ["Day 3: Upper Body Focus",
                    [
                        "1) Lat Pulldowns: 4 sets of 10 reps",
                        "2) Cable Chest Flyes: 3 sets of 12 reps",
                        "3) Dumbbell Shoulder Press: 3 sets of 10 reps",
                        "4) Tricep Rope Pushdowns: 3 sets of 12 reps",
                        "5) Russian Twists: 3 sets of 20 reps (10 per side)"
                    ]
                ],
                ["Day 4: Lower Body Focus",
                    [
                        "1) Deadlifts: 4 sets of 8-10 reps",
                        "2) Leg Press: 4 sets of 10 reps",
                        "3) Leg Curls: 3 sets of 12 reps",
                        "4) Standing Calf Raises: 3 sets of 15 reps",
                        "5) Plank: 3 sets, hold for 45-60 seconds"
                    ]
                ]
            ]
        ]
    ],
    [
        # 5 days-a-week workout
        [
            # Home workout
            [
                ["Day 1: Full Body Strength",
                    [
                        "1) Bodyweight Squats: 4 sets of 15 reps",
                        "2) Push-ups: 4 sets of 12 reps",
                        "3) Bent-over Dumbbell Rows (using water bottles or other improvised weights): 4 sets of 12 reps",
                        "4) Plank: 3 sets, hold for 45-60 seconds",
                        "5) Jumping Jacks: 3 sets of 1 minute"
                    ]
                ],
                ["Day 2: HIIT Cardio",
                    [
                        "1) Burpees: 5 sets of 12 reps",
                        "2) Mountain Climbers: 4 sets of 20 reps (10 per leg)",
                        "3) High Knees: 4 sets of 30 seconds",
                        "4) Jump Squats: 4 sets of 15 reps",
                        "5) Bicycle Crunches: 3 sets of 20 reps per side"
                    ]
                ],
                ["Day 3: Upper Body Focus",
                    [
                        "1) Tricep Dips (using a chair or elevated surface): 4 sets of 12 reps",
                        "2) Push-ups (wide grip): 4 sets of 10 reps",
                        "3) Bicep Curls (using water bottles or resistance bands): 4 sets of 12 reps",
                        "4) Superman: 3 sets of 15 reps",
                        "5) Russian Twists: 3 sets of 20 reps (10 per side)"
                    ]
                ],
                ["Day 4: Lower Body Strength",
                    [
                        "1) Lunges: 4 sets of 12 reps per leg",
                        "2) Glute Bridges: 4 sets of 15 reps",
                        "3) Wall Sit: 3 sets, hold for 45-60 seconds",
                        "4) Calf Raises: 3 sets of 15 reps",
                        "5) Leg Raises: 3 sets of 12 reps"
                    ]
                ],
                ["Day 5: Core and Cardio",
                    [
                        "1) Plank: 4 sets, hold for 60 seconds",
                        "2) Russian Twists: 4 sets of 20 reps (10 per side)",
                        "3) Jumping Jacks: 4 sets of 1 minute",
                        "4) Bicycle Crunches: 4 sets of 20 reps per side",
                        "5) Mountain Climbers: 3 sets of 30 seconds"
                    ]
                ]
            ],
            # Gym workout
            [
                ["Day 1: Full Body Strength",
                    [
                        "1) Barbell Squats: 4 sets of 8-10 reps",
                        "2) Bench Press: 4 sets of 8-10 reps",
                        "3) Bent-over Barbell Rows: 4 sets of 8-10 reps",
                        "4) Dumbbell Shoulder Press: 3 sets of 10 reps",
                        "5) Plank: 3 sets, hold for 45-60 seconds"
                    ]
                ],
                ["Day 2: HIIT Cardio",
                    [
                        "1) Treadmill Sprints: 8 sets of 30 seconds sprint, 60 seconds rest",
                        "2) Rowing Machine: 4 sets of 250 meters with 1-minute rest between sets",
                        "3) Battle Ropes: 4 sets of 30 seconds",
                        "4) Jump Rope: 4 sets of 1 minute",
                        "5) Bicycle Crunches: 3 sets of 20 reps per side"
                    ]
                ],
                ["Day 3: Upper Body Focus",
                    [
                        "1) Lat Pulldowns: 4 sets of 10 reps",
                        "2) Cable Chest Flyes: 3 sets of 12 reps",
                        "3) Dumbbell Shoulder Press: 3 sets of 10 reps",
                        "4) Tricep Rope Pushdowns: 3 sets of 12 reps",
                        "5) Russian Twists: 3 sets of 20 reps (10 per side)"
                    ]
                ],
                ["Day 4: Lower Body Strength",
                    [
                        "1) Deadlifts: 4 sets of 8-10 reps",
                        "2) Leg Press: 4 sets of 10 reps",
                        "3) Leg Curls: 3 sets of 12 reps",
                        "4) Standing Calf Raises: 3 sets of 15 reps",
                        "5) Plank: 3 sets, hold for 45-60 seconds"
                    ]
                ],
                ["Day 5: Core and Cardio",
                    [
                        "1) Plank: 4 sets, hold for 60 seconds",
                        "2) Russian Twists: 4 sets of 20 reps (10 per side)",
                        "3) Jumping Jacks: 4 sets of 1 minute",
                        "4) Bicycle Crunches: 4 sets of 20 reps per side",
                        "5) Mountain Climbers: 3 sets of 30 seconds"
                    ]
                ]
            ]
        ]
    ],
    [
        # 6 days-a-week workout
        [
            # Home workout
            [
                ["Day 1: Full Body Strength",
                    [
                        "1) Bodyweight Squats: 4 sets of 15 reps",
                        "2) Push-ups: 4 sets of 12 reps",
                        "3) Bent-over Dumbbell Rows (using water bottles or other improvised weights): 4 sets of 12 reps",
                        "4) Plank: 3 sets, hold for 45-60 seconds",
                        "5) Jumping Jacks: 3 sets of 1 minute",
                        "6) Active Recovery"
                    ]
                ],
                ["Day 2: HIIT Cardio",
                    [
                        "1) Burpees: 5 sets of 12 reps",
                        "2) Mountain Climbers: 4 sets of 20 reps (10 per leg)",
                        "3) High Knees: 4 sets of 30 seconds",
                        "4) Jump Squats: 4 sets of 15 reps",
                        "5) Bicycle Crunches: 3 sets of 20 reps per side"
                    ]
                ],
                ["Day 3: Upper Body Focus",
                    [
                        "1) Tricep Dips (using a chair or elevated surface): 4 sets of 12 reps",
                        "2) Push-ups (wide grip): 4 sets of 10 reps",
                        "3) Bicep Curls (using water bottles or resistance bands): 4 sets of 12 reps",
                        "4) Superman: 3 sets of 15 reps",
                        "5) Russian Twists: 3 sets of 20 reps (10 per side)"
                    ]
                ],
                ["Day 4: Lower Body Strength",
                    [
                        "1) Lunges: 4 sets of 12 reps per leg",
                        "2) Glute Bridges: 4 sets of 15 reps",
                        "3) Wall Sit: 3 sets, hold for 45-60 seconds",
                        "4) Calf Raises: 3 sets of 15 reps",
                        "5) Leg Raises: 3 sets of 12 reps"
                    ]
                ],
                ["Day 5: Core and Cardio",
                    [
                        "1) Plank: 4 sets, hold for 60 seconds",
                        "2) Russian Twists: 4 sets of 20 reps (10 per side)",
                        "3) Jumping Jacks: 4 sets of 1 minute",
                        "4) Bicycle Crunches: 4 sets of 20 reps per side",
                        "5) Mountain Climbers: 3 sets of 30 seconds"
                    ]
                ],
                ["Day 6: Active Recovery",
                    [
                        "1) Walking or Jogging: 30-45 minutes at a moderate pace",
                        "2) Yoga or Stretching: 20-30 minutes focusing on flexibility and mobility"
                    ]
                ]
            ],
            # Gym workout
            [
                ["Day 1: Full Body Strength",
                    [
                        "1) Barbell Squats: 4 sets of 8-10 reps",
                        "2) Bench Press: 4 sets of 8-10 reps",
                        "3) Bent-over Barbell Rows: 4 sets of 8-10 reps",
                        "4) Dumbbell Shoulder Press: 3 sets of 10 reps",
                        "5) Plank: 3 sets, hold for 45-60 seconds",
                        "6) Active Recovery"
                    ]
                ],
                ["Day 2: HIIT Cardio",
                    [
                        "1) Treadmill Sprints: 8 sets of 30 seconds sprint, 60 seconds rest",
                        "2) Rowing Machine: 4 sets of 250 meters with 1-minute rest between sets",
                        "3) Battle Ropes: 4 sets of 30 seconds",
                        "4) Jump Rope: 4 sets of 1 minute",
                        "5) Bicycle Crunches: 3 sets of 20 reps per side"
                    ]
                ],
                ["Day 3: Upper Body Focus",
                    [
                        "1) Lat Pulldowns: 4 sets of 10 reps",
                        "2) Cable Chest Flyes: 3 sets of 12 reps",
                        "3) Dumbbell Shoulder Press: 3 sets of 10 reps",
                        "4) Tricep Rope Pushdowns: 3 sets of 12 reps",
                        "5) Russian Twists: 3 sets of 20 reps (10 per side)"
                    ]
                ],
                ["Day 4: Lower Body Strength",
                    [
                        "1) Deadlifts: 4 sets of 8-10 reps",
                        "2) Leg Press: 4 sets of 10 reps",
                        "3) Leg Curls: 3 sets of 12 reps",
                        "4) Standing Calf Raises: 3 sets of 15 reps",
                        "5) Plank: 3 sets, hold for 45-60 seconds"
                    ]
                ],
                ["Day 5: Core and Cardio",
                    [
                        "1) Plank: 4 sets, hold for 60 seconds",
                        "2) Russian Twists: 4 sets of 20 reps (10 per side)",
                        "3) Jumping Jacks: 4 sets of 1 minute",
                        "4) Bicycle Crunches: 4 sets of 20 reps per side",
                        "5) Mountain Climbers: 3 sets of 30 seconds"
                    ]
                ],
                ["Day 6: Active Recovery",
                    [
                        "1) Walking or Jogging: 30-45 minutes at a moderate pace",
                        "2) Yoga or Stretching: 20-30 minutes focusing on flexibility and mobility"
                    ]
                ]
            ]
        ]
    ]
]


# Helper function to generate workout plan
def generate_workout_plan():
    age = int(user_inputs.get(AGE))
    weight = int(user_inputs.get(WEIGHT))
    gender = user_inputs.get(GENDER)
    goal = user_inputs.get(GOAL)
    workout_days = int(user_inputs.get(WORKOUT_DAYS))
    workout_place = user_inputs.get(WORKOUT_PLACE)
    # Check if the user is under 18 years old
    if age < 18:
        return "You should consult with a health professional for exercise because you are under 18."
    
    # Determine the index of the workout plan based on workout days and workout place
    if workout_days == 4:
        plan_index = 0
    elif workout_days == 5:
        plan_index = 1
    elif workout_days == 6:
        plan_index = 2
    else:
        return "Invalid number of workout days. Please choose 4, 5, or 6."
    
    if workout_place == "Home":
        workout_plan = workout_plans[plan_index][0][0]  # Access home workout plan
    elif workout_place == "Gym":
        workout_plan = workout_plans[plan_index][0][1]  # Access gym workout plan


    
    # Construct the workout plan message
    plan_message = f"Workout plan for {workout_days} days a week at {workout_place}:\n"
    for category, exercises in workout_plan:
        plan_message += f"\n{category}:\n"
        for exercise in exercises:
            plan_message += f"{exercise}\n"
    
    return plan_message

# Callback functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start conversation and ask for age."""
    text = "Welcome to the Workout Plan Bot!\nPlease provide your age."
    await update.message.reply_text(text)
    return AGE


async def ask_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for weight."""
    user_inputs[AGE] = update.message.text  # Store user input
    text = "Great! Now, please provide your weight in kilograms."
    await update.message.reply_text(text)
    return WEIGHT


async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for gender."""
    user_inputs[WEIGHT] = update.message.text  # Store user input
    text = "Please provide your gender (Male/Female):"
    await update.message.reply_text(text)
    return GENDER


async def ask_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for workout goal."""
    user_inputs[GENDER] = update.message.text  # Store user input
    text = (
        "Select your workout goal:\n"
        "1. Fat Loss\n"
        "2. Muscle Building\n"
        "3. Simple Fitness"
    )
    await update.message.reply_text(text)
    return GOAL


async def ask_workout_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for number of workout days."""
    user_inputs[GOAL] = update.message.text  # Store user input
    text = "How many days a week do you want to workout?"
    await update.message.reply_text(text)
    return WORKOUT_DAYS


async def ask_workout_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for workout place and generate workout plan."""
    user_inputs[WORKOUT_DAYS] = update.message.text  # Store user input
    text = "Where do you prefer to workout? (Home/Gym)"
    await update.message.reply_text(text)
    return WORKOUT_PLACE


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation."""
    user_inputs[WORKOUT_PLACE] = update.message.text  # Store user input
    workout_plan = generate_workout_plan()  # Generate workout plan
    await update.message.reply_text(workout_plan)  # Send workout plan to the user
    text = "Thank you for using the Workout Plan Bot!"
    await update.message.reply_text(text)
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weight)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_goal)],
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_workout_days)],
            WORKOUT_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_workout_place)],
            WORKOUT_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, end)],
        },
        fallbacks=[CommandHandler("end", end)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()