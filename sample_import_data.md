# Sample Import Data for Demo

## How to Create Sample Files

### Option 1: Export First, Then Modify
1. Go to admin panel
2. Click "Export" on any model
3. Download as Excel
4. Modify the data
5. Re-import

### Option 2: Create from Scratch

## Sample 1: Modules Import (demo_modules.csv)

Create a CSV file with this content:

```csv
title,slug,category,difficulty,duration_minutes,points_reward,is_published,description
"Plastic Recycling Basics","plastic-recycling-basics","Recycling","beginner",30,50,TRUE,"Learn the fundamentals of plastic recycling in Zambia"
"E-Waste Management","e-waste-management","E-Waste","intermediate",45,75,TRUE,"Proper handling and disposal of electronic waste"
"Community Cleanup Leadership","community-cleanup-leadership","Community","advanced",60,100,TRUE,"Lead effective community cleanup initiatives"
"Composting at Home","composting-at-home","Organic Waste","beginner",25,40,TRUE,"Turn kitchen waste into valuable compost"
"Hazardous Waste Safety","hazardous-waste-safety","Hazardous Waste","advanced",50,90,TRUE,"Safe handling of hazardous materials"
```

## Sample 2: Challenges Import (demo_challenges.csv)

```csv
title,challenge_type,points_reward,start_date,end_date,target_metric,target_value,is_active,description
"December Cleanup Challenge","community",200,2024-12-01,2024-12-31,"reports_submitted",100,TRUE,"Join our community-wide cleanup initiative"
"Recycling Champion","individual",150,2024-12-01,2024-12-31,"modules_completed",10,TRUE,"Complete 10 recycling modules"
"E-Waste Warrior","individual",180,2024-12-01,2024-12-31,"modules_completed",5,TRUE,"Master e-waste management"
"District Leader","district",300,2024-12-01,2024-12-31,"reports_submitted",200,TRUE,"Lead your district in waste reporting"
```

## Sample 3: Events Import (demo_events.csv)

```csv
title,event_type,location,start_date,end_date,max_participants,is_active,description
"Lusaka Central Cleanup","cleanup","Lusaka City Market",2024-12-15 09:00:00,2024-12-15 13:00:00,50,TRUE,"Community cleanup at City Market"
"Recycling Workshop","workshop","Civic Centre, Lusaka",2024-12-20 14:00:00,2024-12-20 17:00:00,30,TRUE,"Learn recycling techniques"
"Eco Competition Finals","competition","Olympic Youth Centre",2024-12-28 10:00:00,2024-12-28 16:00:00,100,TRUE,"Annual eco competition"
```

## Sample 4: Badges Import (demo_badges.csv)

```csv
name,code,description,points_required,is_active
"Eco Beginner","eco-beginner","Complete your first module",0,TRUE
"Recycling Expert","recycling-expert","Complete 5 recycling modules",250,TRUE
"Community Leader","community-leader","Organize 3 community events",500,TRUE
"Waste Warrior","waste-warrior","Submit 20 waste reports",400,TRUE
"Green Champion","green-champion","Earn 1000 points",1000,TRUE
```

## Sample 5: Rewards Import (demo_rewards.csv)

```csv
name,reward_type,points_cost,stock_quantity,is_available,description
"K20 Airtime Voucher","airtime",200,50,TRUE,"MTN/Airtel airtime voucher"
"Eco Certificate","certificate",100,999,TRUE,"Official EcoLearn certificate"
"Recycling Champion Badge","badge",150,999,TRUE,"Digital badge for your profile"
"Eco T-Shirt","merchandise",500,20,TRUE,"Official EcoLearn t-shirt"
"K50 Airtime Voucher","airtime",450,30,TRUE,"Premium airtime voucher"
```

## Quick Import Instructions

### For CSV Files:
1. Copy the content above
2. Save as `.csv` file (e.g., `demo_modules.csv`)
3. Go to admin panel
4. Click "Import"
5. Upload the CSV file
6. Preview and confirm

### For Excel Files:
1. Open Excel
2. Copy the data (including headers)
3. Paste into Excel
4. Save as `.xlsx`
5. Import via admin panel

## Important Notes

### Field Requirements:
- **Required fields**: title, name (depending on model)
- **Date format**: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
- **Boolean values**: TRUE/FALSE or 1/0
- **Foreign keys**: Use the related field name (e.g., category name)

### Common Issues:
- ❌ Missing required fields → Add them
- ❌ Invalid date format → Use YYYY-MM-DD
- ❌ Non-existent foreign key → Create the related object first
- ❌ Duplicate slugs → Make slugs unique

### Pro Tips:
- ✅ Export existing data first to see the correct format
- ✅ Start with small batches (5-10 records)
- ✅ Use the preview feature to catch errors
- ✅ Keep a backup of your data

## Demo Script

1. **Show empty admin page**: "We need to add 50 modules..."
2. **Click Import**: "Instead of manual entry..."
3. **Upload CSV**: "We can import from Excel or CSV..."
4. **Show preview**: "The system validates everything first..."
5. **Confirm**: "And boom! 50 modules added in 10 seconds!"

---

**Time to create samples**: 5 minutes
**Time to import**: 10 seconds per file
**Wow factor**: 🚀🚀🚀
