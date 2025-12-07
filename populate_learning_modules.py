#!/usr/bin/env python
"""
Script to populate the EcoLearn platform with comprehensive e-learning modules
on waste segregation, recycling, and sustainable disposal practices.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from elearning.models import Category, Module, Lesson, Quiz, Question, Answer

def create_categories():
    """Create learning categories for waste management topics."""
    categories_data = [
        {
            'name': 'Waste Segregation',
            'name_bem': 'Ukugawanya Ubwafya',
            'name_ny': 'Kugawa Zinyalala',
            'description': 'Learn how to properly separate different types of waste for effective management.',
            'description_bem': 'Ukufunda ukugawanya ubwafya bwakufyafya ukulenga ukutontonkanya kwa bwino.',
            'description_ny': 'Phunzirani momwe mungagawe zinyalala zosiyanasiyana kuti muziziyang\'anira bwino.'
        },
        {
            'name': 'Recycling Techniques',
            'name_bem': 'Imilimo ya Ukusebenzeshafye',
            'name_ny': 'Njira za Kubwezeretsanso',
            'description': 'Master the art of converting waste materials into new, useful products.',
            'description_bem': 'Ukufunda ukusandula ubwafya mu fintu fipya ifya kufwailisha.',
            'description_ny': 'Phunzirani momwe mungasandulire zinyalala kukhala zinthu zatsopano zothandiza.'
        },
        {
            'name': 'Sustainable Disposal',
            'name_bem': 'Ukutaya Ubwafya mu Mufyashiko Uwa Kutamafye',
            'name_ny': 'Kutaya Zinyalala Mwanjira Yabwino',
            'description': 'Explore environmentally friendly methods for disposing of waste materials.',
            'description_bem': 'Ukufunda imilimo ya kutaya ubwafya iyakufwailisha ku chialo.',
            'description_ny': 'Phunzirani njira zabwino za kutaya zinyalala zomwe siziwononga chilengedwe.'
        },
        {
            'name': 'Community Action',
            'name_bem': 'Imilimo ya Mu Mushi',
            'name_ny': 'Zochita za M\'mudzi',
            'description': 'Learn how to organize and participate in community environmental initiatives.',
            'description_bem': 'Ukufunda ukulonga no kushitakisha mu milimo ya chialo ya mu mushi.',
            'description_ny': 'Phunzirani momwe mungakonzere ndi kutenga nawo mbali mu zochita za chilengedwe m\'mudzi.'
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    return categories

def create_waste_segregation_modules(category):
    """Create comprehensive waste segregation modules."""
    modules_data = [
        {
            'title': 'Introduction to Waste Segregation',
            'title_bem': 'Ukwingila mu Kugawanya Ubwafya',
            'title_ny': 'Chiyambi cha Kugawa Zinyalala',
            'description': 'Learn the basics of waste segregation and why it\'s crucial for environmental protection.',
            'description_bem': 'Ukufunda ifyabukankala fya kugawanya ubwafya nangula cifukwa ca kufwailisha ku chialo.',
            'description_ny': 'Phunzirani zoyambira za kugawa zinyalala ndi chifukwa chake ndichofunikira kuteteza chilengedwe.',
            'difficulty': 'beginner',
            'duration_minutes': 30,
            'points_reward': 50,
            'order': 1
        },
        {
            'title': 'Types of Waste Materials',
            'title_bem': 'Imitundu ya Ubwafya',
            'title_ny': 'Mitundu ya Zinyalala',
            'description': 'Identify different types of waste materials and their proper classification.',
            'description_bem': 'Ukumanya imitundu yakufyafya ya ubwafya no kugawanya kwabo kwa bwino.',
            'description_ny': 'Dziwani mitundu yosiyanasiyana ya zinyalala ndi momwe mungaziike m\'magulu.',
            'difficulty': 'beginner',
            'duration_minutes': 45,
            'points_reward': 75,
            'order': 2
        },
        {
            'title': 'Practical Segregation Techniques',
            'title_bem': 'Imilimo ya Kugawanya Ubwafya mu Chibombelo',
            'title_ny': 'Njira Zenizeni za Kugawa Zinyalala',
            'description': 'Master hands-on techniques for effective waste segregation at home and workplace.',
            'description_bem': 'Ukufunda imilimo ya kugawanya ubwafya mu ng\'anda naku ncito.',
            'description_ny': 'Phunzirani njira zenizeni za kugawa zinyalala bwino kunyumba ndi ku ntchito.',
            'difficulty': 'intermediate',
            'duration_minutes': 60,
            'points_reward': 100,
            'order': 3
        }
    ]
    
    modules = []
    for mod_data in modules_data:
        mod_data['category'] = category
        module, created = Module.objects.get_or_create(
            title=mod_data['title'],
            category=category,
            defaults=mod_data
        )
        modules.append(module)
        if created:
            print(f"Created module: {module.title}")
    
    return modules

def create_recycling_modules(category):
    """Create comprehensive recycling modules."""
    modules_data = [
        {
            'title': 'Fundamentals of Recycling',
            'title_bem': 'Ifyabukankala fya Ukusebenzeshafye',
            'title_ny': 'Maziko a Kubwezeretsanso',
            'description': 'Understand the recycling process and its environmental benefits.',
            'description_bem': 'Ukumanya ukulandila kwa ukusebenzeshafye no kufwailisha kwakwe ku chialo.',
            'description_ny': 'Mvetsetsani njira ya kubwezeretsanso ndi ubwino wake ku chilengedwe.',
            'difficulty': 'beginner',
            'duration_minutes': 40,
            'points_reward': 60,
            'order': 1
        },
        {
            'title': 'Plastic Recycling Methods',
            'title_bem': 'Imilimo ya Ukusebenzeshafye Ama-plastic',
            'title_ny': 'Njira za Kubwezeretsanso Pulasitiki',
            'description': 'Learn specific techniques for recycling different types of plastic materials.',
            'description_bem': 'Ukufunda imilimo yakufyafya ya ukusebenzeshafye ama-plastic yakufyafya.',
            'description_ny': 'Phunzirani njira zapadera za kubwezeretsanso mitundu yosiyanasiyana ya pulasitiki.',
            'difficulty': 'intermediate',
            'duration_minutes': 50,
            'points_reward': 80,
            'order': 2
        },
        {
            'title': 'Paper and Cardboard Recycling',
            'title_bem': 'Ukusebenzeshafye Amapepa na Cardboard',
            'title_ny': 'Kubwezeretsanso Mapepala ndi Cardboard',
            'description': 'Master the process of recycling paper products and cardboard materials.',
            'description_bem': 'Ukufunda ukulandila kwa ukusebenzeshafye amapepa na cardboard.',
            'description_ny': 'Phunzirani njira ya kubwezeretsanso mapepala ndi cardboard.',
            'difficulty': 'intermediate',
            'duration_minutes': 45,
            'points_reward': 75,
            'order': 3
        },
        {
            'title': 'Metal and Glass Recycling',
            'title_bem': 'Ukusebenzeshafye Ichuma na Glass',
            'title_ny': 'Kubwezeretsanso Zitsulo ndi Galasi',
            'description': 'Learn advanced techniques for recycling metal and glass materials.',
            'description_bem': 'Ukufunda imilimo yakutalika ya ukusebenzeshafye ichuma na glass.',
            'description_ny': 'Phunzirani njira zapamwamba za kubwezeretsanso zitsulo ndi galasi.',
            'difficulty': 'advanced',
            'duration_minutes': 55,
            'points_reward': 90,
            'order': 4
        }
    ]
    
    modules = []
    for mod_data in modules_data:
        mod_data['category'] = category
        module, created = Module.objects.get_or_create(
            title=mod_data['title'],
            category=category,
            defaults=mod_data
        )
        modules.append(module)
        if created:
            print(f"Created module: {module.title}")
    
    return modules

def create_sustainable_disposal_modules(category):
    """Create sustainable disposal practice modules."""
    modules_data = [
        {
            'title': 'Composting and Organic Waste',
            'title_bem': 'Ukupanga Compost na Ubwafya bwa Fyakufyala',
            'title_ny': 'Kupanga Compost ndi Zinyalala za Chilengedwe',
            'description': 'Learn how to convert organic waste into valuable compost for gardening.',
            'description_bem': 'Ukufunda ukusandula ubwafya bwa fyakufyala mu compost yakufwailisha ku munda.',
            'description_ny': 'Phunzirani momwe mungasandulire zinyalala za chilengedwe kukhala compost yothandiza ku munda.',
            'difficulty': 'beginner',
            'duration_minutes': 35,
            'points_reward': 55,
            'order': 1
        },
        {
            'title': 'Hazardous Waste Management',
            'title_bem': 'Ukutontonkanya Ubwafya bwa Bwafya',
            'title_ny': 'Kuyang\'anira Zinyalala Zoopsa',
            'description': 'Safely handle and dispose of hazardous materials to protect health and environment.',
            'description_bem': 'Ukutontonkanya ubwafya bwa bwafya mu mufyashiko wa chiteko ku moyo na chialo.',
            'description_ny': 'Gwirani ndi kutaya zinyalala zoopsa mwachitetezo kuti muteteze umoyo ndi chilengedwe.',
            'difficulty': 'advanced',
            'duration_minutes': 50,
            'points_reward': 85,
            'order': 2
        },
        {
            'title': 'E-waste and Electronics Disposal',
            'title_bem': 'Ukutaya E-waste na Ma-electronics',
            'title_ny': 'Kutaya E-waste ndi Ma-electronics',
            'description': 'Proper methods for disposing of electronic devices and e-waste materials.',
            'description_bem': 'Imilimo ya bwino ya kutaya ama-electronics na e-waste.',
            'description_ny': 'Njira zabwino za kutaya zipangizo za magetsi ndi e-waste.',
            'difficulty': 'intermediate',
            'duration_minutes': 40,
            'points_reward': 70,
            'order': 3
        }
    ]
    
    modules = []
    for mod_data in modules_data:
        mod_data['category'] = category
        module, created = Module.objects.get_or_create(
            title=mod_data['title'],
            category=category,
            defaults=mod_data
        )
        modules.append(module)
        if created:
            print(f"Created module: {module.title}")
    
    return modules

def create_community_action_modules(category):
    """Create community action modules."""
    modules_data = [
        {
            'title': 'Organizing Community Cleanups',
            'title_bem': 'Ukulonga Ukusuka kwa Mushi',
            'title_ny': 'Kukonza Kuyeretsa kwa Mudzi',
            'description': 'Learn how to organize and lead effective community cleanup initiatives.',
            'description_bem': 'Ukufunda ukulonga no kutongosha imilimo ya ukusuka mu mushi.',
            'description_ny': 'Phunzirani momwe mungakonzere ndi kutsogolera zochita za kuyeretsa mudzi.',
            'difficulty': 'intermediate',
            'duration_minutes': 45,
            'points_reward': 75,
            'order': 1
        },
        {
            'title': 'Environmental Education Campaigns',
            'title_bem': 'Imilimo ya Ukufundisha pa Chialo',
            'title_ny': 'Zochita za Kuphunzitsa za Chilengedwe',
            'description': 'Design and implement educational campaigns about environmental protection.',
            'description_bem': 'Ukupanga no kushitikisha imilimo ya ukufundisha pa chiteko ca chialo.',
            'description_ny': 'Konzani ndi kukhazikitsa zochita za kuphunzitsa za kuteteza chilengedwe.',
            'difficulty': 'advanced',
            'duration_minutes': 60,
            'points_reward': 95,
            'order': 2
        }
    ]
    
    modules = []
    for mod_data in modules_data:
        mod_data['category'] = category
        module, created = Module.objects.get_or_create(
            title=mod_data['title'],
            category=category,
            defaults=mod_data
        )
        modules.append(module)
        if created:
            print(f"Created module: {module.title}")
    
    return modules

def create_lessons_for_module(module, lessons_data):
    """Create lessons for a specific module."""
    for lesson_data in lessons_data:
        lesson_data['module'] = module
        lesson, created = Lesson.objects.get_or_create(
            title=lesson_data['title'],
            module=module,
            defaults=lesson_data
        )
        if created:
            print(f"  Created lesson: {lesson.title}")
        
        # Create quiz if lesson is quiz type
        if lesson.content_type == 'quiz' and created:
            create_quiz_for_lesson(lesson)

def create_quiz_for_lesson(lesson):
    """Create quiz and questions for a lesson."""
    quiz_data = {
        'title': f"Quiz: {lesson.title}",
        'title_bem': f"Quiz: {lesson.title_bem}",
        'title_ny': f"Quiz: {lesson.title_ny}",
        'description': "Test your knowledge from this lesson.",
        'description_bem': "Ukuipima imyeyo yakufunda mu lesson iyi.",
        'description_ny': "Yesani chidziwitso chanu kuchokera mu phunziro lino.",
        'pass_percentage': 70,
        'max_attempts': 3
    }
    
    quiz, created = Quiz.objects.get_or_create(
        lesson=lesson,
        defaults=quiz_data
    )
    
    if created:
        print(f"    Created quiz: {quiz.title}")
        # Add sample questions based on lesson content
        create_sample_questions(quiz, lesson)

def create_sample_questions(quiz, lesson):
    """Create sample questions for quizzes."""
    if "segregation" in lesson.title.lower():
        questions_data = [
            {
                'question_text': "What are the main categories of waste segregation?",
                'question_text_bem': "Ni imitundu iyapi iyakufunikisha ya kugawanya ubwafya?",
                'question_text_ny': "Ndi magulu anji aakulu a kugawa zinyalala?",
                'question_type': 'multiple_choice',
                'points': 2,
                'order': 1,
                'answers': [
                    {'answer_text': 'Organic, Recyclable, Hazardous, General', 'is_correct': True},
                    {'answer_text': 'Wet, Dry, Mixed', 'is_correct': False},
                    {'answer_text': 'Big, Small, Medium', 'is_correct': False},
                    {'answer_text': 'Clean, Dirty, Broken', 'is_correct': False}
                ]
            },
            {
                'question_text': "Why is waste segregation important for the environment?",
                'question_text_bem': "Nangula cifukwa ca kugawanya ubwafya cakufwailisha ku chialo?",
                'question_text_ny': "Ndi chifukwa chiyani kugawa zinyalala ndikofunikira ku chilengedwe?",
                'question_type': 'multiple_choice',
                'points': 2,
                'order': 2,
                'answers': [
                    {'answer_text': 'Reduces pollution and enables recycling', 'is_correct': True},
                    {'answer_text': 'Makes waste look organized', 'is_correct': False},
                    {'answer_text': 'Saves storage space only', 'is_correct': False},
                    {'answer_text': 'No real benefit', 'is_correct': False}
                ]
            }
        ]
    elif "recycling" in lesson.title.lower():
        questions_data = [
            {
                'question_text': "Which materials can be recycled multiple times?",
                'question_text_bem': "Ni fintu fyapi ifyo fingasebenzeshwa kabhili-bhili?",
                'question_text_ny': "Ndi zinthu ziti zomwe zingabwerezeretsedwe kangapo?",
                'question_type': 'multiple_choice',
                'points': 2,
                'order': 1,
                'answers': [
                    {'answer_text': 'Glass and metal', 'is_correct': True},
                    {'answer_text': 'Paper only', 'is_correct': False},
                    {'answer_text': 'Plastic only', 'is_correct': False},
                    {'answer_text': 'Food waste', 'is_correct': False}
                ]
            }
        ]
    else:
        questions_data = [
            {
                'question_text': "What is the most important principle of sustainable waste disposal?",
                'question_text_bem': "Ni cani icakufunikisha sana mu kutaya ubwafya mu mufyashiko wa kutamafye?",
                'question_text_ny': "Ndi chiyani chofunikira kwambiri pa kutaya zinyalala mwanjira yabwino?",
                'question_type': 'multiple_choice',
                'points': 2,
                'order': 1,
                'answers': [
                    {'answer_text': 'Minimize environmental impact', 'is_correct': True},
                    {'answer_text': 'Dispose quickly', 'is_correct': False},
                    {'answer_text': 'Use any available method', 'is_correct': False},
                    {'answer_text': 'Ignore disposal guidelines', 'is_correct': False}
                ]
            }
        ]
    
    for q_data in questions_data:
        answers_data = q_data.pop('answers')
        question, created = Question.objects.get_or_create(
            quiz=quiz,
            question_text=q_data['question_text'],
            defaults=q_data
        )
        
        if created:
            print(f"      Created question: {question.question_text[:50]}...")
            
            # Create answers
            for ans_data in answers_data:
                ans_data['question'] = question
                Answer.objects.create(**ans_data)

def populate_comprehensive_lessons():
    """Create comprehensive lessons for all modules."""
    
    # Get all modules
    modules = Module.objects.all()
    
    for module in modules:
        if "Introduction to Waste Segregation" in module.title:
            lessons_data = [
                {
                    'title': 'What is Waste Segregation?',
                    'title_bem': 'Ni Cani Kugawanya Ubwafya?',
                    'title_ny': 'Ndi Chiyani Kugawa Zinyalala?',
                    'content_type': 'video',
                    'content': 'Comprehensive introduction to waste segregation principles and benefits.',
                    'content_bem': 'Ukwingila ukwa bwino mu myeyo ya kugawanya ubwafya na kufwailisha kwayo.',
                    'content_ny': 'Chiyambi chokwanira cha mfundo za kugawa zinyalala ndi ubwino wake.',
                    'duration_minutes': 10,
                    'order': 1
                },
                {
                    'title': 'Benefits of Proper Segregation',
                    'title_bem': 'Kufwailisha kwa Kugawanya Ubwafya kwa Bwino',
                    'title_ny': 'Ubwino wa Kugawa Zinyalala Bwino',
                    'content_type': 'audio',
                    'content': 'Learn about environmental and economic benefits of waste segregation.',
                    'content_bem': 'Ukufunda pa kufwailisha kwa chialo na ca mali ca kugawanya ubwafya.',
                    'content_ny': 'Phunzirani za ubwino wa chilengedwe ndi wachuma wa kugawa zinyalala.',
                    'duration_minutes': 8,
                    'order': 2
                },
                {
                    'title': 'Basic Segregation Categories',
                    'title_bem': 'Imitundu ya Bukankala ya Kugawanya',
                    'title_ny': 'Magulu Oyambira a Kugawa',
                    'content_type': 'text',
                    'content': 'Detailed guide on the four main categories: Organic, Recyclable, Hazardous, and General waste.',
                    'content_bem': 'Ukutontonkanya ukwa talika pa mitundu iine iyakufunikisha: Ubwafya bwa fyakufyala, bwa ukusebenzeshafye, bwa bwafya, na bwa conse.',
                    'content_ny': 'Chitsogozo chatsatanetsatane cha magulu anayi aakulu: Zinyalala za chilengedwe, zobwerezeretseka, zoopsa, ndi za wamba.',
                    'duration_minutes': 12,
                    'order': 3
                },
                {
                    'title': 'Knowledge Check',
                    'title_bem': 'Ukuipima Imyeyo',
                    'title_ny': 'Kuyesa Chidziwitso',
                    'content_type': 'quiz',
                    'duration_minutes': 5,
                    'order': 4
                }
            ]
            create_lessons_for_module(module, lessons_data)
            
        elif "Types of Waste Materials" in module.title:
            lessons_data = [
                {
                    'title': 'Organic Waste Identification',
                    'title_bem': 'Ukumanya Ubwafya bwa Fyakufyala',
                    'title_ny': 'Kuzindikira Zinyalala za Chilengedwe',
                    'content_type': 'video',
                    'content': 'Learn to identify biodegradable organic waste materials.',
                    'content_bem': 'Ukufunda ukumanya ubwafya bwa fyakufyala ubwakuola.',
                    'content_ny': 'Phunzirani kuzindikira zinyalala za chilengedwe zomwe zimavunda.',
                    'duration_minutes': 12,
                    'order': 1
                },
                {
                    'title': 'Recyclable Materials Guide',
                    'title_bem': 'Ukutontonkanya Fintu Ifya Ukusebenzeshafye',
                    'title_ny': 'Chitsogozo cha Zinthu Zobwerezeretseka',
                    'content_type': 'text',
                    'content': 'Comprehensive guide to identifying recyclable plastics, paper, metal, and glass.',
                    'content_bem': 'Ukutontonkanya ukwa bwino ukwa kumanya ama-plastic, amapepa, ichuma, na glass ifya ukusebenzeshafye.',
                    'content_ny': 'Chitsogozo chokwanira cha kuzindikira pulasitiki, mapepala, zitsulo, ndi galasi zobwerezeretseka.',
                    'duration_minutes': 15,
                    'order': 2
                },
                {
                    'title': 'Hazardous Waste Recognition',
                    'title_bem': 'Ukumanya Ubwafya bwa Bwafya',
                    'title_ny': 'Kuzindikira Zinyalala Zoopsa',
                    'content_type': 'audio',
                    'content': 'Safety guidelines for identifying and handling hazardous materials.',
                    'content_bem': 'Imilimo ya chiteko ya kumanya no kutontonkanya ubwafya bwa bwafya.',
                    'content_ny': 'Malangizo achitetezo a kuzindikira ndi kugwira zinyalala zoopsa.',
                    'duration_minutes': 10,
                    'order': 3
                },
                {
                    'title': 'Material Classification Quiz',
                    'title_bem': 'Quiz ya Kugawanya Fintu',
                    'title_ny': 'Quiz ya Kugawa Zinthu',
                    'content_type': 'quiz',
                    'duration_minutes': 8,
                    'order': 4
                }
            ]
            create_lessons_for_module(module, lessons_data)

def main():
    """Main function to populate all learning content."""
    print("Starting to populate EcoLearn with comprehensive learning modules...")
    
    # Create categories
    print("\n1. Creating categories...")
    categories = create_categories()
    
    # Create modules for each category
    print("\n2. Creating modules...")
    waste_seg_modules = create_waste_segregation_modules(categories[0])
    recycling_modules = create_recycling_modules(categories[1])
    disposal_modules = create_sustainable_disposal_modules(categories[2])
    community_modules = create_community_action_modules(categories[3])
    
    # Create comprehensive lessons
    print("\n3. Creating lessons and quizzes...")
    populate_comprehensive_lessons()
    
    print("\n✅ Successfully populated EcoLearn with comprehensive learning modules!")
    print(f"Created {Category.objects.count()} categories")
    print(f"Created {Module.objects.count()} modules")
    print(f"Created {Lesson.objects.count()} lessons")
    print(f"Created {Quiz.objects.count()} quizzes")
    print(f"Created {Question.objects.count()} questions")

if __name__ == "__main__":
    main()
