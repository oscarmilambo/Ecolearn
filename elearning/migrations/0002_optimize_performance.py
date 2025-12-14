# Generated migration for performance optimizations
from django.db import migrations, models
import cloudinary.models

class Migration(migrations.Migration):

    dependencies = [
        ('elearning', '0001_initial'),
    ]

    operations = [
        # Add database indexes for better query performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_module_published_active ON elearning_module (is_published, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_module_published_active;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_module_category_published ON elearning_module (category_id, is_published);",
            reverse_sql="DROP INDEX IF EXISTS idx_module_category_published;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_module_difficulty_published ON elearning_module (difficulty, is_published);",
            reverse_sql="DROP INDEX IF EXISTS idx_module_difficulty_published;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_module_featured_enrollments ON elearning_module (is_featured, enrollments_count);",
            reverse_sql="DROP INDEX IF EXISTS idx_module_featured_enrollments;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_module_rating_enrollments ON elearning_module (average_rating, enrollments_count);",
            reverse_sql="DROP INDEX IF EXISTS idx_module_rating_enrollments;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_lesson_module_order ON elearning_lesson (module_id, order);",
            reverse_sql="DROP INDEX IF EXISTS idx_lesson_module_order;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_lesson_module_published ON elearning_lesson (module_id, is_published);",
            reverse_sql="DROP INDEX IF EXISTS idx_lesson_module_published;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_category_active_order ON elearning_category (is_active, order);",
            reverse_sql="DROP INDEX IF EXISTS idx_category_active_order;"
        ),
        
        # Add composite indexes for common query patterns
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_enrollment_user_module ON elearning_enrollment (user_id, module_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_enrollment_user_module;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_lesson_progress_enrollment_lesson ON elearning_lessonprogress (enrollment_id, lesson_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_lesson_progress_enrollment_lesson;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_quiz_attempt_user_quiz ON elearning_quizattempt (user_id, quiz_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_quiz_attempt_user_quiz;"
        ),
    ]