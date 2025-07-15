import sqlite3
import os

DATABASE_FILE = "predictions.db"

def populate_db_with_data():
    """Creates the database table if it doesn't exist and populates it with sample data."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Create the table if it doesn't exist (this is also done in app.py's init_db, but safe to repeat)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sign TEXT NOT NULL,
                category TEXT NOT NULL,
                text TEXT NOT NULL
            )
        """)
        conn.commit()
        print("Table 'predictions' ensured to exist.")

        # Sample Data - YOU CAN ADD MORE HERE!
        # Remember to keep sign and category in lowercase
        sample_data = [
            ('aries', 'love', 'A romantic encounter could brighten your day.'),
            ('aries', 'career', 'New challenges bring great rewards at work. Embrace them!'),
            ('aries', 'health', 'Pay attention to your energy levels; a short break could be beneficial.'),
            ('aries', 'finance', 'Unexpected expenses may arise, but you will manage them effectively.'),
            ('aries', 'general', 'A day of new beginnings and exciting opportunities.'),

            ('taurus', 'love', 'Stability and comfort define your romantic outlook today.'),
            ('taurus', 'career', 'Hard work will be recognized. Keep pushing towards your goals.'),
            ('taurus', 'health', 'Focus on nourishing foods and gentle exercise for well-being.'),
            ('taurus', 'finance', 'A good day for reviewing your budget and making sound financial plans.'),
            ('taurus', 'general', 'Patience is your virtue today, leading to positive outcomes.'),

            ('gemini', 'love', 'Communication is key in your relationships today, Gemini.'),
            ('gemini', 'career', 'Networking can open doors to exciting new projects.'),
            ('gemini', 'health', 'Mental clarity is high; use it to plan healthy routines.'),
            ('gemini', 'finance', 'Look for innovative ways to increase your income.'),
            ('gemini', 'general', 'A busy but fulfilling day, full of interesting conversations.'),

            ('cancer', 'love', 'Emotional connections deepen. Cherish moments with loved ones.'),
            ('cancer', 'career', 'Your intuition guides you well in professional decisions.'),
            ('cancer', 'health', 'Listen to your body; rest when needed.'),
            ('cancer', 'finance', 'A good day for home-related financial matters.'),
            ('cancer', 'general', 'A comforting day spent nurturing yourself and others.'),

            ('leo', 'love', 'Your charisma shines, attracting positive romantic attention.'),
            ('leo', 'career', 'Take the lead on a project; your ideas are well-received.'),
            ('leo', 'health', 'Channel your vibrant energy into a new fitness routine.'),
            ('leo', 'finance', 'Opportunities for financial gain may appear; be bold.'),
            ('leo', 'general', 'A day to express yourself creatively and confidently.'),

            ('virgo', 'love', 'Small gestures of affection mean a lot today.'),
            ('virgo', 'career', 'Detail-oriented tasks go smoothly, bringing a sense of accomplishment.'),
            ('virgo', 'health', 'Maintain your routine; consistency brings good results.'),
            ('virgo', 'finance', 'Review your spending habits for greater efficiency.'),
            ('virgo', 'general', 'A productive day, focusing on practical matters and organization.'),

            ('libra', 'love', 'Harmony and balance are key in your relationships.'),
            ('libra', 'career', 'Collaborate with colleagues for mutually beneficial outcomes.'),
            ('libra', 'health', 'Seek balance in your diet and lifestyle.'),
            ('libra', 'finance', 'Negotiations might favor you today.'),
            ('libra', 'general', 'A day for making fair decisions and seeking beauty.'),

            ('scorpio', 'love', 'Deep emotional insights strengthen your bonds.'),
            ('scorpio', 'career', 'Your intense focus helps you achieve significant breakthroughs.'),
            ('scorpio', 'health', 'Address any lingering stress with calming activities.'),
            ('scorpio', 'finance', 'Investigate new avenues for financial growth.'),
            ('scorpio', 'general', 'A day of profound transformations and uncovering truths.'),

            ('sagittarius', 'love', 'Adventure calls in your romantic life; explore new horizons.'),
            ('sagittarius', 'career', 'Learning new skills can significantly boost your career.'),
            ('sagittarius', 'health', 'Embrace outdoor activities to uplift your spirits.'),
            ('sagittarius', 'finance', 'Long-term financial goals look promising.'),
            ('sagittarius', 'general', 'A day filled with optimism, exploration, and new ideas.'),

            ('capricorn', 'love', 'Solidify existing relationships with clear communication.'),
            ('capricorn', 'career', 'Your diligent efforts are paving the way for long-term success.'),
            ('capricorn', 'health', 'Stick to a disciplined routine for optimal well-being.'),
            ('capricorn', 'finance', 'Prudent financial planning will yield positive results.'),
            ('capricorn', 'general', 'A productive day for setting and achieving practical goals.'),

            ('aquarius', 'love', 'Unique connections bring joy to your relationships.'),
            ('aquarius', 'career', 'Innovative ideas are your strength; share them boldly.'),
            ('aquarius', 'health', 'Try unconventional approaches to boost your energy.'),
            ('aquarius', 'finance', 'Look for new technological investments or solutions.'),
            ('aquarius', 'general', 'A day of inspiration, social connections, and fresh perspectives.'),

            ('pisces', 'love', 'Empathy deepens your romantic understanding.'),
            ('pisces', 'career', 'Your creativity is a valuable asset in professional settings.'),
            ('pisces', 'health', 'Tune into your emotional needs for overall balance.'),
            ('pisces', 'finance', 'Trust your intuition regarding financial opportunities.'),
            ('pisces', 'general', 'A dreamy day where imagination leads to unexpected beauty.')
        ]

        # Only insert data if the table is empty to avoid duplicates on rerun
        cursor.execute("SELECT COUNT(*) FROM predictions")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("INSERT INTO predictions (sign, category, text) VALUES (?, ?, ?)", sample_data)
            conn.commit()
            print("Sample data inserted into 'predictions' table.")
        else:
            print("Table 'predictions' already contains data. Skipping sample data insertion.")

    except sqlite3.Error as e:
        print(f"Database operation error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    populate_db_with_data()
    print(f"Database '{DATABASE_FILE}' created/checked and populated with data.")